import yaml
import csv
import os


def parse_file(filename, env):
    definitions_obj = yaml.load(open(filename, 'r'))
    if 'DOMAIN' in definitions_obj:
        if 'viewport_width' in definitions_obj['DOMAIN']:
            env.viewport_width = definitions_obj['DOMAIN']['viewport_width']
        if 'viewport_height' in definitions_obj['DOMAIN']:
            env.viewport_height = definitions_obj['DOMAIN']['viewport_height']
        if 'ppm' in definitions_obj['DOMAIN']:
            env.ppm = definitions_obj['DOMAIN']['ppm']
        if 'statistics' in definitions_obj['DOMAIN']:
            env.statistics = definitions_obj['DOMAIN']['statistics']
    if 'ENVIRONMENT' in definitions_obj and 'gravity' in definitions_obj['ENVIRONMENT']:
        env.gravity = definitions_obj['ENVIRONMENT']['gravity']
    if 'PARTS' in definitions_obj:
            for part in definitions_obj['PARTS']:
                env.partslist[part] = definitions_obj['PARTS'][part]
    if 'JOINTS' in definitions_obj:
        env.jointslist = definitions_obj['JOINTS']


def get_color(color_name):
    with open("%s/colors.csv" % os.path.dirname(__file__), 'r') as colors:
        r = csv.reader(colors)
        colors_list = []
        for row in r:
            colors_list.append(row)
    for name, full_name, hexa, r, g, b in colors_list:
        if color_name == name:
            color = ((int(r) / 256, int(g) / 256, int(b) / 256))
            return color
    return (0, 0, 0)
