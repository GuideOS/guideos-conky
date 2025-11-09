#!/usr/bin/env python3
# ktt73 for GuideOS - 2025

import sys
import platform
import psutil
import socket
import os

def cpu_info():
    cpu = platform.processor()
    phys = psutil.cpu_count(logical=False)
    logical = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    return f"{cpu}| Kerne: {phys} | Threads: {logical} | {freq.current:.2f} MHz"

def ram_info():
    mem = psutil.virtual_memory()
    return f"{mem.total // (1024 ** 2)} MB gesamt, {mem.available // (1024 ** 2)} MB frei"

def disk_info():
    invalid_mountpoints = ['/proc', '/sys', '/run', '/dev', '/var/lib/snapd', '/snap', '/boot/efi']
    valid_fs = ['ext4', 'xfs', 'btrfs', 'ntfs', 'vfat']
    
    disks = psutil.disk_partitions(all=False)  # nur wirklich gemountete Partitionen
    
    infos = []
    seen_devices = set()
    seen_mounts = set()
    
    for d in disks:
        if any(d.mountpoint.startswith(m) for m in invalid_mountpoints):
            continue
        if d.fstype.lower() not in valid_fs:
            continue

        # Skip if device or mountpoint duplicate oder Unterverzeichnis schon gelistet
        if d.device in seen_devices:
            continue

        if any(d.mountpoint.startswith(mnt + '/') or d.mountpoint == mnt for mnt in seen_mounts):
            continue

        seen_devices.add(d.device)
        seen_mounts.add(d.mountpoint)
        
        usage = psutil.disk_usage(d.mountpoint)
        
        mount_name = d.mountpoint.upper()
        if mount_name == '/':
            mount_name = 'ROOT'
        elif mount_name == '/home':
            mount_name = 'HOME'
        elif mount_name == '/boot':
            mount_name = 'BOOT'
        elif mount_name == '/boot/efi':
            mount_name = 'EFI'
        
        infos.append(f"{mount_name}: {usage.total // (1024 ** 3)} GB, frei: {usage.free // (1024 ** 3)} GB")
        
    return "\n".join(infos)


def network_info():
    hostname = socket.gethostname()
    ips = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and iface != 'lo':
                ips.append(f"{iface}: {addr.address}")
    return f"{hostname} | IPs: {' | '.join(ips)}"


def gpu_info():
    try:
        output = os.popen("lspci | grep VGA").read().strip()
        if not output:
            return "GPU unbekannt"
        
        # Beispielausgabe lspci VGA: "01:00.0 VGA compatible controller: NVIDIA Corporation GeForce RTX 3060"
        # Alles vor dem Hersteller wegschneiden:
        
        # Suche nach bekannten Herstellern als Schlüsselwörter (optional erweiterbar)
        known_manufacturers = ['NVIDIA', 'AMD', 'Advanced Micro Devices', 'Intel', 'ATI', 'Broadcom', 'VMware']
        manufacturer_found = None
        
        for man in known_manufacturers:
            if man in output:
                manufacturer_found = man
                break
        
        if manufacturer_found:
            # Hersteller plus alles was danach kommt
            model = output.split(manufacturer_found,1)[-1].strip()
            # Für 'Advanced Micro Devices' kurz 'AMD'
            if manufacturer_found == 'Advanced Micro Devices':
                manufacturer_found = 'AMD'
            return f"{manufacturer_found} {model}"
        else:
            # Kein bekannter Hersteller gefunden, gib komplette Beschreibung ab Herstellerwort „VGA compatible controller“ zurück
            parts = output.split("VGA compatible controller:",1)
            if len(parts) == 2:
                return parts[1].strip()
            else:
                return output
    except Exception as e:
        return f"GPU unbekannt ({e})"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "cpu":
            print(cpu_info())
        elif arg == "ram":
            print(ram_info())
        elif arg == "disk":
            print(disk_info())
        elif arg == "net":
            print(network_info())
        elif arg == "gpu":
            print(gpu_info())
        else:
            print("Unbekannter Parameter")
    else:
        print("Bitte Parameter angeben: cpu | ram | disk | net | gpu")
