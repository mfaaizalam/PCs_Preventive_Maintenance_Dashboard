import re
import subprocess

import win32com.client


def get_windows_license():
    """
    Get the active Windows license.

    Windows contains many SoftwareLicensingProduct entries.
    We only return the licensed Windows product.
    """

    try:
        wmi = win32com.client.GetObject(
            "winmgmts:"
        )

    except Exception as exc:
        return {
            "available": False,
            "product": None,
            "license_status": "Unknown",
            "expiration_date": None,
            "error": str(exc),
        }

    try:

        for product in wmi.InstancesOf(
            "SoftwareLicensingProduct"
        ):

            name = product.Name or ""

            if "Windows" not in name:
                continue

            if product.LicenseStatus != 1:
                continue

            if not product.ApplicationID:
                continue

            expiration_date = None

            if product.ExpirationDate:

                try:
                    expiration_date = (
                        product.ExpirationDate.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )

                except AttributeError:
                    expiration_date = None

            return {
                "available": True,
                "product": name,
                "license_status": "Licensed",
                "expiration_date": expiration_date,
                "error": None,
            }

    except Exception as exc:

        return {
            "available": False,
            "product": None,
            "license_status": "Unknown",
            "expiration_date": None,
            "error": str(exc),
        }

    return {
        "available": True,
        "product": None,
        "license_status": "Unlicensed",
        "expiration_date": None,
        "error": None,
    }


def find_office_ospp():
    """
    Find Microsoft's Office licensing script.
    """

    possible_paths = [

        r"C:\Program Files\Microsoft Office\Office16\OSPP.VBS",

        r"C:\Program Files\Microsoft Office\root\Office16\OSPP.VBS",

        r"C:\Program Files (x86)\Microsoft Office\Office16\OSPP.VBS",

        r"C:\Program Files (x86)\Microsoft Office\root\Office16\OSPP.VBS",

    ]

    for path in possible_paths:

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ):
                return path

        except (FileNotFoundError, OSError):
            continue

    return None


def get_office_license():
    """
    Get Microsoft Office licensing information.

    Office does not always expose a real calendar
    expiration date. Therefore we never invent one.
    """

    ospp_path = find_office_ospp()

    if not ospp_path:

        return {
            "installed": False,
            "product": None,
            "license_status": "Not Installed",
            "expiration_date": None,
            "error": None,
        }

    try:

        result = subprocess.run(
            [
                "cscript.exe",
                "//Nologo",
                ospp_path,
                "/dstatus",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout or ""

    except (
        subprocess.SubprocessError,
        OSError,
    ) as exc:

        return {
            "installed": True,
            "product": None,
            "license_status": "Unknown",
            "expiration_date": None,
            "error": str(exc),
        }

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    product_match = re.search(
        r"LICENSE NAME:\s*(.+)",
        output,
        re.IGNORECASE,
    )

    product = (
        product_match.group(1).strip()
        if product_match
        else None
    )

    # --------------------------------------------------------
    # LICENSE STATUS
    # --------------------------------------------------------

    status_match = re.search(
        r"LICENSE STATUS:\s*(.+)",
        output,
        re.IGNORECASE,
    )

    raw_status = (
        status_match.group(1).strip()
        if status_match
        else None
    )

    if raw_status:

        upper_status = raw_status.upper()

        if "LICENSED" in upper_status:

            license_status = "Licensed"

        elif "NOTIFICATIONS" in upper_status:

            license_status = "Notification"

        elif "UNLICENSED" in upper_status:

            license_status = "Unlicensed"

        else:

            license_status = raw_status

    else:

        license_status = "Unknown"

    # --------------------------------------------------------
    # ERROR DESCRIPTION
    # --------------------------------------------------------

    error_match = re.search(
        r"ERROR DESCRIPTION:\s*(.+)",
        output,
        re.IGNORECASE,
    )

    error_description = (
        error_match.group(1).strip()
        if error_match
        else None
    )

    return {
        "installed": True,
        "product": product,
        "license_status": license_status,
        "expiration_date": None,
        "error": error_description,
    }


def get_license_info():
    """
    Collect all license-related information.
    """

    return {
        "windows": get_windows_license(),
        "office": get_office_license(),
    }


if __name__ == "__main__":

    license_info = get_license_info()

    print("=" * 70)
    print("WINDOWS LICENSE")
    print("=" * 70)

    print(license_info["windows"])

    print()

    print("=" * 70)
    print("MICROSOFT OFFICE LICENSE")
    print("=" * 70)

    print(license_info["office"])