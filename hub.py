from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from drone import Drone


class Hub:
    """Represents a zone/hub node in the drone routing network.

    Each hub has a position, optional capacity limits, a zone type,
    and maintains the list of drones currently occupying it.

    Attributes:
        name: Unique identifier for this hub.
        x: Horizontal coordinate on the map grid.
        y: Vertical coordinate on the map grid.
        color: Display color used for rendering (default: "black").
        max_drones: Maximum number of drones allowed simultaneously,
            or None if unlimited.
        zone: Zone type affecting movement cost and rules.
            One of "normal", "blocked", "restricted", "priority".
        neighbors: Adjacent hubs directly connected to this one.
        current_drones: Drones currently located at this hub.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str = "black",
        max_drones: Optional[int] = None,
        zone: str = "normal",
    ) -> None:
        """Initializes a Hub with position, visual and zone properties.

        Args:
            name: Unique name identifying the hub.
            x: X-axis coordinate on the map.
            y: Y-axis coordinate on the map.
            color: Color used when rendering the hub (default: "black").
            max_drones: Maximum concurrent drones allowed, or None for
                no limit.
            zone: Zone classification. Accepted values are "normal",
                "blocked", "restricted", "priority" (default: "normal").
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y

        self.color: str = color
        self.max_drones: Optional[int] = max_drones
        self.zone: str = zone

        self.neighbors: list[Hub] = []
        self.current_drones: list[Drone] = []

    def get_pos(self) -> tuple[int, int]:
        """Returns the (x, y) grid position of the hub.

        Returns:
            A tuple (x, y) representing the hub's coordinates.
        """
        return (self.x, self.y)

    def remove_drone_hub(self, drone: Drone) -> None:
        """Removes a drone from the hub's occupancy list if present.

        Args:
            drone: The drone instance to remove.
        """
        if drone in self.current_drones:
            self.current_drones.remove(drone)

    def add_drone_hub(self, drone: Drone) -> None:
        """Registers a drone as occupying this hub if not already there.

        Args:
            drone: The drone instance to add.
        """
        if drone not in self.current_drones:
            self.current_drones.append(drone)

    def __repr__(self) -> str:
        """Returns a developer-readable string representation of the hub.

        Returns:
            A string with the hub's name and position.
        """
        return f"Hub(name='{self.name}', pos=({self.x}, {self.y}) "
