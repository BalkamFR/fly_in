

color_good = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'black', 'white']

def split_check_format(hub: str, separateur: str) -> list:
    new_tab = []
    temp = ""
    dans_crochets = False
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
        raise TypeError(f"nbr argument on hub is not good({hub_split})")
    try:
        int(hub_split[2])
    except ValueError:
        raise TypeError(f"argument: ({hub_split[2]}) is not int")
    try:
        int(hub_split[3])
    except ValueError:
        raise TypeError(f"argument: ({hub_split[3]}) is not int")
    if not hub_split[4].startswith("[") or not hub_split[4].endswith("]"):
        raise TypeError("Format setting hub is not good")
    if not "color" in hub_split[4] and not "[]" in hub_split[4]:
        return
    if not "=" in hub_split[4]:
        raise TypeError("Format setting hub is not good ")
        
    setting_hub_split = hub_split[4].strip("[]").split()
    thisdict = {}
    for item in setting_hub_split:
        split_color = item.split("=")
        if len(split_color) != 2:
            raise TabError("Format setting hub is not good")
            
        key, value = split_color[0], split_color[1]
        if key != "color" and key != "max_drones":
            raise TabError(f"{key} format is not good")
        
        thisdict[key] = value
        
    if "color" in thisdict and thisdict["color"] not in color_good:
        raise TabError(f"{thisdict['color']} is not good color")

def check_double(files:str, check_double1:str, check_double2:str):
    res1:int  = 0
    res2:int = 0
    for line in files:
        if check_double1 in line :
            res1+=1
        if check_double2 in line:
            res2+=1
    if res1 != 1:
        raise ValueError(f"parsing hub ({check_double1}) is not good")
    if res2 != 1 and len(check_double2) != 0:
        raise ValueError(f"parsing hub ({check_double2}) is not good")
    return [res1, res2]

def open_files(path_file:str) -> str:
    with open(path_file) as f:
        return f.read()

def pars_file(name_file:str):
    files_str = open_files(name_file)
    file_split = files_str.split('\n')
    check_double(file_split, "start_hub","end_hub")
    for line in file_split:
        if "hub" in line:
            check_format_hub(line)
    maps = ParsingFiles(file_split)
    print(f"nb drone {maps.nb_drone}")
    print(f"start hub {maps.start_hub}")
    print(f"end hub {maps.end_hub}")
    print(f"maps hub {maps.hub}")
    print(f"connection: {maps.connection}")



class Hub:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str = "black",
        max_drones: int | None = None,
        zone: str = "normal"
    ):
        self.name: str = name
        self.x: int = x
        self.y: int = y

        self.color: str = color
        self.max_drones: int | None = max_drones
        self.zone: str = zone

        self.neighbors: list[dict] = []
        self.current_drones: list = []
    def __repr__(self) -> str:
            return (
                f"Hub(name='{self.name}', pos=({self.x}, {self.y}), "
                f"zone='{self.zone}', max_drones={self.max_drones}, color='{self.color}')"
            )


def hub_good_format(line: str) -> Hub:
    content = line.split(":", 1)[1].strip()

    if "[" in content and "]" in content:
        main_part, options_part = content.split("[", 1)
        options_str = options_part.rstrip("]").strip()
    else:
        main_part = content
        options_str = ""

    tokens = main_part.split()
    name = tokens[0]
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
                    max_drones = int(value)
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




class ParsingFiles:
    def __init__(self, file_split:str):
        self.file_split = file_split
        self.nb_drone = 0
        self.start_hub = {}
        self.end_hub = {}
        self.hub = []
        self.connection = {}
        self.nb_drone_check()
        self.hub_check()
        self.create_connection()

    def nb_drone_check(self):
        for line in self.file_split:
            if "nb_drone" in line:
                line_split = line.split(":")
                if len(line_split) != 2:
                    raise ValueError("[Error] format is not good")
                try:
                    if line_split[1]:
                        self.nb_drone = int(line_split[1])
                except:
                    raise ValueError("[Error]: arg nb_drone is not int")
                if  int(line_split[1]) < 0:
                    raise ValueError("[Error]: arg nb_drone cant be not is negative value")
        if self.nb_drone == 0:
                    raise ValueError("[Error]: arg nb_drone cant be not is negative value")


    def check_connection(self):
        all_name_hub = []
        all_name_connection = []
        all_name_hub.append(self.start_hub.name)
        all_name_hub.append(self.end_hub.name)
        for hub_name in self.hub:
            all_name_hub.append(hub_name.name)
        for connection_name in self.connection.values():
            print(connection_name)
            if len(connection_name) != 2:
                raise "argument on connection is not good"
        print(all_name_hub)


    def create_connection(self):
        i = 0
        for line in self.file_split:
            if line.startswith("connection: "):
                try:
                    content = line.split("connection:", 1)[1].strip()
                    self.connection.update({i:content.split("-")})
                except Exception:
                    raise ValueError(f"[Error] Invalid connection syntax on line: '{line}'") 
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


if __name__ == '__main__':
    try:
        pars_file("maps/easy/01_linear_path.txt")
    except BaseException as e:
        print(e)