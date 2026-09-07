from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from hub import Hub

if TYPE_CHECKING:
    from drone import ControlDrone

def split_check_format(hub: str, separateur: str) -> list[str]:
    new_tab: list[str] = []
    temp = ""
    dans_crochets = False
    hub = hub.strip()
    for char in hub:
        if char == "[":
            dans_crochets = True
        elif char == "]":
            dans_crochets = False
        if char == separateur and not dans_crochets:
            new_tab.append(temp)
            temp = ""
        else:
            temp += char
    if "[" in hub and "]" in hub:
        new_tab.append(temp)
    if "[" not in hub and "]" not in hub:
        new_tab.append("[color=black]")
    return new_tab


def check_format_hub(hub: str) -> None:
    if "[" in hub and "]" in hub:
        main_part, options_part = hub.split("[", 1)
        options_str = options_part.rstrip("]").strip()
    else:
        main_part = hub
        options_str = ""

    tokens = main_part.split()
    if len(tokens) != 4:
        raise ValueError(
            f"[Error] Hub definition expects 3 fields (name x y), got {len(tokens) - 1}: {tokens}"
        )

    try:
        int(tokens[2])
    except ValueError:
        raise ValueError(f"[Error] Hub X coordinate must be an integer, got '{tokens[2]}'")

    try:
        int(tokens[3])
    except ValueError:
        raise ValueError(f"[Error] Hub Y coordinate must be an integer, got '{tokens[3]}'")

    if options_str:
        for item in options_str.split():
            split_opt = item.split("=")
            if len(split_opt) != 2:
                raise ValueError(f"[Error] Malformed hub option '{item}' — expected key=value")
            key, value = split_opt[0], split_opt[1]
            if key not in ("color", "max_drones", "zone"):
                raise ValueError(f"[Error] Unknown hub option '{key}'")
            if key == "color" and (not value or len(value.split()) != 1):
                raise ValueError(f"[Error] 'color' must be a single word, got '{value}'")

    
def check_double(
    files: list[str], check_double1: str, check_double2: str
) -> list[int]:
    res1: int = 0
    res2: int = 0
    prefix1 = f"{check_double1}:"
    prefix2 = f"{check_double2}:"

    for line in files:
        if line.startswith(prefix1):
            res1 += 1
        if line.startswith(prefix2):
            res2 += 1

    if res1 != 1:
        raise ValueError(
            f"[Error] Expected exactly 1 '{check_double1}' definition, found {res1}"
        )
    if res2 != 1 and len(check_double2) != 0:
        raise ValueError(
            f"[Error] Expected exactly 1 '{check_double2}' definition, found {res2}"
        )
    return [res1, res2]



def open_files(path_file: str) -> str:
    files = ""
    with open(path_file) as f:
        files_read = str(f.read())
        if len(files_read) == 0:
            raise ValueError(
                f"[Error] This file ({path_file}) is empty"
            )
        name_file = f.name.split("/")[-1]
        files += name_file
        files += "\n"
        files += files_read
        return files


class ParsingFiles:
    def __init__(self, file_split: list[str]) -> None:
        self.file_split = file_split
        self.nb_drone: int = 0
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None
        self.hub: list[Hub] = []
        self.all_name_hub: list[str] = []
        self.name_file: str = file_split[0]
        self.connection: dict[int, dict[int, list[str]]] = {}
        self.nb_drone_check()
        self.hub_check()
        self.create_connection()

        self.create_neightbord()
        self.path_to_exit: list[Hub] = []
        self.control_drone: ControlDrone
        from drone import ControlDrone as _ControlDrone
        self.control_drone = _ControlDrone(self)

    def create_neightbord(self) -> None:
        assert self.start_hub is not None
        assert self.end_hub is not None
        all_hubs = {h.name: h for h in self.hub}
        all_hubs[self.start_hub.name] = self.start_hub
        all_hubs[self.end_hub.name] = self.end_hub
        for conn in self.connection.values():
            connection_names = list(conn.values())[0]
            if len(connection_names) >= 2:
                name1 = connection_names[0].strip()
                name2 = connection_names[1].split()[0].strip()
                if name1 in all_hubs and name2 in all_hubs:
                    hub1 = all_hubs[name1]
                    hub2 = all_hubs[name2]
                    if hub2 not in hub1.neighbors:
                        hub1.neighbors.append(hub2)
                    if hub1 not in hub2.neighbors:
                        hub2.neighbors.append(hub1)

    def nb_drone_check(self) -> None:
        for line in self.file_split:
            if "nb_drone" in line:
                line_split = line.split(":")
                if len(line_split) != 2:
                    raise ValueError(
                        f"[Error] 'nb_drone' line must use format"
                        f" 'nb_drone:<number>', got: '{line}'"
                    )
                try:
                    if line_split[1]:
                        self.nb_drone = int(line_split[1])
                except ValueError:
                    raise ValueError(
                        f"[Error] 'nb_drone' value must be a positive"
                        f" integer, got: '{line_split[1].strip()}'"
                    )
                if int(line_split[1]) < 0:
                    raise ValueError(
                        f"[Error] 'nb_drone' value must be strictly"
                        f" positive, got: {line_split[1]}"
                    )
        if self.nb_drone == 0:
            raise ValueError(
                "[Error] No 'nb_drone' field found or value is 0"
                " — at least 1 drone required"
            )

    def check_connection(self) -> None:
        assert self.start_hub is not None
        assert self.end_hub is not None
        all_name_connection: list[str] = []
        self.all_name_hub.append(self.start_hub.name)
        self.all_name_hub.append(self.end_hub.name)
        seen_pairs: set[tuple[str, ...]] = set()
        for hub_name in self.hub:
            self.all_name_hub.append(hub_name.name)
        for connection_name_for in self.connection.values():
            connection_name = list(connection_name_for.values())[0]
            if len(connection_name) != 2:
                raise ValueError(
                    f"[Error] Connection must link exactly 2 hubs,"
                    f" got: {connection_name}"
                )
            pair = tuple(sorted(connection_name))
            if pair in seen_pairs:
                raise ValueError(
                    f"[Error] Duplicate connection forbidden between"
                    f" '{connection_name[0]}' and '{connection_name[1]}'"
                )
            if connection_name[0] == connection_name[1]:
                raise ValueError(
                    f"[Error] Self-loop forbidden: hub"
                    f" '{connection_name[0]}' cannot connect to itself"
                )
            seen_pairs.add(pair)
            all_name_connection.append(connection_name[0])
            all_name_connection.append(connection_name[1].split()[0])
        for connection in all_name_connection:
            if (
                connection not in self.all_name_hub
                and "max_link_capacity=" not in connection
            ):
                raise ValueError(
                    f"[Error] Connection references unknown hub"
                    f" '{connection}' — not declared in map"
                )
        if self.start_hub.name not in all_name_connection:
            raise ValueError(
                f"[Error] The start hub '{self.start_hub.name}'"
                f" is isolated (has no connections)."
            )

        if self.end_hub.name not in all_name_connection:
            raise ValueError(
                f"[Error] The end hub '{self.end_hub.name}'"
                f" is isolated (has no connections)."
            )

    def create_connection(self) -> None:
        i = 0
        for line in self.file_split:
            if line.startswith("connection: "):
                try:
                    content = line.split("connection:", 1)[1].strip()
                    max_lint = 0
                    if "max_link_capacity" in content:
                        max_lint = int(
                            content
                            .split("max_link_capacity=")[1]
                            .split()[0]
                            .strip("]")
                        )
                        if max_lint < 1:
                            raise ValueError(
                                f"[Error] max_link_capacity must be"
                                f" >= 1, got: {max_lint}"
                            )
                        if "[" in content:
                            bracket_content = (
                                content.split("[")[1].split("]")[0]
                            )
                            for item in bracket_content.split():
                                if "=" in item:
                                    key = item.split("=")[0]
                                    if key != "max_link_capacity":
                                        raise ValueError(
                                            f"[Error] Unknown connection"
                                            f" option '{key}' — only"
                                            f" 'max_link_capacity'"
                                            f" is allowed"
                                        )
                    else:
                        max_lint = 1
                    self.connection.update(
                        {i: {max_lint: content.split("-")}}
                    )
                except Exception:
                    raise ValueError(
                        f"[Error] Invalid connection syntax:"
                        f" '{line.strip()}'"
                    )
                i += 1
        self.check_connection()

    def hub_check(self) -> None:
        assert self.start_hub is None or self.start_hub is not None
        i = 0
        for line in self.file_split:
            if "start_hub:" in line:
                self.start_hub = hub_good_format(line)
            if "end_hub:" in line:
                self.end_hub = hub_good_format(line)
            if (
                "hub:" in line
                and "end_hub" not in line
                and "start_hub" not in line
            ):
                self.hub.append(hub_good_format(line))
                i += 1
        assert self.start_hub is not None
        assert self.end_hub is not None
        all_names = (
            [self.start_hub.name, self.end_hub.name]
            + [h.name for h in self.hub]
        )
        seen: set[str] = set()
        for name in all_names:
            if name in seen:
                raise ValueError(
                    f"[Error] Duplicate hub name '{name}'"
                    f" — each hub must have a unique name"
                )
            seen.add(name)
        all_hubs_list = [self.start_hub, self.end_hub] + self.hub
        seen_coords: set[tuple[int, int]] = set()
        for h in all_hubs_list:
            coord = (h.x, h.y)
            if coord in seen_coords:
                raise ValueError(
                    f"[Error] Duplicate coordinates ({h.x}, {h.y})"
                    f" for hub '{h.name}'"
                    f" — each hub must have unique coordinates"
                )
            seen_coords.add(coord)


def pars_file(name_file: str) -> ParsingFiles:
    files_str = open_files(name_file)
    raw_lines = files_str.split("\n")

    cleaned_lines: list[str] = [raw_lines[0]]

    for line in raw_lines[1:]:
        clean = line.split("#", 1)[0].strip()
        
        if clean:
            cleaned_lines.append(clean)

    check_double(cleaned_lines, "start_hub", "end_hub")
    for line in cleaned_lines[1:]:
        if "hub:" in line:
            check_format_hub(line)

    maps = ParsingFiles(cleaned_lines)
    return maps

def hub_good_format(line: str) -> Hub:
    content = line.split(":", 1)[1].strip()
    if "[" in content and "]" in content:
        main_part, options_part = content.split("[", 1)
        options_str = options_part.rstrip("]").strip()
    else:
        main_part = content
        options_str = ""

    tokens = main_part.split()
    name = tokens[0]
    x = int(tokens[1])
    y = int(tokens[2])
    color = "black"
    max_drones: Optional[int] = None
    zone = "normal"
    if options_str:
        for item in options_str.split():
            if "=" in item: 
                key, value = item.split("=", 1)
                if key == "color":
                    if not value or len(value.split()) != 1:
                        raise ValueError(f"[Error line ] 'color' must be a single word, got '{value}'")
                    color = value
                elif key == "max_drones":
                    try:
                        max_drones = int(value)
                    except ValueError:
                        raise ValueError(
                            f"[Error] 'max_drones' value must be an"
                            f" integer, got: '{value}'"
                        )
                    if max_drones <= 0:
                        raise ValueError(
                            f"[Error] 'max_drones' value must be strictly"
                            f" positive, got: {max_drones}"
                        )
                elif key == "zone":
                    if value not in ("normal", "blocked", "restricted", "priority"):
                        raise ValueError(
                            f"[Error] Invalid zone type '{value}' — allowed: normal, blocked, restricted, priority"
                        )
                    zone = value
    hub = Hub(
        name=name,
        x=x,
        y=y,
        color=color,
        max_drones=max_drones,
        zone=zone,
    )

    return hub
