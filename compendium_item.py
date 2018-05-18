class CompendiumItem:
    def __init__(self, title, body):
        self.body = body
        # hybrid key of the compendium_id/user_id
        self.id = ""
        # Order/?
        self.index = 0
        self.locale = "en_US"
        # Drop actions
        self.metadata = {}
        # parent category ID
        self.parent_category = ""
        # The title of the entry
        self.title = title
        # How to parse
        self.type = "markdown"

    def to_obj(self):
        return {
            "body": self.body,
            "id": self.id,
            "index": self.index,
            "locale": self.locale,
            "metadata": self.metadata,
            "parent_category": self.parent_category,
            "title": self.title,
            "type": self.type
        }
