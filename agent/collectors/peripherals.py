import win32com.client


# Keywords used only to classify a display as a projector.
# Many projectors expose themselves to Windows as a normal PnP monitor,
# so the exact model name is used when Windows provides it.
PROJECTOR_KEYWORDS = (
    "projector",
    "projector display",
    "beamer",
    "epson",
    "benq",
    "viewsonic projector",
    "nec projector",
    "panasonic projector",
    "optoma",
    "hitachi projector",
    "acer projector",
    "sony projector",
)


def _safe(value):
    return str(value).strip() if value is not None else None


def _is_projector(name: str | None) -> bool:
    value = (name or "").lower()
    return any(keyword in value for keyword in PROJECTOR_KEYWORDS)


def _append_display(peripherals, seen_keys, device, source="pnp"):
    """
    Add a physical display/projector only once.

    Windows normally exposes a projector as a monitor/display. We keep the
    original PnP device id as the stable device_key so disconnect/reconnect
    can be tracked by the backend.
    """
    name = _safe(getattr(device, "Name", None))
    device_id = _safe(getattr(device, "DeviceID", None))
    pnp_class = _safe(getattr(device, "PNPClass", None))

    if not device_id and not name:
        return

    device_id = device_id or name
    key = device_id.upper()

    if key in seen_keys:
        return

    seen_keys.add(key)

    friendly_name = name or "Display"

    peripherals.append({
        "device_type": "projector" if _is_projector(friendly_name) else "monitor",
        "name": friendly_name,
        "device_id": device_id,
        "status": _safe(getattr(device, "Status", None)) or "OK",
        "is_virtual": False,
        "model": friendly_name,
        "descriptor": (
            f"Windows PnP display ({pnp_class or source})"
        ),
    })


def get_peripherals():
    """
    Collect currently detected physical peripherals.

    Includes:
      - keyboard
      - mouse / touchpad
      - monitor / projector
      - printer
      - USB storage / external SSD
      - Bluetooth audio devices

    The agent sends the current inventory every report. The agent also keeps
    a local snapshot so it can report newly connected devices immediately.
    The backend already converts previously-seen devices that disappear from
    the next inventory into DISCONNECTED/MISSING events.
    """

    wmi = win32com.client.GetObject("winmgmts:")
    peripherals = []

    # =========================================================
    # KEYBOARDS
    # =========================================================

    for device in wmi.InstancesOf("Win32_Keyboard"):
        peripherals.append({
            "device_type": "keyboard",
            "name": _safe(device.Name),
            "device_id": _safe(device.DeviceID),
            "status": _safe(device.Status) or "OK",
            "is_virtual": False,
        })

    # =========================================================
    # POINTING DEVICES
    # =========================================================

    for device in wmi.InstancesOf("Win32_PointingDevice"):
        name = (_safe(device.Name) or "").lower()
        device_id = (_safe(device.DeviceID) or "").lower()

        touchpad_keywords = (
            "touchpad",
            "clickpad",
            "trackpad",
            "elan",
            "synaptics",
            "precision touchpad",
        )

        is_touchpad = any(
            keyword in name or keyword in device_id
            for keyword in touchpad_keywords
        )

        peripherals.append({
            "device_type": "touchpad" if is_touchpad else "mouse",
            "name": _safe(device.Name),
            "device_id": _safe(device.DeviceID),
            "status": _safe(device.Status) or "OK",
            "is_virtual": False,
        })

    # =========================================================
    # MONITORS / PROJECTORS
    # =========================================================
    # Win32_PnPEntity is preferred because it gives a stable PnP DeviceID.
    # A second Win32_DesktopMonitor pass catches older Windows systems where
    # the monitor PnP class is not exposed cleanly.

    display_keys = set()

    try:
        for device in wmi.InstancesOf("Win32_PnPEntity"):
            pnp_class = (_safe(getattr(device, "PNPClass", None)) or "").lower()
            name = _safe(getattr(device, "Name", None)) or ""

            if pnp_class == "monitor":
                _append_display(
                    peripherals,
                    display_keys,
                    device,
                    source="pnp",
                )

            # Some projectors/drivers do not report PNPClass=Monitor.
            if _is_projector(name):
                _append_display(
                    peripherals,
                    display_keys,
                    device,
                    source="projector-detection",
                )
    except Exception:
        # Display collection should never stop the rest of the agent.
        pass

    try:
        for device in wmi.InstancesOf("Win32_DesktopMonitor"):
            _append_display(
                peripherals,
                display_keys,
                device,
                source="desktop-monitor",
            )
    except Exception:
        pass

    # =========================================================
    # PRINTERS
    # =========================================================

    for device in wmi.InstancesOf("Win32_Printer"):
        name = (_safe(device.Name) or "").lower()

        virtual_printer_keywords = (
            "microsoft print to pdf",
            "microsoft xps document writer",
            "onenote",
            "fax",
            "dopdf",
            "pdf",
            "xps",
        )

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
            if bool(getattr(device, "WorkOffline", False))
            else "online"
        )

        peripherals.append({
            "device_type": printer_type,
            "name": _safe(device.Name),
            "device_id": _safe(device.DeviceID),
            "status": status,
            "is_virtual": is_virtual,
        })

    # =========================================================
    # EXTERNAL / PORTABLE STORAGE
    # =========================================================

    try:
        storage_wmi = win32com.client.GetObject(
            r"winmgmts:\\.\root\Microsoft\Windows\Storage"
        )

        # BusType 7 = USB, MediaType 4 = SSD.
        for disk in storage_wmi.InstancesOf("MSFT_PhysicalDisk"):
            is_usb = getattr(disk, "BusType", None) == 7
            is_ssd = getattr(disk, "MediaType", None) == 4

            if is_usb:
                size_bytes = getattr(disk, "Size", None)

                peripherals.append({
                    "device_type": (
                        "external_ssd"
                        if is_ssd
                        else "external_storage"
                    ),
                    "name": _safe(getattr(disk, "FriendlyName", None)),
                    "device_id": _safe(getattr(disk, "DeviceId", None)),
                    "status": (
                        "ok"
                        if getattr(disk, "HealthStatus", 0) == 0
                        else "degraded"
                    ),
                    "is_virtual": False,
                    "size_gb": (
                        round(int(size_bytes) / (1024 ** 3), 1)
                        if size_bytes
                        else None
                    ),
                })

    except Exception:
        # Older Windows fallback.
        for disk in wmi.InstancesOf("Win32_DiskDrive"):
            interface_type = (
                _safe(getattr(disk, "InterfaceType", None)) or ""
            ).upper()
            caption = (
                _safe(getattr(disk, "Caption", None)) or ""
            ).lower()

            is_usb = (
                interface_type == "USB"
                or "usb" in caption
            )
            is_ssd = (
                "ssd" in caption
                or "solid state" in caption
            )

            if is_usb:
                size = getattr(disk, "Size", None)

                peripherals.append({
                    "device_type": (
                        "external_ssd"
                        if is_ssd
                        else "external_storage"
                    ),
                    "name": _safe(getattr(disk, "Caption", None)),
                    "device_id": _safe(getattr(disk, "DeviceID", None)),
                    "status": (
                        "ok"
                        if _safe(getattr(disk, "Status", None)) == "OK"
                        else _safe(getattr(disk, "Status", None))
                    ),
                    "is_virtual": False,
                    "size_gb": (
                        round(int(size) / (1024 ** 3), 1)
                        if size
                        else None
                    ),
                })

    # =========================================================
    # BLUETOOTH SPEAKERS / HEADSETS
    # =========================================================

    bt_audio_services = ("btha2dp", "bthhfenum", "bthenum")
    audio_name_keywords = (
        "speaker",
        "headphone",
        "headset",
        "earbuds",
        "soundbar",
        "audio",
    )

    for device in wmi.InstancesOf("Win32_PnPEntity"):
        device_id = (_safe(device.DeviceID) or "").upper()
        service = (_safe(device.Service) or "").lower()
        name = (_safe(device.Name) or "").lower()

        is_bluetooth = (
            "BTHENUM" in device_id
            or service in bt_audio_services
        )
        is_audio_like = any(
            keyword in name
            for keyword in audio_name_keywords
        )

        if is_bluetooth and is_audio_like:
            peripherals.append({
                "device_type": "bluetooth_speaker",
                "name": _safe(device.Name),
                "device_id": _safe(device.DeviceID),
                "status": _safe(device.Status) or "OK",
                "is_virtual": False,
            })

    return peripherals


if __name__ == "__main__":
    peripherals = get_peripherals()

    print("Detected Peripherals:\n")

    for peripheral in peripherals:
        print(peripheral)
