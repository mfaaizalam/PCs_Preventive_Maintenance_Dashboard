# its work is to collect basic system information
# like:
# hostname
# IP address
# CPU usage
# RAM usage
# disk usage
# uptime
# OS information
# psutil (process and system utilities) is a cross-platform Python library used for retrieving information on running processes and hardware utilization
import socket
import time
import platform

import psutil


def get_system_info():
    """
    Collect current system information from the PC.
    """

    # Computer hostname
    hostname = socket.gethostname()

    # Try to get the local IP address
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.error:
        ip_address = None

    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=None)

    # RAM usage
    ram_usage = psutil.virtual_memory().percent

    # Disk usage of the main Windows drive
    disk_usage = psutil.disk_usage("C:\\").percent

    # System uptime
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    # Operating system information
    operating_system = platform.system()
    os_version = platform.version()

    return {
        "hostname": hostname,
        "ip_address": ip_address,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "disk_usage": disk_usage,
        "uptime_seconds": uptime_seconds,
        "operating_system": operating_system,
        "os_version": os_version,
    }


if __name__ == "__main__":
    system_info = get_system_info()
    print(system_info)

