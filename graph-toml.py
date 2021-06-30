from collections import deque
from math import dist
import os
import toml
import json

print("Computing Routes")

def distance(n0,n1,n2):
    if not 'x' in data[n2] or not 'z' in data[n2]:
        return 0
    if not 'x' in data[n1] or not 'z' in data[n1]:
        p1 = [data[n0]['x'],data[n0]['z']]
    else:
        p1 = [data[n1]['x'],data[n1]['z']]
    p2 = [data[n2]['x'],data[n2]['z']]

    return dist(p1,p2)

# Finds a path between 2 points
def pathfind(start,end):
    def get_links(n):
        if n == start:
            return start_lis[n]
        else:
            return adjac_lis[n]
    
    open_list = set([start])
    closed_list = set([])
    path = {}
    path[start] = start
    while len(open_list) > 0:
        cur_node = None

        for n in open_list:
            if cur_node == None:
                cur_node = n
            elif distance(path[n],n,end) < distance(path[cur_node],cur_node,end):
                cur_node = n
            
        open_list.remove(cur_node)
        closed_list.add(cur_node)
        if cur_node == end:
            reconst_path = []
            n = cur_node
            while n != start:
                reconst_path.append(n)
                n = path[n]

            reconst_path.append(start)
            
            reconst_path.reverse()

            return reconst_path
        for link in get_links(cur_node):
            if link not in closed_list:
                path[link] = cur_node
                open_list.add(link)

    return None

# Returns the dest command needed to move between 2 points
def getdest(prev,cur,nex,final):
    cmd = []
    if 'link_dests' in data[cur] and nex in data[cur]['link_dests']:
        cmd.append(data[cur]['link_dests'][nex])
    if data[cur]['type'] == 'line':
        s,e = 0,0
        for i in range(len(data[cur]['links'])):
            l = data[cur]['links'][i]
            if l == prev:
                s = i
            if l == nex:
                e = i
        if s > e:
            cmd.append(data[cur]['dest_a'])
        else:
            cmd.append(data[cur]['dest_b'])
    if 'dest' in data[nex]:
        cmd.append(data[nex]['dest'])
    if final:
        if data[nex]['type'] == 'junctionstop':
            cmd.append(data[nex]['dest_stop'])
    elif data[nex]['type'] == 'stopjunction':
        cmd.append(data[nex]['dest_junction'])

    return cmd

###---------------------
### Load the toml data files
###---------------------
data = {}
for root, dirs, files in os.walk(r'./data'):
    print(root,dirs,files)
    for filename in files:
        if filename.endswith('.toml'):
            with open(os.path.join(root, filename)) as f:
                data[filename[:-5]] = toml.loads(f.read())

###---------------------
### Generate the node lists
###---------------------
start_lis = {}
adjac_lis = {}
for node in data:
    #print(node)
    start_lis[node] = data[node]['links']
    if data[node]['type'] == 'stop':
        adjac_lis[node] = []
    else:
        adjac_lis[node] = data[node]['links']

###---------------------
### Compute all routes
###---------------------
dests = {}
for s in data:
    for e in data:
        if s != e and "station" in data[s] and "station" in data[e] and data[s]["station"] and data[e]["station"]:
            cmd = []
            path = pathfind(s,e)
            for i in range(len(path)-1):
                prev = None
                if i > 0:
                    prev = path[i-1]
                cmd.extend(getdest(prev,path[i],path[i+1],i==len(path)-2))
            print(path,cmd)
            dests['{} - {}'.format(s,e)] = '/dest {}'.format(" ".join(cmd))

computed = {}
computed['nodes'] = data
computed['dests'] = dests

with open('computed.json','w') as f:
    f.write(json.dumps(computed))