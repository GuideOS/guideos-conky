#!/usr/bin/env python3
# ktt73 for GuideOS - 2025

import platform
import psutil
import socket
import os

def cpu_info():
    cpu = platform.processor()
    phys = psutil.cpu_count(logical=False)
    logical = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    return f"CPU: {cpu} | Cores: {phys} | Threads: {logical} | Frequency: {freq.current:.2f} MHz"

def ram_info():
    mem = psutil.virtual_memory()
    return f"RAM: {mem.total // (1024 ** 2)} MB total, {mem.available // (1024 ** 2)} MB frei"

def disk_info():
    disks = psutil.disk_partitions()
    infos = []
    for d in disks:
        usage = psutil.disk_usage(d.mountpoint)
        infos.append(f"{d.device}: {usage.total // (1024 ** 3)} GB, frei: {usage.free // (1024 ** 3)} GB")
    return " | ".join(infos)

def network_info():
    hostname = socket.gethostname()
    ips = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ips.append(f"{iface}: {addr.address}")
    return f"Hostname: {hostname} | IPs: {' | '.join(ips)}"

def gpu_info():
    try:
        # Nvidia/AMD: Optional, über lspci
        gpu = os.popen("lspci | grep VGA").read().strip()
        return f"GPU: {gpu}"
    except Exception:
        return "GPU: Unbekannt"

def main():
    print(cpu_info())
    print(ram_info())
    print(disk_info())
    print(network_info())
    print(gpu_info())

if __name__ == "__main__":
    main()