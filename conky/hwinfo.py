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
    return f"gesamt {mem.total // (1024 ** 2)} MB | frei {mem.available // (1024 ** 2)} MB | benutzt {mem.used // (1024 ** 2)} MB"

def disk_info():
    import psutil
    invalidmountpoints = ["/proc", "/sys", "/run", "/dev", "/var/lib/snapd", "/snap", "/boot/efi"]
    valid_mountpoints = ["/media", "/run/media"]
    validfs = ["ext4", "xfs", "btrfs", "ntfs", "vfat", "exfat"]
    disks = psutil.disk_partitions(all=False)
    infos = []
    seendevices = set()
    seenmounts = set()
    for d in disks:
        if any(d.mountpoint.startswith(m) for m in invalidmountpoints):
            if not any(d.mountpoint.startswith(v) for v in valid_mountpoints):
                continue
        if d.fstype.lower() not in validfs:
            continue
        if d.device in seendevices:
            continue
        if d.mountpoint in seenmounts:
            continue
        seendevices.add(d.device)
        seenmounts.add(d.mountpoint)
        usage = psutil.disk_usage(d.mountpoint)
        # nur letzter Name des Mountpoints
        if d.mountpoint == "/":
            mountname = "ROOT"
        else:
            mountname = os.path.basename(d.mountpoint.rstrip('/')).upper()
        infos.append(f"{mountname} | {d.fstype} | {usage.total // 1024 ** 3} GB | frei {usage.free // 1024 ** 3} GB | benutzt {usage.used // 1024 ** 3} GB")
    return "\n".join(infos)



def network_info():
    hostname = socket.gethostname()
    ips = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and iface != 'lo':
                ips.append(f"{addr.address} | {iface}")
    return f"LAN IP v4 {' | '.join(ips)}"


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

