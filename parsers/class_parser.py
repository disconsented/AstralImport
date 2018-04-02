from plugins import Plugin


class ClassParser(Plugin):

    def __init__(self):
        super().__init__("class")

    def serialise_tabletop_macro_language(self, data):
        pass

    def serialise_common_mark(self, data):
        return "Class Parser!"
