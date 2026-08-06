import pygame
from parsing import pars_file, ParsingFiles, Hub
from pathlib import Path
from drone import Drone



def drawing_function_menu(window, x, y, width, height):
    pygame.draw.rect(window, (0, 0, 255), [x, y, width, height])

class Screen:
    def __init__(self, setting_maps:ParsingFiles):
        pygame.init()
        self.setting_maps = setting_maps
        self.control_drones = setting_maps.control_drone
        self.zoom = 2
        self.width = 1920 
        self.height = 1080 
        self.change_background("background.png")
        self.name_program = "Fly-in"
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.name_program)
        self.first_color = (186, 186, 186)
        self.path_select = "easy"
        path = Path(f"maps/{self.path_select}")
        self.files_select = sorted([f.name for f in path.iterdir() if f.is_file()])
        self.virtual_surface = pygame.Surface((self.width, self.height))


    def change_background(self, path):
        bg_image = pygame.image.load(f"img/{path}")
        self.background = pygame.transform.smoothscale(bg_image, (self.width, self.height))
    def display(self):
        move_drone = 0
        clock = pygame.time.Clock()
        running = True
        page = "start_page"
        animation = 0
        while running:
            clock.tick(60)
            animation += 1
            if animation == 60:
                animation = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.btn_quit.collidepoint(event.pos):
                            running = False
                        if hasattr(self, "map_buttons") and page == "start_page":
                                for file_name, rect in self.map_buttons:
                                    if rect.collidepoint(event.pos):
                                        self.setting_maps = pars_file(f"maps/{self.path_select}/{file_name}")
                        if self.btn_easy.collidepoint(event.pos) and page == "start_page":
                            self.path_select = "easy"
                            path = Path(f"maps/{self.path_select}")
                            self.files_select = sorted([f.name for f in path.iterdir() if f.is_file()])
                        if self.btn_medium.collidepoint(event.pos) and page == "start_page":
                            self.path_select = "medium"
                            path = Path(f"maps/{self.path_select}")
                            self.files_select = sorted([f.name for f in path.iterdir() if f.is_file()])
                        if self.btn_hard.collidepoint(event.pos) and page == "start_page":
                            self.path_select = "hard"
                            path = Path(f"maps/{self.path_select}")
                            self.files_select = sorted([f.name for f in path.iterdir() if f.is_file()])
                        if self.btn_start.collidepoint(event.pos) and page == "start_page":
                            page = "hub_page"
                        if self.menu_home.collidepoint(event.pos):
                            page = "start_page"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    drone = None
                    drone_0:Drone = self.control_drones.all_drone[0]
                    from algo.astar import a_star
                    path_to_go = a_star(self.setting_maps.start_hub, self.setting_maps.end_hub)
                    drone_0.move_drone_to_end(path_to_go)
                    print("espace")
            for drone in self.control_drones.all_drone:
                drone.draw_animation()
            self.window.blit(self.background, (0, 0))
            if page == "start_page":
                self.drawing_start_page()
            if page == "hub_page":
                # self.window.fill((255, 0, 0))
                self.drawing_hub_page()
            pygame.display.update()
        pygame.quit()

    def text_center_box(self, box,text, police, color, font):
        self.font = pygame.font.SysFont(font, police)
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = box.center
        self.window.blit(text_surface, text_rect)

    def text_left_box(self, box, text, police, color, font):
        padding=15 
        self.font = pygame.font.SysFont(font, police)
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midleft = (box.left + padding, box.centery)
        self.window.blit(text_surface, text_rect)

    def all_transparent(self, list_box, flag=None):
        radius=15 
        border_width=2
        color_font = 29, 29, 34, 220
        border_color = 107, 120, 138
        i = 0
        for box in list_box:
            if i == len(list_box) - 1 and flag is None:
                color_font = 176, 35, 35, 200
                border_color = 255, 255, 255 
            if i == len(list_box) - 2 and flag is None:
                color_font = 35, 176, 98, 200
                border_color = 255, 255, 255 
            surface = pygame.Surface(box.size, pygame.SRCALPHA)
            pygame.draw.rect(
                surface, (color_font), surface.get_rect(), border_radius=radius
            )
            self.window.blit(surface, box)
                
            pygame.draw.rect(
                self.window,
                border_color,
                box,
                width=border_width,
                border_radius=radius,
            )
            i+=1

    def menu(self):
        menu_rect = pygame.Rect(0, 160  , self.width  , 80  )
        menu_surface = pygame.Surface(menu_rect.size, pygame.SRCALPHA)
        menu_surface.fill((25, 8, 36, 100))
        self.window.blit(menu_surface, menu_rect)

        self.menu_home = pygame.Rect((int(self.width * 0.35) - 75), 175 , 150 , 50 )
        self.text_center_box(
            self.menu_home, "Home", 25 , self.first_color, "consolas"
        )

        self.menu_maps = pygame.Rect((int(self.width * 0.50) - 75), 175, 150, 50)
        self.text_center_box(
            self.menu_maps, "Maps", 25 , self.first_color, "consolas"
        )

        self.menu_settings = pygame.Rect((int(self.width * 0.65) - 75) , 175 , 150 , 50 )
        self.text_center_box(
            self.menu_settings, "Settings", 25 , self.first_color, "consolas"
        )

    def header(self):
        header_rect = pygame.Rect(0, 0, self.width , 160 )
        menu_surface = pygame.Surface(header_rect.size, pygame.SRCALPHA)
        menu_surface.fill((25, 8, 36, 100))
        self.window.blit(menu_surface, header_rect)
        self.text_center_box(header_rect, "Fly-In", 70 , self.first_color, "lucidaconsole")


    def select_maps(self, start_x, start_y, all_btn):
        self.map_buttons = []

        size_height = 220
        size_width = 400
        max_width = 480
        padding_left = (max_width - size_width) / 2
        padding = 15 + size_height 
        i = 0
        start_y = (start_y + padding) - size_height
        for box in all_btn:
            self.box = pygame.Rect(
                start_x + padding_left, start_y + i, size_width, size_height
            )
            self.all_transparent([self.box], True)
            self.text_left_box(self.box, f"{box}", 22 , (255, 255, 255), "consolas")

            self.map_buttons.append(
                (box, self.box)
            )
            i += padding

    def drawing_start_page(self):
        self.change_background("background.png")
        self.detail_card = pygame.Rect((self.width - 400) , (self.height - 820) , 380 , 60 )
        self.right_panel_rect = pygame.Rect(self.width - 400 , (self.height - 820) , 380 , 400 )

        self.btn_start = pygame.Rect(0, 0, 380  , 80 )
        self.btn_start.centerx =( self.width // 2) 
        self.btn_start.bottom = (self.height - 20) 
        self.text_center_box(self.btn_start, "Start", 30 , (255, 255, 255), "consolas")

        self.btn_quit = pygame.Rect((self.width - 200)  , (self.height - 100) , 180 , 50 )
        self.text_center_box(self.btn_quit, "Quit", 20, (255, 255, 255), "consolas")

        self.text_center_box(self.detail_card, "Details carte", 32 , (255, 255, 255), "consolas")
        self.btn_help = pygame.Rect((self.width - 400)  , (self.height - 100) , 180 , 50 )
        self.text_center_box(self.btn_help, "Help", 20 , (255, 255, 255), "consolas")

        self.left_panel_rect = pygame.Rect(15, self.height - 820, 480, 800)

        self.all_transparent([self.left_panel_rect, self.right_panel_rect,self.btn_help ,self.btn_start , self.btn_quit])

        self.name_maps = pygame.Rect(self.width - 400 , self.height - 770, 110, 70)
        self.text_left_box(self.name_maps, "Name: ", 25, (255, 255, 255), "consolas")
        self.nb_drone_maps = pygame.Rect(self.width - 400 , self.height - 730, 110, 70)
        self.text_left_box(self.nb_drone_maps, "Drones: ", 25, (255, 255, 255), "consolas")
        self.hub_maps = pygame.Rect(self.width - 400 , self.height - 690, 110, 70)
        self.text_left_box(self.hub_maps, "Hubs: ", 25, (255, 255, 255), "consolas")
        self.mode_maps = pygame.Rect(self.width - 400 , self.height - 650, 110, 70)
        self.text_left_box(self.mode_maps, "Mode: ", 25, (255, 255, 255), "consolas")


        self.name_maps_text = pygame.Rect(self.width - 240 , self.height - 770, 110, 70)
        self.text_left_box(self.name_maps_text, f"{self.setting_maps.name_file}", 15, (255, 255, 255), "consolas")
        self.nb_drone_maps_text = pygame.Rect(self.width - 240 , self.height - 730, 110, 70)
        self.text_left_box(self.nb_drone_maps_text, f"{self.setting_maps.nb_drone}", 20, (255, 255, 255), "consolas")
        self.hub_maps_text = pygame.Rect(self.width - 240 , self.height - 690, 110, 70)
        self.text_left_box(self.hub_maps_text, f"{len(self.setting_maps.all_name_hub)}", 20, (255, 255, 255), "consolas")
        self.mode_maps_text = pygame.Rect(self.width - 240 , self.height - 650, 110, 70)
        self.text_left_box(self.mode_maps_text, "Mode: ", 20, (255, 255, 255), "consolas")

        self.select_maps(15, self.height - 745, self.files_select)

        self.btn_easy = pygame.Rect(30, self.height - 800, 120, 50)
        self.btn_medium = pygame.Rect(190, self.height - 800, 120, 50)
        self.btn_hard = pygame.Rect(360, self.height - 800, 120, 50)

        self.all_transparent([self.btn_easy, self.btn_medium, self.btn_hard], flag=True)

        self.text_center_box(self.btn_easy, "Easy", 22, (21, 237, 47), "consolas")
        self.text_center_box(self.btn_medium, "Medium", 22, (21, 79, 237), "consolas")
        self.text_center_box(self.btn_hard, "Hard", 22, (255, 0, 0), "consolas")

        self.header()
        self.menu()


    def draw_connections(self, size: int = 100) -> None:
        if self.path_select == "easy":
            size = 150
        if self.path_select == "medium":
            size = 125
        if self.path_select == "hard":
            size = 100
        if self.path_select == "easy":
            color_select = 21, 237, 47
        if self.path_select == "medium":
            color_select = 21, 79, 237
        if self.path_select == "hard":
            color_select = 255, 0, 0
        all_hubs = [
            self.setting_maps.start_hub,
            self.setting_maps.end_hub,
        ] + self.setting_maps.hub
        hubs_by_name = {h.name: h for h in all_hubs}

        min_x = min(h.x for h in all_hubs)
        max_x = max(h.x for h in all_hubs)
        min_y = min(h.y for h in all_hubs)
        max_y = max(h.y for h in all_hubs)

        margin = (size // 2) + 20
        usable_w = self.hub_zone.width - (2 * margin)
        usable_h = self.hub_zone.height - (2 * margin)

        range_x = (max_x - min_x) if max_x != min_x else 1
        range_y = (max_y - min_y) if max_y != min_y else 1

        scale = min(usable_w / range_x, usable_h / range_y)

        offset_x = (usable_w - (range_x * scale)) / 2
        offset_y = (usable_h - (range_y * scale)) / 2

        def to_pixels(target_hub: Hub) -> tuple[int, int]:

            px = int(
                self.hub_zone.x
                + margin
                + offset_x
                + (target_hub.x - min_x) * scale
            )
            py = int(
                self.hub_zone.y
                + margin
                + offset_y
                + (max_y - target_hub.y) * scale
            )
            return (px, py)

        for conn in self.setting_maps.connection.values():
            if len(conn) >= 2:
                n1 = conn[0].strip()
                n2 = conn[1].split()[0].strip()

                if n1 in hubs_by_name and n2 in hubs_by_name:
                    pos1 = to_pixels(hubs_by_name[n1])
                    pos2 = to_pixels(hubs_by_name[n2])
                    pygame.draw.line(
                        self.window, (color_select), pos1, pos2, width=3
                    )
    def draw_drones(self,hub:Hub ,x, y) -> None:
        for drone in hub.current_drones:
            try:
                drone_img = pygame.image.load(drone.img_drone)
                drone_img = pygame.transform.scale(drone_img, (40, 40))
                rect = drone_img.get_rect(center=(x, y))
                self.window.blit(drone_img, rect)
            except (pygame.error, FileNotFoundError):
                pygame.window.circle(self.screen, (255, 0, 0), (drone.pos_x, drone.pos_y), 15)


    def create_hub(self, hub: Hub, size: int = 100) -> None:
        if self.path_select == "easy":
            size = 150
        if self.path_select == "medium":
            size = 125
        if self.path_select == "hard":
            size = 100
        color_map: dict[str, tuple[int, int, int]] = {
            "red": (220, 53, 69),
            "blue": (13, 110, 253),
            "green": (25, 135, 84),
            "yellow": (255, 193, 7),
            "orange": (253, 126, 20),
            "purple": (111, 66, 193),
            "black": (33, 37, 41),
            "white": (248, 249, 250),
            "cyan": (13, 202, 240),
            "brown": (139, 69, 19),
            "lime": (50, 205, 50),
            "magenta": (255, 0, 255),
            "gold": (255, 215, 0),
        }

        all_hubs = [
            self.setting_maps.start_hub,
            self.setting_maps.end_hub,
        ] + self.setting_maps.hub

        min_x = min(h.x for h in all_hubs)
        max_x = max(h.x for h in all_hubs)
        min_y = min(h.y for h in all_hubs)
        max_y = max(h.y for h in all_hubs)

        margin = (size // 2) + 20
        usable_w = self.hub_zone.width - (2 * margin)
        usable_h = self.hub_zone.height - (2 * margin)

        range_x = (max_x - min_x) if max_x != min_x else 1
        range_y = (max_y - min_y) if max_y != min_y else 1

        scale = min(usable_w / range_x, usable_h / range_y)

        offset_x = (usable_w - (range_x * scale)) / 2
        offset_y = (usable_h - (range_y * scale)) / 2

        cx = int(
            self.hub_zone.x + margin + offset_x + (hub.x - min_x) * scale
        )
        cy = int(
            self.hub_zone.y + margin + offset_y + (max_y - hub.y) * scale
        )

        radius = size // 2
        color_rgb = color_map.get(hub.color, (128, 128, 128))

        pygame.draw.circle(self.window, color_rgb, (cx, cy), radius)
        pygame.draw.circle(
            self.window, (255, 255, 255), (cx, cy), radius, width=2
        )

        hub_rect = pygame.Rect(cx - radius, cy - radius, size, size)
        size_name_hub = 16
        if len(hub.name) > 10:
            size_name_hub = 10
        self.text_center_box(
            hub_rect, hub.name, size_name_hub, (255, 255, 255), "consolas"
        )


    def draw_all_drones(self) -> None:
        size = 100
        if self.path_select == "easy":
            size = 150
        elif self.path_select == "medium":
            size = 125
        elif self.path_select == "hard":
            size = 100

        all_hubs = [
            self.setting_maps.start_hub,
            self.setting_maps.end_hub,
        ] + self.setting_maps.hub

        min_x = min(h.x for h in all_hubs)
        max_x = max(h.x for h in all_hubs)
        min_y = min(h.y for h in all_hubs)
        max_y = max(h.y for h in all_hubs)

        margin = (size // 2) + 20
        usable_w = self.hub_zone.width - (2 * margin)
        usable_h = self.hub_zone.height - (2 * margin)

        range_x = (max_x - min_x) if max_x != min_x else 1
        range_y = (max_y - min_y) if max_y != min_y else 1

        scale = min(usable_w / range_x, usable_h / range_y)
        offset_x = (usable_w - (range_x * scale)) / 2
        offset_y = (usable_h - (range_y * scale)) / 2

        for drone in self.control_drones.all_drone:
            cx = int(self.hub_zone.x + margin + offset_x + (drone.pos_x - min_x) * scale)
            cy = int(self.hub_zone.y + margin + offset_y + (max_y - drone.pos_y) * scale)

            try:
                drone_img = pygame.image.load(drone.img_drone)
                drone_img = pygame.transform.scale(drone_img, (80, 80))
                rect = drone_img.get_rect(center=(cx, cy))
                self.window.blit(drone_img, rect)
            except (pygame.error, FileNotFoundError):
                pygame.draw.circle(self.window, (255, 0, 0), (cx, cy), 15)

    def drawing_hub_page(self):
        self.change_background("background_hub.png")
        self.btn_quit = pygame.Rect(self.width - 200, self.height - 100, 180, 50)
        self.hub_zone = pygame.Rect(20, 270, self.width - 40, 680)
        self.text_center_box(self.btn_quit, "Quit", 20, (255, 255, 255), "consolas")
        self.all_transparent([self.btn_quit])
        self.all_transparent([self.hub_zone], flag=True)
        self.draw_connections()
        self.create_hub(self.setting_maps.start_hub)
        self.create_hub(self.setting_maps.end_hub)
        for h in self.setting_maps.hub:
            self.create_hub(h)
        self.draw_all_drones()
        self.header()
        self.menu()
