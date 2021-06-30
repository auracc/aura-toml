# AURA data repo

`python3 debugger.py --help`

`python3 debugger.py --listpoints`

`python3 debugger.py --from <> --to <>`

| Field                  | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| name                   | The name of the node, currently used by AURA website to select a station, can either be a string or an array of strings (useful for locations that commonly use abreviations of their names) |
| type="stop"            | A point that is incapable of routing the rider further, common type of stations |
| type="junction"        | A point that allows the player to route onto further nodes, typically a roundabout that takes the rider through multiple destination options |
| type="stopjunction"    | A stop that can become a junction by running an additional command |
| type="junctionstop"    | A junction that can become a stop by running an additional command |
| type="crossing"        | A non-junction switch that connects multiple lines or points |
| type="line"            | A line that connects multiple points together, with support for direction routing along it |
| dest                   | The command used to enter this node                          |
| dest_junction          | The command used to enable junction functionality (stopjunction) |
| dest_stop              | The command used to enable stop functionality (junctionstop) |
| dest_a                 | The command used to route the rider towards the beggining of the line |
| dest_b                 | The command used to route the rider towards the end of the line |
| x,z                    | The x and z coordinates of the point                         |
| links                  | An array of all nodes connected to this                      |
| station (true/false)   | Wheter this is an intended start or end point for travel, default false |
| suggested (true/false) | Wheter a station should be visually shown in the AURA router station list and auto-fill fields (can still be routed to/from), default true |
| surface (true/false)   | Wheter a node is located on the surface, default false       |
| horse (true/false)     | Wheter a node can be accessed by horses, default false       |
| [link_dests]           | Collection of any node specific commands required to access a node's neighbours |

