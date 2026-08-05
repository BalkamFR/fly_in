from parsing import Hub

class Node:
    def __init__(self, hub, parent):
        self.current_hub:Hub = hub
        self.parent = parent
        self.score_g = 0
        self.score_h = 0
        self.score_f = self.score_g + self.score_f


def a_star(start_hub, end_hub):
    open_list = []
    closed_list = set()
