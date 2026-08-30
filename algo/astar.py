import heapq
from typing import List, Tuple, Optional, Dict
from parsing import Hub

class State:
    def __init__(self, hub: Hub, turn: int, g: float, h: float, parent: Optional['State'] = None):
        self.hub = hub
        self.turn = turn
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent

def reverse_dijkstra(end_hub: Hub, all_hubs: List[Hub]) -> Dict[str, float]:
    distances = {hub.name: float('inf') for hub in all_hubs}
    distances[end_hub.name] = 0.0
    queue = [(0.0, 0, end_hub)]
    counter = 1

    while queue:
        dist, _, current = heapq.heappop(queue)
        if dist > distances[current.name]:
            continue

        for neighbor in current.neighbors:
            if getattr(neighbor, "zone", "normal") == "blocked":
                continue

            cost = 2.0 if getattr(current, "zone", "normal") == "restricted" else 1.0
            new_dist = dist + cost
            
            if new_dist < distances[neighbor.name]:
                distances[neighbor.name] = new_dist
                heapq.heappush(queue, (new_dist, counter, neighbor))
                counter += 1
    return distances

def reconstruct_path(current: State) -> List[Tuple[Hub, int]]:
    path = []
    while current:
        path.insert(0, (current.hub, current.turn))
        current = current.parent
    return path

def is_zone_free(hub: Hub, turn: int, reservations: dict, start: str, end: str) -> bool:
    if hub.name in (start, end):
        return True
    capacity = hub.max_drones if hub.max_drones else 1
    return reservations.get((hub.name, turn), 0) < capacity

def get_link_capacity(h1: Hub, h2: Hub, connections: dict) -> int:
    link_key = tuple(sorted([h1.name, h2.name]))
    for val in connections.values():
        for cap, names in val.items():
            parsed = tuple(sorted([names[0].strip(), names[1].split()[0].strip()]))
            if parsed == link_key:
                return cap
    return 1

def is_link_free(h1: Hub, h2: Hub, turn: int, reservations: dict, connections: dict) -> bool:
    link_key = tuple(sorted([h1.name, h2.name]))
    capacity = get_link_capacity(h1, h2, connections)
    return reservations.get((link_key, turn), 0) < capacity

def a_star(start: Hub, end: Hub, reservations: dict, connections: dict, true_distances: Dict[str, float], max_turn: int = 150) -> List[Tuple[Hub, int]]:
    start_h = true_distances.get(start.name, float('inf'))
    if start_h == float('inf'):
        return []

    start_state = State(start, 0, 0.0, start_h)
    open_list = [(start_state.f, 0, start_state)]
    visited = set()
    counter = 1

    while open_list:
        _, _, current = heapq.heappop(open_list)

        if current.hub.name == end.name:
            return reconstruct_path(current)

        state_key = (current.hub.name, current.turn)
        if state_key in visited:
            continue
        visited.add(state_key)

        if current.turn >= max_turn:
            continue

        if is_zone_free(current.hub, current.turn + 1, reservations, start.name, end.name):
            wait_state = State(current.hub, current.turn + 1, current.g + 1.0, current.h, current)
            heapq.heappush(open_list, (wait_state.f, counter, wait_state))
            counter += 1

        for neighbor in current.hub.neighbors:
            if getattr(neighbor, "zone", "normal") == "blocked":
                continue

            move_time = 2 if getattr(neighbor, "zone", "normal") == "restricted" else 1
            arrival_turn = current.turn + move_time

            if not is_link_free(current.hub, neighbor, current.turn + 1, reservations, connections):
                continue

            if not is_zone_free(neighbor, arrival_turn, reservations, start.name, end.name):
                continue

            bonus = 0.5 if getattr(neighbor, "zone", "normal") == "priority" else 0.0
            new_g = current.g + move_time - bonus
            new_h = true_distances.get(neighbor.name, float('inf'))

            if new_h == float('inf'):
                continue

            move_state = State(neighbor, arrival_turn, new_g, new_h, current)
            heapq.heappush(open_list, (move_state.f, counter, move_state))
            counter += 1

    return []


def start_astar_drones(scren):

    reservations = {}
    schedule = {}

    all_hubs = [scren.setting_maps.start_hub, scren.setting_maps.end_hub] + scren.setting_maps.hub
    true_distances = reverse_dijkstra(scren.setting_maps.end_hub, all_hubs)

    print(scren.control_drones.all_drone)
    for drone in scren.control_drones.all_drone:
        path = a_star(
            scren.setting_maps.start_hub,
            scren.setting_maps.end_hub,
            reservations,
            scren.setting_maps.connection,
            true_distances
        )
        if not path:
            continue

        d_id = f"D{int(drone.name_drone.split('_')[1]) + 1}"
        drone.path = [p[0] for p in path]

        for i in range(1, len(path)):
            prev_hub, prev_turn = path[i - 1]
            curr_hub, curr_turn = path[i]

            if curr_hub != prev_hub:
                if curr_turn - prev_turn == 2:
                    conn_name = f"{prev_hub.name}-{curr_hub.name}"
                    schedule.setdefault(prev_turn + 1, []).append(f"{d_id}-{conn_name}")
                
                schedule.setdefault(curr_turn, []).append(f"{d_id}-{curr_hub.name}")

                link = tuple(sorted([prev_hub.name, curr_hub.name]))
                reservations[(link, prev_turn + 1)] = reservations.get((link, prev_turn + 1), 0) + 1

            if curr_hub.name != scren.setting_maps.end_hub.name:
                reservations[(curr_hub.name, curr_turn)] = reservations.get((curr_hub.name, curr_turn), 0) + 1

        drone.move_drone_to_end([p[0] for p in path])

    if schedule:
        max_turn = max(schedule.keys())
        for t in range(1, max_turn + 1):
            if t in schedule:
                print(" ".join(schedule[t]))

