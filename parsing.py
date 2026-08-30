from hub import Hub

color_good = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'black', 'white', 'cyan', 'brown', 'lime', 'magenta', 'gold', 'maroon', 'darkred', 'violet', 'crimson', 'rainbow']

def split_check_format(hub: str, separateur: str) -> list:
    new_tab = []
    temp = ""
    dans_crochets = False
    hub = hub.strip()
    for char in hub:
        if char == "[":
            dans_crochets = True
        elif char == "]":
            dans_crochets = False
        if char == separateur and not dans_crochets:
            new_tab.append(temp)
            temp = ""
        else:
            temp += char
    if "[" in hub and "]" in hub:
        new_tab.append(temp)
    if not "[" in hub and not "]" in hub:
        new_tab.append("[color=black]")
    return new_tab

def check_format_hub(hub: str):
    hub_split = split_check_format(hub, " ")
    if len(hub_split) != 5:
        raise TypeError(f"[Error] Hub definition expects 5 fields (name x y [options]), got {len(hub_split)}: {hub_split}")
    try:
        int(hub_split[2])
    except ValueError:
        raise TypeError(f"[Error] Hub X coordinate must be an integer, got '{hub_split[2]}'")
    try:
        int(hub_split[3])
    except ValueError:
        raise TypeError(f"[Error] Hub Y coordinate must be an integer, got '{hub_split[3]}'")
    if not hub_split[4].startswith("[") or not hub_split[4].endswith("]"):
        raise TypeError(f"[Error] Hub options must be enclosed in brackets [], got: '{hub_split[4]}'")
    if not "=" in hub_split[4]:
        raise TypeError(f"[Error] Hub options require '=' assignments (e.g. [color=red]), got: '{hub_split[4]}'")
        
    setting_hub_split = hub_split[4].strip("[]").split()
    thisdict = {}
    for item in setting_hub_split:
        split_color = item.split("=")
        if len(split_color) != 2:
            raise TabError(f"[Error] Malformed hub option '{item}' — expected key=value format")
            
        key, value = split_color[0], split_color[1]
        if key != "color" and key != "max_drones" and key != "zone":
            raise TabError(f"[Error] Unknown hub option '{key}' — allowed: color, max_drones, zone")
        
        thisdict[key] = value
        
    if "color" in thisdict and thisdict["color"] not in color_good:
        raise TabError(f"[Error] Invalid hub color '{thisdict['color']}' — allowed: {', '.join(color_good)}")

def check_double(files:str, check_double1:str, check_double2:str):
    res1:int  = 0
    res2:int = 0
    for line in files:
        if check_double1 in line :
            res1+=1
        if check_double2 in line:
            res2+=1
    if res1 != 1:
        raise ValueError(f"[Error] Expected exactly 1 '{check_double1}' definition, found {res1}")
    if res2 != 1 and len(check_double2) != 0:
        raise ValueError(f"[Error] Expected exactly 1 '{check_double2}' definition, found {res2}")
    return [res1, res2]

def open_files(path_file:str) -> str:
    files = ""
    with open(path_file) as f:
        files_read = str(f.read())
        if len(files_read) == 0:
            raise ValueError(f"[Error] This file ({path_file}) is empty")
        name_file = f.name.split("/")[-1]
        files += name_file
        files += "\n" 
        files += files_read
        return files

class ParsingFiles:
    def __init__(self, file_split:str):
        self.file_split = file_split
        self.nb_drone = 0
        self.start_hub:Hub = None
        self.end_hub:Hub = None
        self.hub = []
        self.all_name_hub:list[Hub] = []
        self.name_file = file_split[0]
        self.connection = {}
        self.nb_drone_check()
        self.hub_check()
        self.create_connection()

        self.create_neightbord()
        self.path_to_exit = []
        self.control_drone = ControlDrone(self)

    def create_neightbord(self):
        all_hubs = {h.name: h for h in self.hub}
        all_hubs[self.start_hub.name] = self.start_hub
        all_hubs[self.end_hub.name] = self.end_hub
        for conn in self.connection.values():
            connection_names = list(conn.values())[0]
            if len(connection_names) >= 2:
                name1 = connection_names[0].strip()
                name2 = connection_names[1].split()[0].strip()
                if name1 in all_hubs and name2 in all_hubs:
                    hub1 = all_hubs[name1]
                    hub2 = all_hubs[name2]
                    if hub2 not in hub1.neighbors:
                        hub1.neighbors.append(hub2)
                    if hub1 not in hub2.neighbors:
                        hub2.neighbors.append(hub1)
    def nb_drone_check(self):
        for line in self.file_split:
            if "nb_drone" in line:
                line_split = line.split(":")
                if len(line_split) != 2:
                    raise ValueError(f"[Error] 'nb_drone' line must use format 'nb_drone:<number>', got: '{line}'")
                try:
                    if line_split[1]:
                        self.nb_drone = int(line_split[1])
                except ValueError:
                    raise ValueError(f"[Error] 'nb_drone' value must be a positive integer, got: '{line_split[1].strip()}'")
                if  int(line_split[1]) < 0:
                    raise ValueError(f"[Error] 'nb_drone' value must be strictly positive, got: {line_split[1]}")
        if self.nb_drone == 0:
                    raise ValueError("[Error] No 'nb_drone' field found or value is 0 — at least 1 drone required")


    def check_connection(self):
        all_name_connection = []
        self.all_name_hub.append(self.start_hub.name)
        self.all_name_hub.append(self.end_hub.name)
        seen_pairs = set()
        for hub_name in self.hub:
            self.all_name_hub.append(hub_name.name)
        for connection_name_for in self.connection.values():
            connection_name = list(connection_name_for.values())[0]
            if len(connection_name) != 2:
                raise ValueError(f"[Error] Connection must link exactly 2 hubs, got: {connection_name}")
            pair = tuple(sorted(connection_name))
            if pair in seen_pairs:
                raise ValueError(f"[Error] Duplicate connection forbidden between '{connection_name[0]}' and '{connection_name[1]}'")
            if connection_name[0] == connection_name[1]:
                raise ValueError(f"[Error] Self-loop forbidden: hub '{connection_name[0]}' cannot connect to itself")
            seen_pairs.add(pair)
            all_name_connection.append(connection_name[0])
            all_name_connection.append(connection_name[1].split()[0])
        for connection in all_name_connection:
            if connection not in self.all_name_hub and "max_link_capacity=" not in connection:
                raise ValueError(f"[Error] Connection references unknown hub '{connection}' — not declared in map")
        if self.start_hub.name not in all_name_connection:
            raise ValueError(f"[Error] The start hub '{self.start_hub.name}' is isolated (has no connections).")

        if self.end_hub.name not in all_name_connection:
            raise ValueError(f"[Error] The end hub '{self.end_hub.name}' is isolated (has no connections).")


    def create_connection(self):
        i = 0
        for line in self.file_split:
            if line.startswith("connection: "):
                try:
                    content = line.split("connection:", 1)[1].strip()
                    max_lint = 0
                    if "max_link_capacity" in content:
                        max_lint = int(content.split("max_link_capacity=")[1].split()[0].strip("]"))
                        if max_lint < 1:
                            raise ValueError(f"[Error] max_link_capacity must be ≥ 1, got: {max_lint}")
                        if "[" in content:
                            bracket_content = content.split("[")[1].split("]")[0]
                            for item in bracket_content.split():
                                if "=" in item:
                                    key = item.split("=")[0]
                                    if key != "max_link_capacity":
                                        raise ValueError(f"[Error] Unknown connection option '{key}' — only 'max_link_capacity' is allowed")  
                    else:
                        max_lint = 1
                    self.connection.update({i:{max_lint:content.split("-")}})
                except Exception:
                    raise ValueError(f"[Error] Invalid connection syntax: '{line.strip()}'")
                i+=1
        self.check_connection()

    def hub_check(self):
        i = 0
        for line in self.file_split:
            if "start_hub:" in line:
                self.start_hub = hub_good_format(line)
            if "end_hub:" in line:
                self.end_hub = hub_good_format(line)
            if "hub:" in line and "end_hub" not in line and "start_hub" not in line:
                self.hub.append(hub_good_format(line)) 
                i+=1
        all_names = [self.start_hub.name, self.end_hub.name] + [h.name for h in self.hub]
        seen = set()
        for name in all_names:
            if name in seen:
                raise ValueError(f"[Error] Duplicate hub name '{name}' — each hub must have a unique name")
            seen.add(name)
        all_hubs_list = [self.start_hub, self.end_hub] + self.hub
        seen_coords = set()
        for h in all_hubs_list:
            coord = (h.x, h.y)
            if coord in seen_coords:
                raise ValueError(f"[Error] Duplicate coordinates ({h.x}, {h.y}) for hub '{h.name}' — each hub must have unique coordinates")
            seen_coords.add(coord)

from drone import ControlDrone

def pars_file(name_file:str) -> ParsingFiles:
    files_str = open_files(name_file)
    file_split = files_str.split('\n')
    check_double(file_split, "start_hub","end_hub")
    for line in file_split:
        if "hub:" in line:
            check_format_hub(line)
    maps = ParsingFiles(file_split)
    return maps


def hub_good_format(line: str) -> Hub:
    content = line.split(":", 1)[1].strip()
    if "[" in content and "]" in content:
        main_part, options_part = content.split("[", 1)
        options_str = options_part.rstrip("]").strip()
    else:
        main_part = content
        options_str = ""

    RESERVED_NAMES = {"hub", "start_hub", "end_hub", "connection", "nb_drones", "nb_drone"}
    tokens = main_part.split()
    name = tokens[0]
    if name in RESERVED_NAMES:
        raise ValueError(f"[Error] Hub name '{name}' is a reserved keyword — choose a different name")
    x = int(tokens[1])
    y = int(tokens[2])
    color = "black"
    max_drones = None
    zone = "normal"
    if options_str:
        for item in options_str.split():
            if "=" in item:
                key, value = item.split("=", 1)
                if key == "color":
                    color = value
                elif key == "max_drones":
                    try:
                        max_drones = int(value)
                    except ValueError:
                        raise ValueError(f"[Error] 'max_drones' value must be an integer, got: '{value}'")
                    if max_drones <= 0:
                        raise ValueError(f"[Error] 'max_drones' value must be strictly positive, got: {max_drones}")
                elif key == "zone":
                    zone = value
    hub = Hub(
        name=name,
        x=x,
        y=y,
        color=color,
        max_drones=max_drones,
        zone=zone
    )
    
    return hub