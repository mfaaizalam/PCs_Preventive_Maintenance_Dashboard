import win32com.client


def get_peripherals():
    """
    Collect currently detected keyboards, pointing devices,
    printers, projectors/displays, external/portable SSDs,
    and Bluetooth speakers.
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

    # =========================================================
    # EXTERNAL / PORTABLE SSDs
    # =========================================================
    # MSFT_PhysicalDisk (Storage namespace) reports a real
    # MediaType (SSD vs HDD vs Unspecified) and BusType (USB vs
    # SATA/NVMe internal), so it's used first - it's the only
    # reliable way to tell "external" AND "SSD" apart, not just
    # external. Falls back to Win32_DiskDrive (which only knows
    # interface, not SSD vs HDD) if the Storage namespace isn't
    # available (older Windows / stripped-down builds).

    try:
        storage_wmi = win32com.client.GetObject(
            r"winmgmts:\\.\root\Microsoft\Windows\Storage"
        )

        # BusType: 7 = USB. MediaType: 4 = SSD.
        for disk in storage_wmi.InstancesOf("MSFT_PhysicalDisk"):

            is_usb = getattr(disk, "BusType", None) == 7
            is_ssd = getattr(disk, "MediaType", None) == 4

            if is_usb:
                size_bytes = getattr(disk, "Size", None)
                peripherals.append({
                    "device_type": "external_ssd" if is_ssd else "external_storage",
                    "name": disk.FriendlyName,
                    "device_id": disk.DeviceId,
                    "status": "ok" if getattr(disk, "HealthStatus", 0) == 0 else "degraded",
                    "is_virtual": False,
                    "size_gb": round(int(size_bytes) / (1024 ** 3), 1) if size_bytes else None,
                })

    except Exception:
        # Storage namespace unavailable - fall back to a
        # USB-only check (no reliable SSD/HDD distinction here).
        for disk in wmi.InstancesOf("Win32_DiskDrive"):

            interface_type = (disk.InterfaceType or "").upper()
            caption = (disk.Caption or "").lower()

            is_usb = interface_type == "USB" or "usb" in caption
            is_ssd = "ssd" in caption or "solid state" in caption

            if is_usb:
                size = getattr(disk, "Size", None)
                peripherals.append({
                    "device_type": "external_ssd" if is_ssd else "external_storage",
                    "name": disk.Caption,
                    "device_id": disk.DeviceID,
                    "status": "ok" if disk.Status == "OK" else disk.Status,
                    "is_virtual": False,
                    "size_gb": round(int(size) / (1024 ** 3), 1) if size else None,
                })

    # =========================================================
    # BLUETOOTH SPEAKERS / HEADSETS
    # =========================================================
    # Filtered to Bluetooth audio-profile devices only (A2DP /
    # Hands-Free), so paired BT mice/keyboards don't show up
    # here - those are covered by POINTING DEVICES / KEYBOARDS
    # above once Windows exposes them as HID devices.

    bt_audio_services = ("btha2dp", "bthhfenum", "bthenum")
    audio_name_keywords = [
        "speaker",
        "headphone",
        "headset",
        "earbuds",
        "soundbar",
        "audio",
    ]

    for device in wmi.InstancesOf("Win32_PnPEntity"):

        device_id = (device.DeviceID or "").upper()
        service = (device.Service or "").lower()
        name = (device.Name or "").lower()

        is_bluetooth = "BTHENUM" in device_id or service in bt_audio_services
        is_audio_like = any(keyword in name for keyword in audio_name_keywords)

        if is_bluetooth and is_audio_like:
            peripherals.append({
                "device_type": "bluetooth_speaker",
                "name": device.Name,
                "device_id": device.DeviceID,
                "status": device.Status,
                "is_virtual": False,
            })

    return peripherals


if __name__ == "__main__":

    peripherals = get_peripherals()

    print("Detected Peripherals:\n")

    for peripheral in peripherals:
        print(peripheral)