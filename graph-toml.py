from collections import deque
from math import dist
import os
import toml
import json

print("Computing Routes")
SWITCH_DEBUFF = 250

def distance(n0,n1,n2):
    if not 'x' in data[n2] or not 'z' in data[n2]:
        return 0
    if not 'x' in data[n1] or not 'z' in data[n1]:
        return 0
        #p1 = [data[n0]['x'],data[n0]['z']]
    else:
        p1 = [data[n1]['x'],data[n1]['z']]
    p2 = [data[n2]['x'],data[n2]['z']]

    #print("DISTANCE",n0,n1,n2,dist(p1,p2))
    return dist(p1,p2)

# Calculate the shortest route between 2 points on a line, output direction and distance
def line_route(cur,prev,nex):
    s,e = 0,0
    cur_d = data[cur]
    for i in range(len(cur_d['links'])):
        l = cur_d['links'][i]
        if l == prev:
            s = i
        if l == nex:
            e = i
    ldir = 0 # 0 = dest_a ; 1 = dest_b
    dist = 0
    # Hacky solution for looping lines
    if 'loop' in cur_d and cur_d['loop'] == True:
        # Loop Dir A
        dist_a = 0
        i = s
        while (i != e):
            u = i-1
            if u < 0:
                u = len(cur_d['links'])-1
            dist_a += distance(None,cur_d['links'][i],cur_d['links'][u])
            i = u
        # Loop Dir B
        dist_b = 0
        i = s
        while (i != e):
            u = i+1
            if u >= len(cur_d['links']):
                u = 0
            dist_b += distance(None,cur_d['links'][i],cur_d['links'][u])
            i = u
        # Use the shortest loop direction
        dist = dist_a
        if dist_a > dist_b:
            dist = dist_b
            ldir = 1
    else:
        if s > e:
            hi,lo = s,e
        else:
            hi,lo = e,s
            ldir = 1
        for i in range(lo,hi):
            dist += distance(None,cur_d['links'][i],cur_d['links'][i+1])
    return ldir,dist
# Finds a path between 2 points
def pathfind(start,end):
    def get_links(n):
        if 'unsafe_links' in data[n] and path[n] in data[n]['unsafe_links']:
            return []
        elif n == start:
            return start_lis[n]
        else:
            return adjac_lis[n]
    
    open_list = set([start])
    closed_list = set([])
    path = {}
    dista = {}
    path[start] = start
    dista[start] = 0

    while len(open_list) > 0:
        cn = None
        # Heuristics to determine which node to check first
        for n in open_list:
            if cn == None:
                cn = n
            elif dista[n] + distance(path[n],n,end) < dista[cn] + distance(path[cn],cn,end):
                cn = n
        # -----
        open_list.remove(cn)
        closed_list.add(cn)
        if cn == end:
            reconst_path = []
            n = cn
            while n != start:
                reconst_path.append(n)
                n = path[n]
            reconst_path.append(start)
            reconst_path.reverse()
            return reconst_path
        # -----
        for link in get_links(cn):
            if link not in closed_list:
                path[link] = cn
                dista_line = 0
                if data[cn]['type'] == 'line':
                    ldir,dista_line = line_route(cn,path[cn],link)
                debuff = 0
                if data[cn]["type"] in ["junction","stopjunction","junctionstop","crossing"]:
                    debuff = SWITCH_DEBUFF
                dista[link] = dista[cn] + distance(path[cn],cn,link) + dista_line + debuff
                open_list.add(link)

    return None

# Returns the dest command needed to move between 2 points
def getdest(prev,cur,nex,final):
    cmd = []
    if 'link_dests' in data[cur] and nex in data[cur]['link_dests']:
        cmd.append(data[cur]['link_dests'][nex])
    if data[cur]['type'] == 'line':
        ldir,dist = line_route(cur,prev,nex)
        if ldir == 0:
            dest_a = None
            if 'dest_a' in data[cur]:
                dest_a = data[cur]['dest_a']
            if 'local_dests' in data[cur]:
                for local in data[cur]['local_dests']:
                  if prev in local['links'] and 'dest_a' in local:
                      dest_a = local['dest_a']
            if dest_a:
              cmd.append(dest_a)     
        else:
            dest_b = None
            if 'dest_b' in data[cur]:
                dest_b = data[cur]['dest_b']
            if 'local_dests' in data[cur]:
                for local in data[cur]['local_dests']:
                  if prev in local['links'] and 'dest_b' in local:
                      dest_b = local['dest_b']
            if dest_b:
              cmd.append(dest_b)
    if 'bad_links' in data[cur] and nex in data[cur]['bad_links']:
       cmd.append(data[cur]['bad_links'][nex])
    elif 'dest' in data[nex]:
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
    print(node)
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

###---------------------
### Write to file
###---------------------
computed = {}
computed['nodes'] = data
computed['dests'] = dests

with open('computed.json','w') as f:
    f.write(json.dumps(computed))
