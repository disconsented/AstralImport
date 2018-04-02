import click
import os
import json
import io
import importlib.util

plugins = {}


@click.command()
@click.argument('input_file')
def main(input_file):
    # load plugins
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(base_dir + "/parsers/"):
        if os.path.isfile(base_dir + "/parsers/" + file):
            load_plugin(base_dir + "/parsers/" + file)

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
                print("Parsing: " + entity[0])
                file_object = open("test.md", "w")
                file_object.writelines(parser.serialise_common_mark(entity[1]))
                parser.serialise_tabletop_macro_language(entity[1])
            else:
                print("Unsupported data: " + entity[0])


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


def load_plugin(path):
    file_name = os.path.basename(path)
    title = os.path.splitext(file_name)[0]
    module_name = "parsers.{}".format(title)
    plugin_module = importlib.import_module(module_name)
    attributes = dir(plugin_module)
    for attr in attributes:
        # Ignore anything that inst a plugin
        if attr is not "Plugin" and "__" not in attr:
            plugin = getattr(plugin_module, attr)()
            plugins[plugin.name] = plugin
            print("Loaded plugin: {}".format(plugin.name))


main()
print("Done")
