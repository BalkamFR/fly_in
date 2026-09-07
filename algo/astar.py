from __future__ import annotations

import heapq
import sys
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from hub import Hub

if TYPE_CHECKING:
    from drone import Drone
    from py_game.scren import Screen

ReservationKey = Union[Tuple[str, int], Tuple[Tuple[str, str], int]]


class State:
    def __init__(
        self,
        hub: Hub,
        turn: int,
        g: float,
        h: float,
        parent: Optional[State] = None,
    ) -> None:
        self.hub = hub
        self.turn = turn
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent


def reverse_dijkstra(
    end_hub: Hub, all_hubs: List[Hub]
) -> Dict[str, float]:
    distances = {hub.name: float("inf") for hub in all_hubs}
    distances[end_hub.name] = 0.0
    queue: List[Tuple[float, int, Hub]] = [(0.0, 0, end_hub)]
    counter = 1

    while queue:
        dist, _, current = heapq.heappop(queue)
        if dist > distances[current.name]:
            continue

        for neighbor in current.neighbors:
            if getattr(neighbor, "zone", "normal") == "blocked":
                continue

            cost = (
                2.0
                if getattr(neighbor, "zone", "normal") == "restricted"
                else 0.5
                if getattr(neighbor, "zone", "normal") == "priority"
                else 1.0
            )
            new_dist = dist + cost

            if new_dist < distances[neighbor.name]:
                distances[neighbor.name] = new_dist
                heapq.heappush(queue, (new_dist, counter, neighbor))
                counter += 1
    return distances


def reconstruct_path(current: State) -> List[Tuple[Hub, int]]:
    path: List[Tuple[Hub, int]] = []
    node: Optional[State] = current
    while node is not None:
        path.insert(0, (node.hub, node.turn))
        node = node.parent
    return path


def is_zone_free(
    hub: Hub,
    turn: int,
    reservations: Dict[ReservationKey, int],
    start: str,
    end: str,
) -> bool:
    if hub.name in (start, end):
        return True
    capacity = hub.max_drones if hub.max_drones else 1
    key: ReservationKey = (hub.name, turn)
    used: int = reservations.get(key, 0)
    return used < capacity


def is_link_free(
    h1: Hub,
    h2: Hub,
    turn: int,
    reservations: Dict[ReservationKey, int],
    link_capacity: Dict[Tuple[str, str], int],
) -> bool:
    link_key: Tuple[str, str] = (
        min(h1.name, h2.name), max(h1.name, h2.name)
    )
    capacity = link_capacity.get(link_key, 1)
    key: ReservationKey = (link_key, turn)
    used: int = reservations.get(key, 0)
    return used < capacity


def a_star(
    start: Hub,
    end: Hub,
    reservations: Dict[ReservationKey, int],
    link_capacity: Dict[Tuple[str, str], int],
    true_distances: Dict[str, float],
    max_turn: int = 500,
) -> List[Tuple[Hub, int]]:
    start_h = true_distances.get(start.name, float("inf"))
    if start_h == float("inf"):
        return []

    start_state = State(start, 0, 0.0, start_h)
    open_list: List[Tuple[float, int, State]] = [
        (start_state.f, 0, start_state)
    ]
    visited: set[Tuple[str, int]] = set()
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

        if is_zone_free(
            current.hub, current.turn + 1,
            reservations, start.name, end.name,
        ):
            wait_state = State(
                current.hub, current.turn + 1,
                current.g + 1.0, current.h, current,
            )
            heapq.heappush(
                open_list, (wait_state.f, counter, wait_state)
            )
            counter += 1

        for neighbor in current.hub.neighbors:
            if getattr(neighbor, "zone", "normal") == "blocked":
                continue

            move_time: int = (
                2
                if getattr(neighbor, "zone", "normal") == "restricted"
                else 1
            )
            move_cost: float = (
                2.0
                if getattr(neighbor, "zone", "normal") == "restricted"
                else 0.5
                if getattr(neighbor, "zone", "normal") == "priority"
                else 1.0
            )
            arrival_turn = current.turn + move_time

            if not is_link_free(
                current.hub, neighbor, current.turn + 1,
                reservations, link_capacity,
            ):
                continue

            if not is_zone_free(
                neighbor, arrival_turn,
                reservations, start.name, end.name,
            ):
                continue

            new_g = current.g + move_cost
            new_h = true_distances.get(neighbor.name, float("inf"))

            if new_h == float("inf"):
                continue

            move_state = State(
                neighbor, arrival_turn, new_g, new_h, current
            )
            heapq.heappush(
                open_list, (move_state.f, counter, move_state)
            )
            counter += 1

    return []


def start_astar_drones(scren: Screen) -> None:
    assert scren.setting_maps is not None
    assert scren.control_drones is not None
    assert scren.setting_maps.start_hub is not None
    assert scren.setting_maps.end_hub is not None

    start_hub: Hub = scren.setting_maps.start_hub
    end_hub: Hub = scren.setting_maps.end_hub

    reservations: Dict[ReservationKey, int] = {}
    schedule: Dict[int, List[str]] = {}
    link_capacity = scren.setting_maps.link_capacity
    nb_drones = len(scren.control_drones.all_drone)
    max_turn = max(500, nb_drones * 20)

    all_hubs: List[Hub] = (
        [start_hub, end_hub] + scren.setting_maps.hub
    )
    print(
        f"Path of file : {scren.path}/{scren.setting_maps.name_file}\n"
    )
    true_distances = reverse_dijkstra(end_hub, all_hubs)

    for drone_ in scren.control_drones.all_drone:
        drone: Drone = drone_
        path = a_star(
            start_hub,
            end_hub,
            reservations,
            link_capacity,
            true_distances,
            max_turn,
        )
        if not path:
            print(
                f"[Warning] {drone.name_drone}: no path found"
                f" (max_turn={max_turn})"
            )
            continue

        d_id = f"D{int(drone.name_drone.split('_')[1]) + 1}"
        drone.path = [p[0] for p in path]

        for i in range(1, len(path)):
            prev_hub, prev_turn = path[i - 1]
            curr_hub, curr_turn = path[i]

            if curr_hub != prev_hub:
                if curr_turn - prev_turn == 2:
                    conn_name = f"{prev_hub.name}-{curr_hub.name}"
                    schedule.setdefault(prev_turn + 1, []).append(
                        f"{d_id}-{conn_name}"
                    )

                schedule.setdefault(curr_turn, []).append(
                    f"{d_id}-{curr_hub.name}"
                )

                link: Tuple[str, str] = (
                    min(prev_hub.name, curr_hub.name),
                    max(prev_hub.name, curr_hub.name),
                )
                link_key: ReservationKey = (link, prev_turn + 1)
                reservations[link_key] = (
                    reservations.get(link_key, 0) + 1
                )
                if curr_turn - prev_turn == 2:
                    link_key2: ReservationKey = (
                        link, prev_turn + 2
                    )
                    reservations[link_key2] = (
                        reservations.get(link_key2, 0) + 1
                    )

            if curr_hub.name != end_hub.name:
                zone_key: ReservationKey = (curr_hub.name, curr_turn)
                reservations[zone_key] = (
                    reservations.get(zone_key, 0) + 1
                )

        path_find = [p[0] for p in path]
        drone.move_drone_to_end(path_find)

    all_turn_live: List[str] = []
    if schedule:
        max_turn = max(schedule.keys())
        for t in range(1, max_turn + 1):
            if t in schedule:
                all_turn_live.append(" ".join(schedule[t]))
                print(" ".join(schedule[t]))

                if "--capacity-info" in sys.argv:
                    infos: List[str] = []
                    for res_key, used in reservations.items():
                        item_raw, turn = res_key
                        if turn == t:
                            if isinstance(item_raw, tuple):
                                h1, h2 = item_raw
                                max_cap = link_capacity.get(
                                    item_raw, 1  # type: ignore[arg-type]
                                )
                                infos.append(
                                    f"Connection {h1}-{h2}:"
                                    f" {used}/{max_cap} capacity used"
                                )
                            else:
                                max_cap = 1
                                for h in all_hubs:
                                    if h.name == item_raw:
                                        max_cap = (
                                            h.max_drones
                                            if h.max_drones
                                            else 1
                                        )
                                        break
                                infos.append(
                                    f"Zone {item_raw}:"
                                    f" {used}/{max_cap} drones"
                                )

                    if infos:
                        print(", ".join(infos))
