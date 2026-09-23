import winreg


# =========================================================
# PROJECT SOFTWARE BASELINE
# =========================================================
# These are the applications that the maintenance/licensing
# system must explicitly track. Matching is intentionally based
# on aliases because Windows registry DisplayName values differ
# between installers and versions.

TRACKED_SOFTWARE = [
    {
        "required_name": "CATIA VSR20",
        "aliases": (
            ("catia", "vsr20"),
            ("catia", "v5r20"),
            ("catia", "v5 r20"),
        ),
    },
    {
        "required_name": "Autodesk 2016",
        "aliases": (
            ("autodesk", "2016"),
        ),
    },
    {
        "required_name": "AutoCAD 2016",
        "aliases": (
            ("autocad", "2016"),
        ),
    },
    {
        "required_name": "MiniTab 16",
        "aliases": (
            ("minitab", "16"),
            ("mini tab", "16"),
        ),
    },
    {
        "required_name": "SolidWorks 2016",
        "aliases": (
            ("solidworks", "2016"),
        ),
    },
    {
        "required_name": "Ansys 2025",
        "aliases": (
            ("ansys", "2025"),
        ),
    },
    {
        "required_name": "Witness",
        "aliases": (
            ("witness",),
        ),
    },
    {
        "required_name": "MATLAB 2016",
        "aliases": (
            ("matlab", "2016"),
        ),
    },
    {
        "required_name": "TORA",
        "aliases": (
            ("tora",),
        ),
    },
    {
        "required_name": "POM",
        "aliases": (
            ("pom",),
        ),
    },
    {
        "required_name": "Word 2016",
        "aliases": (
            ("microsoft word", "2016"),
            ("word", "2016"),
        ),
    },
    {
        "required_name": "Project 2016",
        "aliases": (
            ("microsoft project", "2016"),
            ("project", "2016"),
        ),
    },
]


UNINSTALL_PATHS = [
    (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    ),
    (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ),
    (
        winreg.HKEY_CURRENT_USER,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    ),
]


def read_registry_value(key, value_name):
    try:
        value, _ = winreg.QueryValueEx(key, value_name)
        return value
    except (FileNotFoundError, OSError):
        return None


def get_installed_software():
    """
    Detect all software registered in Windows.

    The complete inventory is still returned. Tracked-project
    software is identified separately by get_tracked_software().
    """

    software_list = []

    for root, path in UNINSTALL_PATHS:
        try:
            main_key = winreg.OpenKey(root, path)
        except OSError:
            continue

        try:
            number_of_subkeys = winreg.QueryInfoKey(main_key)[0]

            for index in range(number_of_subkeys):
                try:
                    subkey_name = winreg.EnumKey(main_key, index)
                    subkey = winreg.OpenKey(main_key, subkey_name)
                except OSError:
                    continue

                try:
                    name = read_registry_value(subkey, "DisplayName")
                    if not name:
                        continue

                    version = read_registry_value(
                        subkey,
                        "DisplayVersion",
                    )
                    publisher = read_registry_value(
                        subkey,
                        "Publisher",
                    )
                    install_date = read_registry_value(
                        subkey,
                        "InstallDate",
                    )
                    install_location = read_registry_value(
                        subkey,
                        "InstallLocation",
                    )

                    software_list.append({
                        "name": str(name),
                        "version": (
                            str(version)
                            if version
                            else None
                        ),
                        "publisher": (
                            str(publisher)
                            if publisher
                            else None
                        ),
                        "install_date": (
                            str(install_date)
                            if install_date
                            else None
                        ),
                        "install_location": (
                            str(install_location)
                            if install_location
                            else None
                        ),
                    })

                finally:
                    try:
                        winreg.CloseKey(subkey)
                    except OSError:
                        pass

        finally:
            try:
                winreg.CloseKey(main_key)
            except OSError:
                pass

    return software_list


def remove_duplicates(software_list):
    unique = {}

    for software in software_list:
        key = (
            software["name"].lower(),
            software["version"],
            software["publisher"],
        )
        unique[key] = software

    return list(unique.values())


def _normalise(value):
    return " ".join(
        str(value or "").lower().replace("-", " ").split()
    )


def _matches_alias(name, aliases):
    value = _normalise(name)
    return all(
        token in value
        for token in aliases
    )


def find_tracked_software(software_list):
    """
    Return the project baseline with the actual installed
    registry entry when one is found.

    Important:
      found=True means the software is detected.
      It does NOT claim that the software is licensed.
    """

    results = []

    for target in TRACKED_SOFTWARE:
        matches = []

        for entry in software_list:
            name = entry.get("name")

            if any(
                _matches_alias(name, alias)
                for alias in target["aliases"]
            ):
                matches.append(entry)

        # Prefer an exact/shorter match when multiple registry
        # entries satisfy the same target.
        matches.sort(
            key=lambda item: len(
                _normalise(item.get("name"))
            )
        )

        results.append({
            "required_name": target["required_name"],
            "found": bool(matches),
            "installed": matches[0] if matches else None,
            "all_matches": matches,
        })

    return results


def get_tracked_software(software_list=None):
    if software_list is None:
        software_list = get_software_inventory()

    return find_tracked_software(software_list)


def get_software_inventory():
    software = get_installed_software()
    software = remove_duplicates(software)
    software.sort(
        key=lambda item: item["name"].lower()
    )
    return software


if __name__ == "__main__":
    software_inventory = get_software_inventory()
    tracked = get_tracked_software(software_inventory)

    print("=" * 70)
    print("INSTALLED SOFTWARE")
    print("=" * 70)
    print(f"Total software detected: {len(software_inventory)}")
    print()

    for software in software_inventory:
        print({
            "name": software["name"],
            "version": software["version"],
            "publisher": software["publisher"],
            "install_date": software["install_date"],
        })

    print()
    print("=" * 70)
    print("PROJECT SOFTWARE BASELINE")
    print("=" * 70)

    for item in tracked:
        print(
            f"{item['required_name']}: "
            f"{'DETECTED' if item['found'] else 'NOT DETECTED'}"
        )

        if item["found"]:
            print(
                f"  -> {item['installed']['name']} "
                f"{item['installed'].get('version') or ''}".strip()
            )
