from __future__ import annotations

from typing import TYPE_CHECKING

from hub import Hub

if TYPE_CHECKING:
    from parsing import ParsingFiles


class Drone:
    """Represents a single autonomous drone navigating the hub network.

    A drone starts at a given hub, follows a pre-computed path of hubs,
    and smoothly animates between positions for visual rendering.

    Attributes:
        hub_select: The hub where the drone is currently located.
        pos_x: Current horizontal pixel/grid position used for rendering.
        pos_y: Current vertical pixel/grid position used for rendering.
        path: Ordered list of hubs the drone must visit to reach the end.
        img_drone: Path to the drone sprite image file.
        name_drone: Unique string identifier for this drone (e.g. "drone_0").
        animation: Queue of interpolated (x, y) positions for smooth movement.
    """

    def __init__(self, name: str, hub_start: Hub) -> None:
        """Initializes a Drone at a starting hub.

        Registers the drone on the starting hub and sets up its initial
        position equal to that hub's coordinates.

        Args:
            name: Unique name for this drone instance (e.g. "drone_0").
            hub_start: The hub at which the drone begins its journey.
        """
        self.hub_select: Hub = hub_start
        self.pos_x: float = 0.0
        self.pos_y: float = 0.0
        self.path: list[Hub] = []
        self.img_drone = "img/drone.png"
        self.name_drone = name
        self.edit_pos(self.hub_select.get_pos())
        self.hub_select.add_drone_hub(self)
        self.animation: list[tuple[float, float]] = []

    def move_drone_to_end(self, path_to_go: list[Hub]) -> None:
        """Moves the drone sequentially through every hub in a path.

        Iterates over the provided list and calls move_to_hub for each
        hub, building up the animation queue along the way.

        Args:
            path_to_go: Ordered list of Hub objects leading to the
                destination.
        """
        for hub in path_to_go:
            self.move_to_hub(hub)

    def move_to_hub(self, hub_select_param: Hub) -> None:
        """Transfers the drone from its current hub to a target hub.

        Unregisters the drone from the current hub, registers it on the
        new hub, and queues the interpolated animation frames.

        Args:
            hub_select_param: The hub the drone moves to.
        """
        self.hub_select.remove_drone_hub(self)
        self.hub_select = hub_select_param
        self.hub_select.add_drone_hub(self)
        self.calc_animation(hub_select_param)

    def calc_animation(self, hub_select_param: Hub) -> None:
        """Computes and enqueues interpolated frames between two positions.

        Divides the movement into `step` equal increments and appends
        each intermediate (x, y) coordinate to the animation queue,
        finishing with the exact target coordinates.

        Args:
            hub_select_param: The destination hub whose coordinates are
                used to compute the animation frames.
        """
        step = 5
        hub_start_x = self.pos_x
        hub_start_y = self.pos_y
        hub_go_x = hub_select_param.x
        hub_go_y = hub_select_param.y

        dis_x = hub_go_x - hub_start_x
        dis_y = hub_go_y - hub_start_y

        jump_x = dis_x / step
        jump_y = dis_y / step

        for i in range(step):
            hub_start_x += jump_x
            hub_start_y += jump_y
            self.animation.append((hub_start_x, hub_start_y))

        self.animation.append((hub_go_x, hub_go_y))

        self.pos_x = hub_go_x
        self.pos_y = hub_go_y

    def draw_animation(self) -> int:
        """Advances the drone one animation frame if frames are pending.

        Pops the next (x, y) position from the animation queue and
        updates the drone's displayed position.

        Returns:
            1 if a frame was consumed and the position updated,
            0 if the animation queue is empty (no movement this tick).
        """
        if len(self.animation) > 0:
            self.pos_x = self.animation[0][0]
            self.pos_y = self.animation[0][1]
            del self.animation[0]
            return 1
        return 0

    def edit_pos(self, pos: tuple[int, int]) -> None:
        """Sets the drone's current position from a coordinate tuple.

        Args:
            pos: A (x, y) tuple specifying the new position.
        """
        self.pos_x = pos[0]
        self.pos_y = pos[1]

    def __repr__(self) -> str:
        """Returns a developer-readable string representation.

        Returns:
            A string showing the drone's name and current (x, y) position.
        """
        return f"name : {self.name_drone} pos: {(self.pos_x, self.pos_y)}"


class ControlDrone:
    """Manages the fleet of drones for a given simulation run.

    Reads the number of drones and the computed path from the parsed map
    data, then instantiates and stores all drone objects.

    Attributes:
        nb_drone: Total number of drones in this simulation.
        all_drone: List of all Drone instances.
        parsing: Reference to the parsed map data.
    """

    def __init__(self, parsing: ParsingFiles) -> None:
        """Initializes the drone fleet from parsed map configuration.

        Creates all drones and assigns them the pre-computed exit path.

        Args:
            parsing: A ParsingFiles instance containing nb_drone,
                start_hub, and path_to_exit.
        """
        self.nb_drone = parsing.nb_drone
        self.all_drone: list[Drone] = []
        self.parsing = parsing
        self.create_all_drone()

    def create_all_drone(self) -> None:
        """Instantiates all drones and sets their paths.

        Iterates nb_drone times, creating a named Drone at the start hub
        and assigning the shared exit path to each one.

        Raises:
            AssertionError: If parsing.start_hub is None.
        """
        assert self.parsing.start_hub is not None
        for i in range(self.nb_drone):
            drone: Drone = Drone(f"drone_{i}", self.parsing.start_hub)
            drone.path = self.parsing.path_to_exit
            self.all_drone.append(drone)
