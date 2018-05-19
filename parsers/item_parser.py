from plugins import Plugin
from compendium_item import CompendiumItem


class ItemParser(Plugin):

    def __init__(self):
        super().__init__("item", "Items")

    def parse(self, data):
        output = []

        for item in data:
            lines = ""
            # print("Parsing item with name: {}".format(item["name"]))

            # Parse the byline first to figure out if we need to skip

            byline = "*"
            if item.get("wondrous", None) is not None:
                byline += "Wondrous-item, "

            if item.get("weaponCategory", None) is not None:
                byline += item["weaponCategory"] + " "

            if item.get("type", None) is not None:
                item_type = item["type"]
                byline += self.get_property(item_type, False)

            if item.get("property", None) is not None:
                for prop in item.get("property"):
                    byline += ", {}".format(self.get_property(prop, True))

            if item.get("armor", None) is not None:
                item_type = item["type"]
                # Armour
                byline += "AC:{}".format(item["ac"])

            if item.get("rarity", None) is not None:
                rarity = item["rarity"]
                if "None" not in rarity:
                    byline += " {}".format(rarity)

            if item.get("reqAttune", None) is not None:
                attunement = item["reqAttune"]
                # Armour
                byline += ", Requires Attunement ({})".format(attunement.lower())

            if item.get("value", None) is not None:
                byline += item["value"]

            if item.get("weight", None) is not None:
                byline += " {} lbs".format(item["weight"])

            lines += ("# {}".format(item["name"]))
            lines += self.new_line
            lines += byline+"*"
            lines += self.double_line
            # Entries
            entries = item.get("entries", None)
            if entries is not None:
                lines = self.handle_entries(entries, lines)
            # Additional Entries
            adt_entries = item.get("additionalEntries", None)
            if adt_entries is not None:
                lines = self.handle_entries(adt_entries, lines)
            lines += self.new_line

            if item.get("source", None) is not None:
                source = item["source"]
                page = item["page"]
                lines += "{}*{} page: {}*".format(self.double_line, source, page)

            if item.get("additionalSources", None) is not None:
                for source in item.get("additionalSources"):
                    lines += "*, {} page:{}*".format(source['source'], source['page'])

            output.append(CompendiumItem(item['name'], lines))
        return output

    def handle_entries(self, entries, lines):
        for line in entries:
            # Handle tables
            if type(line) == dict:
                line_type = line["type"]
                if line_type == "list":
                    for list_item in line["items"]:
                        lines += "- {}{}".format(list_item, self.new_line)
                elif line_type == "table":
                    # Caption
                    if not self.format_if_not_none("{}{}{}", lines, [self.new_line, line.get("caption", None),
                                                                     self.new_line]):
                        lines += self.new_line
                    # lines += .format(self.new_line, line["caption"], self.new_line))
                    lines += self.new_line
                    lines += self.new_line
                    # Spacing
                    lines += "|{}|{}".format('|'.join(line["colLabels"]), self.new_line)
                    # Rows
                    lines += "|{}|{}".format("|".join((['-'] * len(line["colLabels"]))), self.new_line)
                    for row in line["rows"]:
                        lines += "|{}|{}".format('|'.join(row), self.new_line)
                elif line_type == "entries":
                    # Super annoying special case, used for curses
                    lines += "{}{}**{}.** ".format(self.new_line, self.new_line, line["name"])
                    for entry in line["entries"]:
                        if type(entry) == str:
                            lines += entry
                        else:
                            self.handle_entries(entry, lines)

            else:
                lines += line
        return lines
