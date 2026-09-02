from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from drone import Drone


class Hub:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str = "black",
        max_drones: Optional[int] = None,
        zone: str = "normal",
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y

        self.color: str = color
        self.max_drones: Optional[int] = max_drones
        self.zone: str = zone

        self.neighbors: list[Hub] = []
        self.current_drones: list[Drone] = []

    def get_pos(self) -> tuple[int, int]:
        return (self.x, self.y)

    def remove_drone_hub(self, drone: Drone) -> None:
        if drone in self.current_drones:
            self.current_drones.remove(drone)

    def add_drone_hub(self, drone: Drone) -> None:
        if drone not in self.current_drones:
            self.current_drones.append(drone)

    def __repr__(self) -> str:
        return f"Hub(name='{self.name}', pos=({self.x}, {self.y}) "
