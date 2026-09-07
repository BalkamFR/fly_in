from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from hub import Hub

if TYPE_CHECKING:
    from drone import ControlDrone


def check_format_hub(hub: str, line_no: int) -> None:
    if "[" in hub and "]" in hub:
        main_part, options_part = hub.split("[", 1)
        options_str = options_part.rstrip("]").strip()
    else:
        main_part = hub
        options_str = ""

    tokens = main_part.split()
    if len(tokens) != 4:
        raise ValueError(
            f"[Error line {line_no}] Hub definition expects"
            f" 3 fields (name x y), got"
            f" {len(tokens) - 1}: {tokens}")

    try:
        int(tokens[2])
    except ValueError:
        raise ValueError(
            f"[Error line {line_no}] Hub X coordinate"
            f" must be an integer, got '{tokens[2]}'"
        )

    try:
        int(tokens[3])
    except ValueError:
        raise ValueError(
            f"[Error line {line_no}] Hub Y coordinate"
            f" must be an integer, got '{tokens[3]}'"
        )

    if options_str:
        for item in options_str.split():
            split_opt = item.split("=")
            if len(split_opt) != 2:
                raise ValueError(
                    f"[Error line {line_no}] Malformed hub"
                    f" option '{item}' — expected key=value"
                )
            key, value = split_opt[0], split_opt[1]
            if key not in ("color", "max_drones", "zone"):
                raise ValueError(
                    f"[Error line {line_no}] Unknown hub option '{key}'")
            if key == "color" and (not value or len(value.split()) != 1):
                raise ValueError(
                    f"[Error line {line_no}] 'color' must"
                    f" be a single word, got '{value}'"
                )


def check_double(
    files: list[str], check_double1: str, check_double2: str
) -> list[int]:
    res1: int = 0
    res2: int = 0
    prefix1 = f"{check_double1}:"
    prefix2 = f"{check_double2}:"
    i = 0
    for line in files:
        if line.startswith(prefix1):
            res1 += 1
        if line.startswith(prefix2):
            res2 += 1
        if res1 > 1:
            raise ValueError(
                f"[Error line {i}] Expected exactly 1"
                f" '{check_double1}' definition, found {res1}"
            )
        if res2 > 1 and len(check_double2) != 0:
            raise ValueError(
                f"[Error line {i}] Expected exactly 1"
                f" '{check_double2}' definition, found {res2}"
            )
        i += 1
    if res1 == 0:
        raise ValueError(f"[Error] Missing '{check_double1}:' definition")
    if res2 == 0 and len(check_double2) != 0:
        raise ValueError(f"[Error] Missing '{check_double2}:' definition")
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
        self.link_capacity: dict[tuple[str, str], int] = {}
        self.nb_drone_check()
        self.hub_check()
        self.create_connection()
        self.create_neightbord()
        self.path_to_exit: list[Hub] = []
        self.control_drone: ControlDrone = self._init_control_drone()

    def _init_control_drone(self) -> ControlDrone:
        from drone import ControlDrone as _ControlDrone
        return _ControlDrone(self)

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
        found = False
        line_no = 0
        for line in self.file_split[1:]:
            line_no += 1
            if not line:
                continue
            if line.startswith("nb_drone:") or line.startswith("nb_drones:"):
                if found:
                    raise ValueError(
                        f"[Error line {line_no}] Duplicate"
                        f" 'nb_drones' definition — only 1 allowed"
                    )
                found = True

                line_split = line.split(":")
                if len(line_split) != 2 or not line_split[1].strip():
                    raise ValueError(
                        f"[Error line {line_no}] 'nb_drone'"
                        f" line must use format 'nb_drone:<number>'"
                    )
                try:
                    val = int(line_split[1].strip())
                except ValueError:
                    raise ValueError(
                        f"[Error line {line_no}] 'nb_drone' value"
                        f" must be a positive integer, got:"
                        f" '{line_split[1].strip()}'"
                    )
                if val <= 0:
                    raise ValueError(
                        f"[Error line {line_no}] 'nb_drone' value"
                        f" must be strictly positive, got: {val}"
                    )
                self.nb_drone = val

        if not found:
            raise ValueError(
                "[Error] No 'nb_drone' field found — at least 1 drone required"
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
        conn_idx = 0
        line_no = 0
        seen_pairs = set()
        assert self.start_hub is not None
        assert self.end_hub is not None
        declared = {
            h.name for h in self.hub
        }.union({
            self.start_hub.name,
            self.end_hub.name,
        })
        for line in self.file_split[1:]:
            line_no += 1
            if not line:
                continue

            if line.startswith("connection:"):
                content = line.split("connection:", 1)[1].strip()
                if not content:
                    raise ValueError(
                        f"[Error line {line_no}] Empty connection definition"
                    )

                if "[" in content:
                    if not content.endswith("]"):
                        raise ValueError(
                            f"[Error line {line_no}] Connection"
                            f" options must be enclosed in brackets '[]'"
                        )
                    main_part, bracket_part = content.split("[", 1)
                    opt_str = bracket_part.rstrip("]").strip()
                else:
                    main_part = content
                    opt_str = ""

                nodes = main_part.split("-")
                if len(nodes) != 2:
                    raise ValueError(
                        f"[Error line {line_no}] Connection must"
                        f" link exactly 2 hubs, got:"
                        f" '{main_part.strip()}'"
                    )

                n1 = nodes[0].strip()
                n2 = nodes[1].strip()
                if n1 not in declared:
                    raise ValueError(
                        f"[Error line {line_no}] Connection"
                        f" references unknown hub '{n1}'"
                        f" — not declared in map"
                    )
                if n2 not in declared:
                    raise ValueError(
                        f"[Error line {line_no}] Connection"
                        f" references unknown hub '{n2}'"
                        f" — not declared in map"
                    )
                if n1 == n2:
                    raise ValueError(
                        f"[Error line {line_no}] Self-loop forbidden:"
                        f" hub '{n1}' cannot connect to itself"
                    )
                if not n1 or not n2:
                    raise ValueError(
                        f"[Error line {line_no}] Hub names"
                        f" in connection cannot be empty"
                    )
                pair = tuple(sorted([n1, n2]))
                if pair in seen_pairs:
                    raise ValueError(
                        f"[Error line {line_no}] Duplicate connection"
                        f" forbidden between '{n1}' and '{n2}'"
                    )
                seen_pairs.add(pair)

                max_lint = 1
                if opt_str:
                    for item in opt_str.split():
                        if "=" not in item:
                            raise ValueError(
                                f"[Error line {line_no}] Malformed"
                                f" connection option '{item}'"
                                f" — expected key=value"
                            )
                        key, value = item.split("=", 1)
                        if key != "max_link_capacity":
                            raise ValueError(
                                f"[Error line {line_no}] Unknown"
                                f" connection option '{key}' — only"
                                f" 'max_link_capacity' is allowed"
                            )
                        try:
                            max_lint = int(value)
                        except ValueError:
                            raise ValueError(
                                f"[Error line {line_no}]"
                                f" 'max_link_capacity' must be"
                                f" an integer, got: '{value}'"
                            )
                        if max_lint < 1:
                            raise ValueError(
                                f"[Error line {line_no}]"
                                f" 'max_link_capacity' must be"
                                f" >= 1, got: {max_lint}"
                            )

                self.connection.update({conn_idx: {max_lint: [n1, n2]}})
                link_key = (
                    min(n1, n2), max(n1, n2)
                )
                self.link_capacity[link_key] = max_lint
                conn_idx += 1

        self.check_connection()

    def hub_check(self) -> None:
        i = 0
        for line in self.file_split:
            if line.startswith("start_hub:"):
                self.start_hub = hub_good_format(line, i)

            elif line.startswith("end_hub:"):
                self.end_hub = hub_good_format(line, i)
            elif line.startswith("hub:"):
                self.hub.append(hub_good_format(line, i))
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
        cleaned_lines.append(clean)

    check_double(cleaned_lines, "start_hub", "end_hub")
    valide_prefix = (
        "nb_drone:",
        "nb_drones:",
        "start_hub:",
        "end_hub:",
        "hub:",
        "connection:")
    for line_no, line in enumerate(cleaned_lines[1:], start=1):
        if not line:
            continue
        if not any(line.startswith(p) for p in valide_prefix):
            raise ValueError(
                f"[Error line {line_no}] Unknown directive"
                f" or syntax error: '{line}'"
            )
        if any(line.startswith(p) for p in (
            "start_hub:", "end_hub:", "hub:"
        )):
            check_format_hub(line, line_no)
    maps = ParsingFiles(cleaned_lines)
    return maps


def hub_good_format(line: str, line_no: int) -> Hub:
    content = line.split(":", 1)[1].strip()
    if "[" in content and "]" in content:
        main_part, options_part = content.split("[", 1)
        options_str = options_part.rstrip("]").strip()
    else:
        main_part = content
        options_str = ""
    tokens = main_part.split()
    name = tokens[0]
    if "-" in name:
        raise ValueError(
            f"[Error line {line_no}] Hub name '{name}'"
            f" cannot contain dashes ('-')"
        )
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
                        raise ValueError(
                            f"[Error line {line_no}] 'color'"
                            f" must be a single word, got '{value}'"
                        )
                    color = value
                elif key == "max_drones":
                    if not value.isdigit() or int(value) <= 0:
                        raise ValueError(
                            f"[Error line {line_no}] 'max_drones'"
                            f" value must be strictly positive,"
                            f" got: '{value}'"
                        )
                    max_drones = int(value)
                elif key == "zone":
                    if value not in (
                        "normal",
                        "blocked",
                        "restricted",
                            "priority"):
                        raise ValueError(
                            f"[Error line {line_no}] Invalid zone"
                            f" type '{value}' — allowed:"
                            f" normal, blocked, restricted, priority"
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
