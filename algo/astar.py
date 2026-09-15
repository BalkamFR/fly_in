from __future__ import annotations

import heapq
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from hub import Hub

if TYPE_CHECKING:
    from drone import Drone
    from py_game.scren import Screen

ReservationKey = Union[Tuple[str, int], Tuple[Tuple[str, str], int]]


class State:
    """Represents a node in the A* search space.

    Each state encodes a drone at a specific hub at a specific simulation
    turn, together with the g (cost so far), h (heuristic), and f = g + h
    values used to order the priority queue.

    Attributes:
        hub: The hub the drone occupies in this state.
        turn: The simulation turn number at which the drone is at this hub.
        g: Accumulated movement cost from the start state.
        h: Heuristic estimate of cost to reach the destination (from
            reverse Dijkstra).
        f: Total estimated cost f = g + h used for priority ordering.
        parent: The preceding State in the path, or None for the initial
            state.
    """

    def __init__(
        self,
        hub: Hub,
        turn: int,
        g: float,
        h: float,
        parent: Optional[State] = None,
    ) -> None:
        """Initializes an A* search state.

        Args:
            hub: Hub the drone is located at in this state.
            turn: Simulation turn corresponding to this state.
            g: Cumulative cost from the start to this state.
            h: Heuristic remaining cost estimate to the goal.
            parent: Parent State from which this state was reached,
                or None if this is the initial state.
        """
        self.hub = hub
        self.turn = turn
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent


def reverse_dijkstra(
    end_hub: Hub, all_hubs: List[Hub]
) -> Dict[str, float]:
    """Computes shortest distances from every hub to the end hub.

    Runs Dijkstra in reverse (from end_hub outward) to produce a
    lookup table used as the A* heuristic. Blocked hubs are skipped.
    Zone-based movement costs are applied:
        - "restricted": cost 2.0
        - "priority":   cost 0.5
        - otherwise:    cost 1.0

    Args:
        end_hub: The destination hub (start of the reverse search).
        all_hubs: Complete list of hubs in the graph.

    Returns:
        A dict mapping each hub name to its minimum travel cost to
        reach end_hub. Unreachable hubs map to float("inf").
    """
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
    """Reconstructs the full path by walking parent links back to root.

    Args:
        current: The goal State from which the path is traced backward.

    Returns:
        An ordered list of (Hub, turn) pairs from start to goal.
    """
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
    """Checks whether a hub has available capacity at a given turn.

    The start and end hubs are always considered free (no capacity
    restriction applied at the origin or the destination).

    Args:
        hub: The hub to check.
        turn: The simulation turn to check capacity for.
        reservations: Current reservation counts keyed by
            (hub_name, turn) or ((h1, h2), turn).
        start: Name of the start hub (always allowed).
        end: Name of the end hub (always allowed).

    Returns:
        True if the hub can accept one more drone at that turn,
        False if it is already at full capacity.
    """
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
    """Checks whether the link between two hubs is free at a given turn.

    The link key is a sorted tuple of hub names to guarantee consistency
    regardless of traversal direction.

    Args:
        h1: First hub of the connection.
        h2: Second hub of the connection.
        turn: The simulation turn at which to check link occupancy.
        reservations: Current reservation counts keyed by
            (hub_name, turn) or ((h1, h2), turn).
        link_capacity: Maximum concurrent drones per link, keyed by
            sorted (name1, name2) tuple.

    Returns:
        True if the link can accept one more drone at that turn,
        False if it is at full capacity.
    """
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
    """Finds the optimal time-expanded path from start to end for one drone.

    Implements a space-time A* search where each state is (hub, turn).
    The heuristic is the pre-computed reverse-Dijkstra cost to the goal.
    The drone may wait at its current hub (cost 1.0, turn +1) or move to
    a neighbor. Blocked hubs are skipped. Zone costs are:
        - "restricted": move_cost 2.0, arrival_turn +2
        - "priority":   move_cost 0.5, arrival_turn +1
        - "normal":     move_cost 1.0, arrival_turn +1

    Args:
        start: The hub where the drone begins.
        end: The target hub the drone must reach.
        reservations: Shared reservation table updated by previously
            scheduled drones (modified in-place by the caller).
        link_capacity: Maximum concurrent drones per link.
        true_distances: Reverse-Dijkstra costs from every hub to end,
            used as the admissible heuristic.
        max_turn: Hard cap on the number of simulation turns to explore
            (default: 500).

    Returns:
        An ordered list of (Hub, turn) pairs describing the drone's path
        including wait states, or an empty list if no path was found.
    """
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
    """Runs the cooperative A* planner for the entire drone fleet.

    For each drone in turn, computes an A* path from the shared start hub
    to the end hub, respecting reservations already made by earlier drones.
    After planning, it populates the schedule dict and prints the
    turn-by-turn output in the required format (D<ID>-<zone> per turn).

    The optional ``--capacity-info`` CLI flag prints per-turn link and zone
    capacity usage alongside the regular output.

    Args:
        scren: The Screen instance holding the parsed map data
            (setting_maps) and the drone fleet (control_drones).

    Raises:
        AssertionError: If scren.setting_maps, scren.control_drones,
            or the start/end hub are None.
    """
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
