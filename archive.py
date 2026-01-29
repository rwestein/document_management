import os
import pathlib
import re
import shutil


class DocumentArchiver:
    CLOUD_DIRECTORY = ''
    INBOX_DIRECTORY = CLOUD_DIRECTORY+'/Inbox'
    DOC_DIRECTORY = CLOUD_DIRECTORY+'/Documents'
    verbose = True
    actions = []
    files = []
    existing_files = []

    def __init__(self, cloud_dir=pathlib.Path.home(), verbose=True):
        self.CLOUD_DIRECTORY = str(cloud_dir)
        self.INBOX_DIRECTORY = self.CLOUD_DIRECTORY + '/Inbox'
        self.DOC_DIRECTORY = self.CLOUD_DIRECTORY + '/Documents'
        self.verbose = verbose
        self.actions = []
        self.files = []
        self.existing_files = []

    def list(self):
        try:
            for file_ in os.listdir(self.INBOX_DIRECTORY):
                if not file_.startswith('.'):
                    self.files.append(file_)
        except FileNotFoundError:
            # Ignore if the inbox dir doesn't exist, just return the already known files for testing purposes
            pass
        return self.files

    @staticmethod
    def determine_year(doc):
        match = re.search('^.*_([12][0-9][0-9][0-9])[01][0-9][0123][0-9][a-z]?\.(pdf|PDF)', doc)
        if match is not None:
            return match.group(1)
        match = re.search('^([12][0-9][0-9][0-9])[01][0-9][0123][0-9]_.*\.pdf', doc)
        if match is not None:
            return match.group(1)

    def determine_new_name(self, old_name):
        match = re.search('^.*_([12][0-9][0-9][0-9])[01][0-9][0123][0-9][a-z]?\.(pdf|PDF)', old_name)
        if match is not None:
            return old_name
        match = re.search('^(.*)_([12][0-9][0-9][0-9][01][0-9][0123][0-9])_([0-9]+)\.pdf', old_name)
        if match is not None:
            return match.group(1) + '_' + match.group(2) + chr(int(match.group(3))+97) + '.pdf'
        match = re.search('^([12][0-9][0-9][0-9][01][0-9][0123][0-9])_(.*)\.pdf', old_name)
        if match is not None:
            return match.group(2) + '_' + match.group(1) + '.pdf'
        return old_name

    def determine_next_name(self, old_name):
        match = re.search('^(.*_[12][0-9][0-9][0-9][01][0-9][0123][0-9])([a-z]?)\.(pdf|PDF)$', old_name)
        if match is not None:
            if match.group(2):
                next = chr(ord(match.group(2))+1)
            else:
                next = 'b'
            return match.group(1) + next + '.pdf'

    def determine_destination(self, doc):
        year = self.determine_year(doc)
        if year is None:
            return
        destination_dir = os.path.join(self.DOC_DIRECTORY, year)
        if not os.path.isdir(destination_dir):
            os.mkdir(destination_dir)
        return os.path.join(self.DOC_DIRECTORY, year, self.determine_new_name(doc))

    def log(self, text):
        if self.verbose:
            print(text)
        self.actions.append(text)

    def simulate(self, max=None):
        return self.move(max=max, simulate=True)

    def isfile(self, dest):
        if dest.replace(self.CLOUD_DIRECTORY, '...') in self.existing_files:
            return True
        return os.path.isfile(dest)

    def move(self, max=None, simulate=False):
        movements_done = 0
        for doc in self.list():
            if max is not None and movements_done >= max:
                break
            orig_doc = doc
            new_doc = self.determine_new_name(doc)
            dest = self.determine_destination(new_doc)
            if dest is None:
                self.log(f'Skipping "{orig_doc}", don\'t know where to store it')
            else:
                i = 0
                # rename until we found a unique new name
                while self.isfile(dest) and i<20:
                    new_doc = self.determine_next_name(new_doc)
                    dest = self.determine_destination(new_doc)
                    i+=1
                if self.isfile(dest):
                    self.log(f'Skipping "{orig_doc}", already exists on destination')
                else:
                    if not simulate:
                        shutil.move(self.INBOX_DIRECTORY+os.sep+orig_doc, dest)
                    self.log(f'Move "{orig_doc}" to "{dest.replace(self.CLOUD_DIRECTORY, "...")}"')
                    movements_done += 1
        return self.actions


if __name__ == '__main__':
    dropbox = pathlib.Path.home() / 'Dropbox'
    da = DocumentArchiver(dropbox)
    da.move()
