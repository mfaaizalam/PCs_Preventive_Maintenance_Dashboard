import winreg


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
    """
    Safely read a value from Windows Registry.
    """

    try:
        value, _ = winreg.QueryValueEx(key, value_name)
        return value

    except (FileNotFoundError, OSError):
        return None


def get_installed_software():
    """
    Detect ALL software registered in Windows.

    No software names are hard-coded.

    Returns:
        list[dict]
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
                    subkey_name = winreg.EnumKey(
                        main_key,
                        index
                    )

                    subkey = winreg.OpenKey(
                        main_key,
                        subkey_name
                    )

                except OSError:
                    continue

                try:
                    name = read_registry_value(
                        subkey,
                        "DisplayName"
                    )

                    # Ignore registry entries without a software name
                    if not name:
                        continue

                    version = read_registry_value(
                        subkey,
                        "DisplayVersion"
                    )

                    publisher = read_registry_value(
                        subkey,
                        "Publisher"
                    )

                    install_date = read_registry_value(
                        subkey,
                        "InstallDate"
                    )

                    install_location = read_registry_value(
                        subkey,
                        "InstallLocation"
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
    """
    Remove duplicate software entries.

    Same software can appear in both:
    32-bit and 64-bit registry locations.
    """

    unique = {}

    for software in software_list:

        key = (
            software["name"].lower(),
            software["version"]
        )

        unique[key] = software

    return list(unique.values())


def get_software_inventory():
    """
    Return complete software inventory for this PC.
    """

    software = get_installed_software()

    software = remove_duplicates(software)

    software.sort(
        key=lambda item: item["name"].lower()
    )

    return software


if __name__ == "__main__":

    software_inventory = get_software_inventory()

    print("=" * 70)
    print("INSTALLED SOFTWARE")
    print("=" * 70)

    print(
        f"Total software detected: "
        f"{len(software_inventory)}"
    )

    print()

    for software in software_inventory:

        print({
            "name": software["name"],
            "version": software["version"],
            "publisher": software["publisher"],
            "install_date": software["install_date"],
        })