from parsing import Hub

class Node:
    def __init__(self, hub, parent):
        self.current_hub:Hub = hub
        self.parent = parent
        self.score_g = 0
        self.score_h = 0
        self.score_f = self.score_g + self.score_h


def heuristic(start, goal):
    pass

def find_lower_value(open_list:list[Node]):
    node_min = open_list[0]
    for node in open_list:
        if node.score_f < node_min.score_f:
            node_min = node
    return node_min

def find_distance(current, neighbor):
    pass

def reconstruct_path(current:Node):
    path = []
    while current is not None:
        path.insert(0, current)
        current = current.parent
    return path

def a_star(start:Node, goal:Node):
    open_list = [start]
    closed_list = []

    while len(open_list) != 0:
        current = find_lower_value(open_list)
        open_list.remove(current)
        closed_list.append(current)

        if current.current_hub.name == goal.current_hub.name:
            return reconstruct_path(current)

        for neighbor in current:
            neighbor:Node = neighbor
            if neighbor in closed_list:
                continue
            tentative_g = current.score_g + find_distance(current, neighbor)
            if neighbor not in open_list:
                open_list.append(neighbor)
            elif tentative_g >= neighbor.score_g:
                continue
            neighbor.parent = current
            neighbor.score_g = tentative_g
            neighbor.score_h = heuristic(neighbor, goal)
            neighbor.score_f = neighbor.score_g + neighbor.score_h

    return "failure"