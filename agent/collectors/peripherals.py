import win32com.client


def get_peripherals():
    """
    Collect currently detected keyboards, pointing devices,
    printers, and projectors/displays.
    """

    wmi = win32com.client.GetObject("winmgmts:")

    peripherals = []

    # =========================================================
    # KEYBOARDS
    # =========================================================

    for device in wmi.InstancesOf("Win32_Keyboard"):

        peripherals.append({
            "device_type": "keyboard",
            "name": device.Name,
            "device_id": device.DeviceID,
            "status": device.Status,
            "is_virtual": False,
        })

    # =========================================================
    # POINTING DEVICES
    # =========================================================

    for device in wmi.InstancesOf("Win32_PointingDevice"):

        name = (device.Name or "").lower()
        device_id = (device.DeviceID or "").lower()

        touchpad_keywords = [
            "touchpad",
            "clickpad",
            "trackpad",
            "elan",
            "synaptics",
            "precision touchpad",
        ]

        is_touchpad = any(
            keyword in name or keyword in device_id
            for keyword in touchpad_keywords
        )

        device_type = "touchpad" if is_touchpad else "mouse"

        peripherals.append({
            "device_type": device_type,
            "name": device.Name,
            "device_id": device.DeviceID,
            "status": device.Status,
            "is_virtual": False,
        })

    # =========================================================
    # PRINTERS
    # =========================================================

    for device in wmi.InstancesOf("Win32_Printer"):

        name = (device.Name or "").lower()

        virtual_printer_keywords = [
            "microsoft print to pdf",
            "microsoft xps document writer",
            "onenote",
            "fax",
            "dopdf",
            "pdf",
            "xps",
        ]

        is_virtual = any(
            keyword in name
            for keyword in virtual_printer_keywords
        )

        printer_type = (
            "virtual_printer"
            if is_virtual
            else "physical_printer"
        )

        status = (
            "offline"
            if device.WorkOffline
            else "online"
        )

        peripherals.append({
            "device_type": printer_type,
            "name": device.Name,
            "device_id": device.DeviceID,
            "status": status,
            "is_virtual": is_virtual,
        })

    
    return peripherals


if __name__ == "__main__":

    peripherals = get_peripherals()

    print("Detected Peripherals:\n")

    for peripheral in peripherals:
        print(peripheral)

