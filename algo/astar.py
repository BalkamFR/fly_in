from parsing import Hub

class Node:
    def __init__(self, hub, parent):
        self.current_hub:Hub = hub
        self.parent = parent
        self.score_g = 0
        self.score_h = 0
        self.score_f = 0

    def __repr__(self):
        return f"{self.current_hub.name}"

def heuristic(start, goal):
    return 0

def find_lower_value(open_list:list[Node]):

    node_min = open_list[0]
    for node in open_list:
        if node.score_f < node_min.score_f:
            node_min = node
    return node_min

def find_distance(current, neighbor):
    return 1

def reconstruct_path(current:Node):
    path = []
    while current is not None:
        path.insert(0, current.current_hub)
        current = current.parent
    return path


def check_node_in_list(hub_name: str, node_list: list[Node]):
    for node in node_list:
        if node.current_hub.name == hub_name:
            return node
    return None

def a_star(start_pars, goal_pars):

    start = Node(start_pars, None)

    goal = Node(goal_pars, None)



    open_list = [start]
    closed_list = []

    i = 0
    current = find_lower_value(open_list)

    while len(open_list) != 0:

        i+=1
        current = find_lower_value(open_list)
        open_list.remove(current)
        closed_list.append(current)

        if current.current_hub.name == goal.current_hub.name:
            return reconstruct_path(current)
        neighbor_hub = current.current_hub.neighbors
        if neighbor_hub is None:
            return reconstruct_path(current)
        if check_node_in_list(neighbor_hub.name, closed_list):
            continue

        tentative_g = current.score_g + find_distance(current, neighbor_hub)
        existing_node = check_node_in_list(neighbor_hub.name, open_list)

        if not existing_node:
            new_node = Node(neighbor_hub, parent=current)
            new_node.score_g = tentative_g
            new_node.score_h = heuristic(neighbor_hub, goal.current_hub)
            new_node.score_f = new_node.score_g + new_node.score_h
            open_list.append(new_node)
        elif tentative_g < existing_node.score_g:
            existing_node.parent = current
            existing_node.score_g = tentative_g
            existing_node.score_f = existing_node.score_g + existing_node.score_h

    return []