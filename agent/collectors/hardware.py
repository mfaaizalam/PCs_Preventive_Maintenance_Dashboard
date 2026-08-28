import json
import subprocess

import psutil
import wmi
import logging

logger = logging.getLogger(__name__)

# ============================================================
# RAM
# ============================================================

def get_ram_info():
    """
    Collect physical RAM module information.
    """

    ram_modules = []

    try:
        computer = wmi.WMI()

        for ram in computer.Win32_PhysicalMemory():

            capacity_gb = None

            if ram.Capacity:
                capacity_gb = round(
                    int(ram.Capacity) / (1024 ** 3),
                    2
                )

            ram_modules.append({
                "slot": ram.DeviceLocator,
                "capacity_gb": capacity_gb,
                "manufacturer": ram.Manufacturer,
                "part_number": ram.PartNumber,
                "speed_mhz": ram.Speed,
            })

    except Exception as exc:
        print(f"RAM collection error: {exc}")

    return ram_modules


# ============================================================
# STORAGE SPACE
# ============================================================

def get_disk_usage():
    """
    Collect usage information for Windows drives.
    """

    disks = []

    try:

        partitions = psutil.disk_partitions()

        for partition in partitions:

            # Only process local Windows drives
            if "fixed" not in partition.opts.lower():
                continue

            try:
                usage = psutil.disk_usage(partition.mountpoint)

                disks.append({
                    "drive": partition.mountpoint,
                    "total_gb": round(
                        usage.total / (1024 ** 3),
                        2
                    ),
                    "used_gb": round(
                        usage.used / (1024 ** 3),
                        2
                    ),
                    "free_gb": round(
                        usage.free / (1024 ** 3),
                        2
                    ),
                    "usage_percent": usage.percent,
                })

            except OSError:
                continue

    except Exception as exc:
        print(f"Disk usage collection error: {exc}")

    return disks


# ============================================================
# PHYSICAL STORAGE
# ============================================================

def get_storage_info():
    """
    Collect physical storage device information.
    """

    storage_devices = []

    try:

        computer = wmi.WMI()

        for disk in computer.Win32_DiskDrive():

            size_gb = None

            if disk.Size:

                size_gb = round(
                    int(disk.Size) / (1024 ** 3),
                    2
                )

            model = disk.Model or ""

            model_upper = model.upper()

            if "SSD" in model_upper:
                media_type = "SSD"

            elif "HDD" in model_upper:

                media_type = "HDD"

            else:

                media_type = "Unknown"

            storage_devices.append({

                "device": disk.DeviceID,

                "model": model,

                "manufacturer": disk.Manufacturer,

                "size_gb": size_gb,

                "media_type": media_type,

                "serial_number": disk.SerialNumber,

                "health_status": None,

                "operational_status": None,

                "health_percent": None,
            })

    except Exception as exc:

        print(
            f"Storage collection error: {exc}"
        )

    return storage_devices


# ============================================================
# WINDOWS STORAGE HEALTH
# ============================================================

def get_storage_health():
    """
    Try to retrieve Windows physical disk health.

    Windows normally provides:
        - HealthStatus
        - OperationalStatus
        - MediaType

    A health percentage is not guaranteed.
    """

    results = []

    powershell_command = """
    Get-PhysicalDisk |
    Select-Object FriendlyName,
                  SerialNumber,
                  HealthStatus,
                  OperationalStatus,
                  MediaType,
                  Size |
    ConvertTo-Json -Compress
    """

    try:

        completed = subprocess.run(

            [
                "powershell",
                "-NoProfile",
                "-Command",
                powershell_command
            ],

            capture_output=True,

            text=True,

            timeout=15
        )

        if completed.returncode != 0:
            return results

        output = completed.stdout.strip()

        if not output:
            return results

        data = json.loads(output)

        if isinstance(data, dict):
            data = [data]

        for disk in data:

            results.append({

                "name": disk.get(
                    "FriendlyName"
                ),

                "serial_number": disk.get(
                    "SerialNumber"
                ),

                "health_status": disk.get(
                    "HealthStatus"
                ),

                "operational_status": disk.get(
                    "OperationalStatus"
                ),

                "media_type": disk.get(
                    "MediaType"
                ),

                "size_bytes": disk.get(
                    "Size"
                ),

                # Windows may not expose
                # a health percentage.
                "health_percent": None,
            })

    except json.JSONDecodeError:

        print(
            "Storage health error: "
            "Invalid PowerShell JSON"
        )

    except subprocess.SubprocessError as exc:

        print(
            f"Storage health subprocess error: {exc}"
        )

    except Exception as exc:

        print(
            f"Storage health collection error: {exc}"
        )

    return results


# ============================================================
# CPU
# ============================================================

def get_cpu_info():
    """
    Collect CPU hardware information.
    """

    cpu_info = []

    try:

        computer = wmi.WMI()

        for cpu in computer.Win32_Processor():

            cpu_info.append({

                "name": cpu.Name,

                "manufacturer": cpu.Manufacturer,

                "cores": cpu.NumberOfCores,

                "logical_processors":
                    cpu.NumberOfLogicalProcessors,

                "max_clock_mhz":
                    cpu.MaxClockSpeed,
            })

    except Exception as exc:

        print(
            f"CPU collection error: {exc}"
        )

    return cpu_info


# ============================================================
# GPU
# ============================================================

def get_gpu_info():
    """
    Collect GPU information.
    """

    gpu_info = []

    try:

        computer = wmi.WMI()

        for gpu in computer.Win32_VideoController():

            vram_gb = None

            if gpu.AdapterRAM:

                try:

                    vram_gb = round(
                        int(gpu.AdapterRAM)
                        / (1024 ** 3),
                        2
                    )

                except (ValueError, TypeError):

                    vram_gb = None

            gpu_info.append({

                "name": gpu.Name,

                "manufacturer":
                    gpu.AdapterCompatibility,

                "vram_gb": vram_gb,

                "driver_version":
                    gpu.DriverVersion,
            })

    except Exception as exc:

        print(
            f"GPU collection error: {exc}"
        )

    return gpu_info


# ============================================================
# MOTHERBOARD
# ============================================================

def get_motherboard_info():
    """
    Collect motherboard information.
    """

    motherboard_info = []

    try:

        computer = wmi.WMI()

        for board in computer.Win32_BaseBoard():

            motherboard_info.append({

                "manufacturer":
                    board.Manufacturer,

                "product":
                    board.Product,

                "serial_number":
                    board.SerialNumber,
            })

    except Exception as exc:

        print(
            f"Motherboard collection error: {exc}"
        )

    return motherboard_info


# ============================================================
# COMPLETE HARDWARE INFORMATION
# ============================================================

def get_hardware_info():
    """
    Collect complete hardware inventory.
    """

    return {

        "ram": get_ram_info(),

        "storage": get_storage_info(),

        "disk_usage": get_disk_usage(),

        "storage_health":
            get_storage_health(),

        "cpu": get_cpu_info(),

        "gpu": get_gpu_info(),

        "motherboard":
            get_motherboard_info(),
    }

def get_system_uuid():
    """
    SMBIOS System UUID - far more reliably populated across OEMs
    than motherboard serial number, which is frequently blank on
    budget/OEM boards. This is the primary hardware identity used
    to re-link an agent if agent_id.txt is ever lost/deleted.
    """
    try:
        computer = wmi.WMI()
        for product in computer.Win32_ComputerSystemProduct():
            uuid = (product.UUID or "").strip()
            if uuid and uuid.upper() != "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF":
                return uuid
    except Exception as exc:
        logger.error("System UUID collection error: %s", exc)
    return None
# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    hardware_info = get_hardware_info()

    print("=" * 70)
    print("HARDWARE INFORMATION")
    print("=" * 70)

    print("\nRAM:")

    for ram in hardware_info["ram"]:
        print(ram)

    print("\nPHYSICAL STORAGE:")

    for disk in hardware_info["storage"]:
        print(disk)

    print("\nDISK USAGE:")

    for disk in hardware_info["disk_usage"]:
        print(disk)

    print("\nSTORAGE HEALTH:")

    for disk in hardware_info["storage_health"]:
        print(disk)

    print("\nCPU:")

    for cpu in hardware_info["cpu"]:
        print(cpu)

    print("\nGPU:")

    for gpu in hardware_info["gpu"]:
        print(gpu)

    print("\nMOTHERBOARD:")

    for board in hardware_info["motherboard"]:
        print(board)