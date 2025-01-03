import maven


class Graphql(maven.Maven):

    @property
    def name(self):
        return 'graphql-java-tools'

    @property
    def language(self):
        return 'kotlin', 'java'
