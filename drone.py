from parsing import Hub,ParsingFiles
import pygame

class Drone:
    def __init__(self, name, hub_start:Hub):
        self.hub_select:Hub = hub_start
        self.pos_x = 0
        self.pos_y = 0
        self.path:list[Hub] = []
        self.img_drone = "img/drone.png"
        self.name_drone = name
        self.edit_pos(self.hub_select.get_pos())
        self.hub_select.add_drone_hub(self)
        self.animation = []
        

    def move_drone_to_end(self, path_to_go):
        for hub in path_to_go:
            hub:Hub = hub
            self.move_to_hub(hub)
    def move_to_hub(self, hub_select_param: Hub):
        self.hub_select.remove_drone_hub(self)
        self.hub_select = hub_select_param
        self.hub_select.add_drone_hub(self)

        self.calc_animation(hub_select_param)

    def calc_animation(self, hub_select_param: Hub):
        step = 5
        
        hub_start_x = self.pos_x
        hub_start_y = self.pos_y
        hub_go_x = hub_select_param.x
        hub_go_y = hub_select_param.y
        
        dis_x = hub_go_x - hub_start_x
        dis_y = hub_go_y - hub_start_y
        
        jump_x = dis_x / step
        jump_y = dis_y / step
        
        new_tab = []
        for i in range(step):
            hub_start_x += jump_x
            hub_start_y += jump_y
            new_tab.append((hub_start_x, hub_start_y))
            
        new_tab.append((hub_go_x, hub_go_y)) 
        self.animation = new_tab

    def draw_animation(self):
        if len(self.animation) > 0:
            self.pos_x = self.animation[0][0]
            self.pos_y = self.animation[0][1]
            del self.animation[0]
            return 1
        return 0

    def edit_pos(self, pos:tuple):
        self.pos_x = pos[0]
        self.pos_y = pos[1]

    def __repr__(self):
        return f"name : {self.name_drone} pos: {(self.pos_x, self.pos_y)}"


class ControlDrone:
    def __init__(self, parsing:ParsingFiles):
        self.nb_drone = parsing.nb_drone
        self.all_drone = []
        self.parsing = parsing
        self.create_all_drone()

    def create_all_drone(self):
        for i in range(self.nb_drone):
            drone:Drone = Drone(f"drone_{i}",self.parsing.start_hub)
            # print(drone.name_drone)
            drone.path = self.parsing.path_to_exit
            self.all_drone.append(drone)