class Hub:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str = "black",
        max_drones: int | None = None,
        zone: str = "normal"
    ):
        self.name: str = name
        self.x: int = x
        self.y: int = y

        self.color: str = color
        self.max_drones: int | None = max_drones
        self.zone: str = zone

        self.neighbors: list[Hub] = []
        self.current_drones: list = []


    def get_pos(self):
        return (self.x, self.y)

    def remove_drone_hub(self, drone):
        self.current_drones.remove(drone)

    def add_drone_hub(self, drone):
        self.current_drones.append(drone)

    def __repr__(self) -> str:
            return (
                f"Hub(name='{self.name}', pos=({self.x}, {self.y}), "
                f"zone='{self.zone}', max_drones={self.max_drones}, color='{self.color}')"
            )
