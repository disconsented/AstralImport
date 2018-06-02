from plugins import Plugin
from compendium_item import CompendiumItem


class FeatParser(Plugin):

    def __init__(self):
        super().__init__("feat", "Feats")

    def parse(self, data):
        output = []

        for item in data:
            lines = ""
            lines += ("# {}".format(item["name"]))
            lines += self.double_line

            entries = item.get("prerequisite", None)
            if entries is not None:
                lines += "* Prerequisite: "
                for entry in entries:
                    for req, val in entry.items():
                        if req == "race":
                            races = []
                            for race in val:
                                if race.get("subrace", None) is not None:
                                    races.append("{} ({})".format(race["name"], race["subrace"]))
                                else:
                                    races.append(race["name"])
                            lines += str.join(" or ", races)

                        elif req == "proficiency":
                            proficiencies = []
                            for sub_dict in val:
                                for key, value in sub_dict.items():
                                    proficiencies.append("{} {}".format(key, value))
                            lines += str.join(" or ", proficiencies)

                        elif req == "ability":
                            abilities = []
                            for sub_dict in val:
                                for key, value in sub_dict.items():
                                    abilities.append("{} {}".format(self.get_ability(key), value))
                            lines += str.join(", ", abilities)
                            lines += " or greater "

                        elif req == "spellcasting":
                            lines += "Spellcasting"
                lines += " *"
                lines += self.new_line

            # ability
            entries = item.get("ability", None)
            if entries is not None:
                for entry_key, entry_val in entries.items():
                    scores = []
                    amount = 0
                    if entry_key == "choose":
                        for score in entry_val[0]["from"]:
                            scores.append(self.get_ability(score))
                        amount = entry_val[0]["amount"]
                    else:
                        scores.append(self.get_ability(entry_key))
                        amount = entry_val
                    lines += "Increase your {} score by {}, up to a maximum of 20.".format(str.join(" or ", scores),
                                                                                           amount)
                    lines += self.new_line

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
