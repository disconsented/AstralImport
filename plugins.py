class Plugin:

    def __init__(self, name, category_name):
        ###
        #  plugin name
        self.name = name

        self.new_line = "\n"
        ###
        #  Name for categories in the database
        self.category_name = category_name

    def parse(self, data):
        raise NotImplementedError

    @staticmethod
    def format_if_not_none(string, lines, attrs):
        if None not in attrs:
            lines += string.format(*attrs)
            return True
        return False

