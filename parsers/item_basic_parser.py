from compendium_item import CompendiumItem
from parsers.item_parser import ItemParser


class BasicItemParser(ItemParser):

    def __init__(self):
        super().__init__()
        self.name = "basicitem"
        self.category_name = "Items"
