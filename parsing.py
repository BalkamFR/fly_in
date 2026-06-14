color_good = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'black', 'white']

def check_format_hub(hub:str):
    hub_split = hub.split()
    if len(hub_split) != 5:
        raise TypeError("nbr on hub argument is not good")
    try:
        int(hub_split[2])
        int(hub_split[3])
    except:
        raise TypeError("argument is not int")
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

def open_files(path_file:str) -> str:
    with open(path_file) as f:
        return f.read()
   

def pars_file(name_file:str):
    file_split = open_files(name_file).split('\n')
    for line in file_split:
        if "hub" in line:
            print(line)
            check_format_hub(line)


if __name__ == '__main__':
    try:
        pars_file("maps/easy/01_linear_path.txt")
    except BaseException as e:
        print(e)