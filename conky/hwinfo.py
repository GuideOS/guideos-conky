#!/usr/bin/env python3

# ktt73 for GuideOS - 2025
# Modifiziert: AMD GPU-Anzeige wie NVIDIA gekürzt (ATI/Navi entfernt)
# Modifiziert: Bei mehreren GPUs (Optimus/Hybrid) nur aktive GPU anzeigen
# Modifiziert: GPU Bus/Class Prefix + PCI Vendor:Device IDs komplett entfernt

import sys
import platform
import psutil
import socket
import os
import re

def cpu_type():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception as e:
        return f"CPU Typ unbekannt ({e})"

def cpu_info():
    cpu = platform.processor()
    phys = psutil.cpu_count(logical=False)
    logical = psutil.cpu_count(logical=True)
    return f"{cpu}| {phys} Kerne | {logical} Threads"

def ram_info():
    mem = psutil.virtual_memory()
    return (
        f"gesamt {mem.total // (1024 ** 2)} MB | "
        f"frei {mem.available // (1024 ** 2)} MB | "
        f"benutzt {mem.used // (1024 ** 2)} MB"
    )

def disk_info():
    invalidmountpoints = ["/proc", "/sys", "/run", "/dev",
                          "/var/lib/snapd", "/snap", "/boot/efi"]
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
        if d.mountpoint == "/":
            mountname = "ROOT"
        else:
            mountname = os.path.basename(d.mountpoint.rstrip('/')).upper()

        infos.append(
            f"{mountname} | {d.fstype} | "
            f"{usage.total // 1024 ** 3} GB | "
            f"frei {usage.free // 1024 ** 3} GB | "
            f"benutzt {usage.used // 1024 ** 3} GB"
        )

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
        # Alle GPUs einsammeln
        lspci_output = os.popen(
            "lspci -nn | grep -Ei 'vga|3d|display'"
        ).read().strip()

        if not lspci_output:
            return "GPU unbekannt"

        lines = lspci_output.splitlines()
        gpus = []
        known_manufacturers = [
            'NVIDIA', 'AMD', 'Advanced Micro Devices', 'Intel',
            'ATI', 'Broadcom', 'VMware'
        ]

        for line in lines:
            # Entferne Bus- und Klasseninformationen + PCI Vendor:Device IDs
            # 1. IDs am Anfang: [xxxx:xxxx] oder 00:01.0 ...
            cleaned = re.sub(r'^\[[\da-fA-F]{4}:[\da-fA-F]{4}\]\s*|^[\da-fA-F:.]+\s+[^\:]+:\s*', '', line).strip()
            # 2. IDs mittendrin entfernen: [1af4:1050]
            cleaned = re.sub(r'\s*\[[\da-fA-F]{4}:[\da-fA-F]{4}\]', '', cleaned).strip()

            manufacturer_found = None
            for man in known_manufacturers:
                if man in cleaned:
                    manufacturer_found = man
                    break

            if manufacturer_found:
                model = cleaned.split(manufacturer_found, 1)[-1].strip()
                if manufacturer_found == 'Advanced Micro Devices':
                    manufacturer_found = 'AMD'
                if manufacturer_found == 'NVIDIA':
                    model = model.replace("Corporation", "").strip()
                elif manufacturer_found == 'AMD':
                    model = model.replace("[AMD/ATI]", "").replace("ATI", "").strip()
                if model.startswith("/"):
                    model = model.lstrip("/").strip()
                bracket_parts = model.split('[')
                if len(bracket_parts) > 1:
                    model = bracket_parts[1].split(']')[0].strip()
                pretty = f"{manufacturer_found} {model}".strip()
                gpus.append((manufacturer_found, pretty))
            else:
                # Fallback, wenn kein Hersteller erkannt
                gpus.append((None, cleaned.strip()))

        if not gpus:
            return "GPU unbekannt"

        # Aktive GPU über glxinfo ermitteln
        renderer_line = os.popen(
            "glxinfo -B 2>/dev/null | grep 'OpenGL renderer'"
        ).read().strip()

        active_name = None
        if renderer_line:
            lower = renderer_line.lower()
            if "nvidia" in lower or "geforce" in lower or "rtx" in lower or "gtx" in lower:
                active_name = "NVIDIA"
            elif "radeon" in lower or "amd" in lower:
                active_name = "AMD"
            elif "intel" in lower:
                active_name = "Intel"

        # Wenn aktive GPU erkannt wurde, passende Zeile aus lspci wählen
        if active_name:
            for man, pretty in gpus:
                if man == active_name:
                    return pretty

        # Fallback: Wenn glxinfo nichts bringt oder kein Match: erste gefilterte GPU
        return gpus[0][1]

    except Exception as e:
        return f"GPU unbekannt ({e})"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "cpu":
            print(cpu_type())
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
