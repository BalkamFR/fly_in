

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
    new_tab.append(temp)
    return new_tab
def check_format_hub(hub:str):
    hub_split = split_check_format(hub, " ")
    print(hub_split)
    if len(hub_split) != 5:
        raise TypeError(f"nbr argument on hub is not good({hub_split})")
    try:
        int(hub_split[2])
        int(hub_split[3])
    except:
        raise TypeError(f"argument: ({hub_split[2]}) is not int")
    if not hub_split[4].startswith("[") or not hub_split[4].endswith("]"):
        raise TypeError("Format setting hub is not good")
    if not "color" in hub_split[4]:
        raise TypeError("Format setting hub is not good (color is mandatory)")
    if not "=" in hub_split[4]:
        raise TypeError("Format setting hub is not good ")
    setting_hub_split = hub_split[4].strip("[]").split()
    for color in setting_hub_split:
        thisdict:dict = {}
        split_color = color.split("=")
        if split_color[0] != "color" and split_color[0] != "max_drones":
            raise TabError(f"{split_color[0]} format is not good")
        thisdict.update({split_color[0]:split_color[1]})
        if not thisdict["color"] in color_good:
            raise TabError(f"{thisdict["color"]} is not good color")

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
    print(maps.nb_drone)
    print(maps.start_hub)
    print(maps.end_hub)
    print(maps.hub)



def hub_good_format(line):
    new_dict = {}

    line_split = line.split(":")
    line_split = line_split[1].split()
    new_dict.update({"name": line_split[0]})
    new_dict.update({"cordonne_x": line_split[1]})
    new_dict.update({"cordonne_y": line_split[2]})
    color = line_split[3].strip("[]").split("=")
    new_dict.update({"color": color[1]})

    return new_dict


class ParsingFiles:
    def __init__(self, file_split:str):
        self.file_split = file_split
        self.nb_drone = 0
        self.start_hub = {}
        self.end_hub = {}
        self.hub = {}
        self.nb_drone_check()
        self.hub_check()

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

    def hub_check(self):
        i = 0
        for line in self.file_split:
            if "start_hub:" in line:
                self.start_hub = hub_good_format(line)
            if "end_hub:" in line:
                self.end_hub = hub_good_format(line)
            if "hub:" in line and "end_hub" not in line and "start_hub" not in line:
                self.hub.update({f"hub_{i}":hub_good_format(line)}) 
                i+=1


if __name__ == '__main__':
    try:
        pars_file("maps/easy/01_linear_path.txt")
    except BaseException as e:
        print(e)