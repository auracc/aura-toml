# AURA Toml

Research into code refactoring and storing AURA data in a Toml format, currently lacks some functionality. 

The AURA database is composed of different nodes, classified into points and lines, data in this repo is stored in .toml files, with each file corresponding to an individual node. Below is a description of all fields avaliable:

| Field                  | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| name                   | The name of the node, currently used by AURA website to select a station, can either be a string or an array of strings (useful for locations that commonly use abreviations of their names ie ['Mount Augusta','MtA']) |
| type="stop"            | A point that is incapable of routing the rider further, common type of stations |
| type="junction"        | A point that allows the player to route onto further nodes, typically a roundabout that takes the rider through multiple destination options. Interrupts travel if a command is not used |
| type="stopjunction"    | A stop that can become a junction by running an additional command |
| type="junctionstop"    | A junction that can become a stop by running an additional command |
| type="crossing"        | A non-junction switch that connects multiple lines or points. Does not interrupt travel if a command is not used |
| type="line"            | A line that connects multiple points together, with support for directional routing along its length |
| dest                   | The command used to enter the node                           |
| dest_junction          | The command used to enable junction functionality on the node (stopjunction) |
| dest_stop              | The command used to enable stop functionality on the node (junctionstop) |
| dest_a                 | The command used to route the rider towards the beggining of the line |
| dest_b                 | The command used to route the rider towards the end of the line |
| x,z                    | The x and z coordinates of the node, not used for lines      |
| links                  | An array of all the nodes connected to this                  |
| station (true/false)   | Wheter this is an intended start or end point for travel, default false |
| suggested (true/false) | Wheter a station should be visually shown in the AURA router station list and auto-fill fields (can still be routed to/from), default true |
| surface (true/false)   | Wheter a node is located on the surface, default false       |
| horse (true/false)     | Wheter a node can be accessed by horses, default false       |
| [link_dests]           | Any node specific commands required to access a node's links |
| [local_dests]          | Allows setting different directional routing commands for different stations |
| [bad_links]            | Any connection that uses a non-standard dest, will be used instead of the standard one |
| [unsafe_links]         | When arriving at a junction from this destination, the junction will not be capable of routing the rider further |

