class Plugin:

    def __init__(self, name):
        self.name = name
        self.new_line = "\r"

    def serialise_common_mark(self, data):
        raise NotImplementedError

    def serialise_tabletop_macro_language(self, data):
        raise NotImplementedError

    @staticmethod
    def format_if_not_none(string, lines, attrs):
        if None not in attrs:
            lines.append(string.format(*attrs))
            return True
        return False

