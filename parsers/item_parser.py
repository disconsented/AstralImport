from plugins import Plugin

class ItemParser(Plugin):

    def __init__(self):
        super().__init__("item")

    def serialise_tabletop_macro_language(self, data):
        pass

    def serialise_common_mark(self, data):
        lines = []
        for item in data:
            print("Parsing item with name: {}".format(item["name"]))

            # Parse the byline first to figure out if we need to skip

            byline = "*"
            if item.get("wondrous", None) is not None:
                byline += "Wondrous-item, "

            if item.get("armor", None) is not None:
                item_type = item["type"]
                # Armour
                byline += "Armour ({}), ".format(item_type)

            if item.get("type", None) is not None:
                item_type = item["type"]
                if "$" in item_type:
                    # byline += "*{}* ".format(item_type)
                    continue

            if item.get("rarity", None) is not None:
                rarity = item["rarity"]
                if "None" not in rarity:
                    byline += rarity

            if item.get("reqAttune", None) is not None:
                attunement = item["reqAttune"]
                # Armour
                byline += ", Requires Attunement ({})".format(attunement.lower())

            if item.get("value", None) is not None:
                byline += item["value"]

            lines.append("# {}".format(item["name"]))
            lines.append(self.new_line)
            lines.append(byline+"*")
            lines.append(self.new_line)
            # Entries
            entries = item.get("entries", None)
            if entries is not None:
                self.handle_entries(entries, lines)
            lines.append(self.new_line)
        return lines

    def handle_entries(self, entries, lines):
        for line in entries:
            # Handle tables
            if type(line) == dict:
                line_type = line["type"]
                if line_type == "list":
                    for list_item in line["items"]:
                        lines.append("- {}{}".format(list_item, self.new_line))
                elif line_type == "table":
                    # Caption
                    if not self.format_if_not_none("{}{}{}", lines, [self.new_line, line.get("caption", None),
                                                                     self.new_line]):
                        lines.append(self.new_line)
                    # lines.append(.format(self.new_line, line["caption"], self.new_line))
                    # Spacing
                    lines.append("|{}|{}".format('|'.join(line["colLabels"]), self.new_line))
                    # Rows
                    lines.append("|{}|{}".format("|".join((['-'] * len(line["colLabels"]))), self.new_line))
                    for row in line["rows"]:
                        lines.append("|{}|{}".format('|'.join(row), self.new_line))
                elif line_type == "entries":
                    # Super annoying special case, used for curses
                    lines.append("{}**{}.** ".format(self.new_line, line["name"]))
                    for entry in line["entries"]:
                        if type(entry) == str:
                            lines.append(entry)
                        else:
                            self.handle_entries(entry, lines)

            else:
                lines.append(line)

