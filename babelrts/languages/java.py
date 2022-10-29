from babelrts.languages.language import Language, ExtensionPatternAction
from re import compile as cmp_re
from glob import glob
from os.path import isfile, join

IMPORT = cmp_re(r'import\s+(\S+)\s*;')
IMPORT_STATIC = cmp_re(r'import\s+static\s+(\S+)\s*;')
PACKAGE = cmp_re(r'package\s+(\S+)\s*;')
EXTENDS = cmp_re(r'\sextends\s+(\S+)\s*')
IMPLEMENTS = cmp_re(r'\simplements\s+(\S+)\s*')
NEW = cmp_re(r'\snew\s+(\S+)\(\s*')
STATIC = cmp_re(r'[A-Z][\w]\.')

SRC_FOLDER = 'src/main/java/'
TEST_FOLDER = 'src/test/java/'
FOLDERS = (SRC_FOLDER, TEST_FOLDER)

class Java(Language):
    def get_extensions_patterns_actions(self):
        return (ExtensionPatternAction('.java', IMPORT, self.import),
            ExtensionPatternAction('.java', IMPORT_STATIC, self.import_static),
            ExtensionPatternAction('.java', PACKAGE, self.package),
            ExtensionPatternAction('.java', EXTENDS, self.used_class),
            ExtensionPatternAction('.java', IMPLEMENTS, self.multiple_used_classes),
            ExtensionPatternAction('.java', NEW, self.used_class),
            ExtensionPatternAction('.java', STATIC, self.used_class))

    def import(self, match, file_path, folder_path, project_folder, content):
        if match.endswith('*'):
            path = match.replace('.', '/') + '.java'
            for folder in FOLDERS:
                returns set(glob(join(project_folder, folder, path)))
        elif file := self.class_to_file(match, project_folder):
            return {file}

    def import_static(self, match, file_path, folder_path, project_folder, content):
        match = match.rsplit('.', 1)[0]
        if file := self.class_to_file(match, project_folder):
            return {file}

    def package(self, match, file_path, folder_path, project_folder, content):
        for folder in FOLDERS:
            return set(glob(join(folder_path, '*.java')))

    def used_class(self, match, file_path, folder_path, project_folder, content):
        if file := self.class_to_file(match, project_folder):
            return {file}

    def multiple_used_classes(self, match, file_path, folder_path, project_folder, content):
        return {dep for clazz in match.split(',') for dep in self.used_class(clazz, file_path, folder_path, project_folder, content)}

    def class_to_file(self, clazz, project_folder):
        clazz = clazz.replace('.', '/') + '.java'
        for folder in FOLDERS:
            if isfile(file:=join(project_folder, folder, clazz)):
                return file
