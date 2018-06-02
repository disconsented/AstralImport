import click
import os
import json
import io
from collections import defaultdict
import importlib.util
import pyrebase
from plugins import Plugin
from tqdm import tqdm
import pprint


@click.command()
@click.argument('input_file')
@click.argument('password')
@click.argument('email')
@click.argument('api_key')
@click.argument('compendium_name')
@click.option('--upload', default=True, type=bool)
def main(input_file, password, email, api_key, compendium_name, upload):
    pretty_print = pprint.PrettyPrinter(indent=4)
    plugins = {}
    # load plugins
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(base_dir + "/parsers/"):
        full_file = base_dir + "/parsers/" + file
        if os.path.isfile(full_file) and file.endswith(".py"):
            load_plugin(full_file, plugins)

    config = {
        "apiKey": api_key,
        "authDomain": "power-vtt.firebaseapp.com",
        "databaseURL": "https://power-vtt.firebaseio.com/",
        "storageBucket": "gs://power-vtt.appspot.com"
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password(email, password)
    local_id = user["localId"]
    token = user["idToken"]
    print("User id : " + local_id)

    compendium_id = None
    compendiums = db.child("/compendiums").get()
    exsisting_items = defaultdict(list)
    categories = {}
    print("Found compendiums:      (looking for {})".format(compendium_name))
    for key, value in compendiums.val()[local_id].items():
        print(value['name'] + ":")
        if value['name'] == compendium_name:
            compendium_id = key
        if 'categories' in value:  # If this compendium has categories
            for cat_key, cat_value in value['categories'].items():
                categories[cat_value['name']] = cat_key
                print("    " + cat_key + " : " + cat_value['name'])
        else:
            print("    None")
    if compendium_id is None:
        print("Unable to find compendium")
        return
    else:
        print("Found compendium {} with id {}".format(compendium_name, compendium_id))

    # db.child("/compendium_items").child("-LC7oNvbN00kaaXOOxFs").update({"body": "Python success"})
    joined_key = "{}/{}".format(local_id, compendium_id)
    response = db.child("/compendium_items").get()
    for item in response.each():
        try:
            if item.val()['id'] in joined_key:
                exsisting_items.__getitem__(item.val()["parent_category"]).append(item)
                # print(item.key() + " | " + item.val()['id'] + " | " + item.val()["parent_category"])
        except KeyError:
            print("Item without a key detected")
            pretty_print.pprint(item.val())
# Find files
    files = []
    if os.path.isdir(input_file):
        files.extend(traverse_dir(input_file))
    else:
        files.append(input_file)

    for file in files:
        data = json.load(io.open(file, 'r', encoding='utf-8-sig'))
        for entity in data.items():
            parser = plugins.get(entity[0], None)
            if None is not parser:
                tqdm.write("Parsing: " + entity[0])
                # file_object = open("test.md", "w")
                # file_object.writelines(parser.serialise_common_mark(entity[1]))

                # No category
                parsed = parser.parse(entity[1])
                if upload is False:
                    continue
                if not categories.get(parser.category_name, None):
                    # Create new category, wont be any new children
                    new_category = db.child("/compendiums").child(local_id).child(compendium_id).child("categories").\
                        push({"index": 0, "name": parser.category_name}, token)['name']
                    tqdm.write("Added new category: " + new_category)
                    for entry in tqdm(parsed, desc="New Items"):
                        entry.id = joined_key
                        entry.parent_category = new_category
                        new_item = db.child("/compendium_items").push(entry.to_obj(), token)['name']
                        db.child("/compendium_items").child(new_item).update(
                            {"metadata":
                             {"drop":
                              {"game":
                               [{"handout":
                                {"compendium_item": new_item},
                                 "type": "handout"}]}}}, token)

                else:  # Existing category
                    category_id = categories[parser.category_name]
                    category_items = exsisting_items[category_id]
                    for item in tqdm(parsed, desc="Updating items"):
                        success = False
                        for existing_item in category_items:
                            if item.title == existing_item.val()["title"]:
                                item.metadata = {"drop": {"game": [{"handout": {"compendium_item": existing_item.key()},
                                                                    "type": "handout"}]}}
                                item.id = existing_item.val()["id"]
                                item.id = joined_key
                                item.parent_category = existing_item.val()["parent_category"]
                                db.child("compendium_items").child(existing_item.key()).update(item.to_obj(), token)
                                success = True
                        if not success:
                            item.id = joined_key
                            item.parent_category = category_id
                            new_item = db.child("/compendium_items").push(item.to_obj(), token)['name']
                            db.child("/compendium_items").child(new_item).update(
                                {"metadata":
                                    {"drop":
                                        {"game":
                                            [{"handout":
                                                {"compendium_item": new_item},
                                              "type": "handout"}]}}}, token)

                    # find existing by name
                    # update
            else:
                continue
                # print("Unsupported data: " + entity[0])


def traverse_dir(directory):
    """Returns all files within a directory and will traverse down infinitely"""
    files = []
    for file in os.listdir(directory):
        full_path = directory + file
        if os.path.isdir(full_path):
            files.extend(traverse_dir(full_path + "/"))
        else:
            files.append(full_path)
    return files


def load_plugin(path, plugins):

    file_name = os.path.basename(path)
    title = os.path.splitext(file_name)[0]
    module_name = "parsers.{}".format(title)
    plugin_module = importlib.import_module(module_name)
    module = importlib.import_module(module_name)
    class_ = get_subclass(module, Plugin)()
    plugins[class_.name] = class_

    # print(getattr(plugin_module, "ItemParser"))
    print("Loaded plugin: {}".format(module_name))


def get_subclass(module, base_class):
    for name in dir(module):
        obj = getattr(module, name)
        try:
            if issubclass(obj, base_class):
                return obj
        except TypeError:  # If 'obj' is not a class
            pass
    return None


main()
print("Done")
