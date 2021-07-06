#!/usr/bin/python3

# script adapted from KANI's ccmap script
# reads all .toml files (nodes) under ./data/
# and writes a CCMap layer JSON to file

import toml
import os
from sys import stderr
import time
import json
from math import sqrt
from os import environ

datadir = r'./data'

data = {}

def processFile(path, name):
    try:
        name = name.removesuffix('.toml')
        myData = toml.load(path)
        myData['id'] = name
        myData['filepath'] = path
        if 'links' not in myData:
            myData['links'] = []
        if 'BadLinks' not in myData:
            myData['BadLinks'] = {}
        if 'link_dests' not in myData:
            myData['link_dests'] = {}
        data[name] = myData
    except Error as e:
        print(f"Error while reading file {path}", file=stderr)
        raise e

for subdir, dirs, files in os.walk(datadir):
    for filename in files:
        filepath = subdir + os.sep + filename

        if filepath.endswith('.toml'):
            processFile(filepath, filename)

optional_fields = 'description x z dest dest_stop dest_junction dest_a dest_b station suggested surface horse'.split(' ')

def format_name(node):
    if not 'name' in node:
        return node['id']
    if type(node['name']) == list:
        return node['name'][0]
    return node['name']

def format_node(node):
    o = {}
    o['id'] = 'ccmap:aura/node/' + node['id']
    o['name'] = format_name(node) + ' (AURA)'
    o['type'] = node['type']
    o['x'] = int(node['x'])
    o['z'] = int(node['z'])
    if 'y' in node:
        o['y'] = int(node['y'])
    for key in optional_fields:
        if key in node:
            o[key] = node[key]

    bad_links = ""
    for canon, bad in node['BadLinks'].items():
        bad_links += f"{canon}: {bad}, "
    bad_links.rstrip(", ")
    if bad_links != "":
        o['BadLinks'] = bad_links
    
    link_dests = ""
    for link,dest in node['link_dests'].items():
        link_dests += f"{link}: {dest}, "
    link_dests.rstrip(", ")
    if link_dests != "":
        o['LinkDests'] = link_dests

    return o

def format_link(node, neighbor):
    n_from, n_to = sorted((node, neighbor),
        key = lambda node: node['id'])
    from_name, to_name = n_from['id'], n_to['id']
    xa, xb = int(n_from['x']), int(n_to['x'])
    za, zb = int(n_from['z']), int(n_to['z'])
    o = {}
    o['type'] = 'link'
    o['id'] = f'ccmap:aura/link/{from_name}/{to_name}'
    o['name'] = f'{format_name(node)} - {format_name(neighbor)} (AURA)'
    o['line'] = [[[ xa, za ], [ xb, zb ]]]
    o['distance'] = int(sqrt((xa-xb)**2 + (za-zb)**2))
    return o

def format_line(node):
    o = {}
    o['id'] = 'ccmap:aura/line/' + node['id']
    o['name'] = format_name(node) + ' (AURA)'
    o['type'] = node['type']
    line = []
    distance = 0
    for c_node_id in node['links']:
        c_node = data[c_node_id]
        line.append([int(c_node['x']),int(c_node['z'])])
        if len(line) >= 2:
            xa,xb = int(line[-2][0]), int(line[-1][0])
            za,zb = int(line[-2][1]), int(line[-1][1])
            distance += int(sqrt((xa-xb)**2 + (za-zb)**2))
    o['line'] = [line]
    o['distance'] = distance
    for key in optional_fields:
        if key in node:
            o[key] = node[key]
    return o

nodes = []
lines = []
links = {}

for node in data.values():
    if node['type'] != 'line':
        nodes.append(format_node(node))
        for neighbor_name in node['links']:
            if neighbor_name == node['id']: continue
            link_id = tuple(sorted((neighbor_name, node['id'])))
            if link_id in links: continue
            neighbor = data[neighbor_name]
            if neighbor['type'] != 'line':
                links[link_id] = format_link(node, neighbor)
    else:
        lines.append(format_line(node))

presentations = [
    {
        "name": "Rails and Stops (AURA)",
        "style_base": {
            "color": "#0077ff",
        },
        "zoom_styles": {
            "-6": { "name": None },
            "-2": { "name": "$name" },
        },
    },
]

if 'LAST_UPDATE' in environ:
    print("Using LAST_UPDATE env variable for time", file=stderr)
else:
    print("Using system time", file=stderr)

collection = {
    "name": "Rails",
    "info": {
        "version": "3.0.0-beta3",
        "last_update": environ.get('LAST_UPDATE') or int(time.time()),
    },
    "presentations": presentations,
    "features":
        list(sorted(nodes,
            key = lambda node: node['id']))
        + list(sorted(lines,
            key = lambda line: line['id'])) 
        + list(sorted(links.values(),
            key = lambda link: link['id'])),
}

collection_string = json.dumps(collection, indent = None, separators = (',', ':'), sort_keys = True)
# apply line breaks for readability and nice diffs
collection_string = collection_string.replace("},{", "},\n{")
print(collection_string)

with open('ccmap.json','w') as f:
    f.write(collection_string)