#!/usr/bin/env python3

# ktt73 for GuideOS - 2025

import sys
import platform
import psutil
import socket
import os


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
    freq = psutil.cpu_freq()
    return f"{cpu}| {phys} Kerne | {logical} Threads"


def ram_info():
    mem = psutil.virtual_memory()
    return (
        f"gesamt {mem.total // (1024 ** 2)} MB | "
        f"frei {mem.available // (1024 ** 2)} MB | "
        f"benutzt {mem.used // (1024 ** 2)} MB"
    )


def disk_info():
    invalidmountpoints = [
        "/proc",
        "/sys",
        "/run",
        "/dev",
        "/var/lib/snapd",
        "/snap",
        "/boot/efi",
    ]
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
            mountname = os.path.basename(d.mountpoint.rstrip("/")).upper()

        infos.append(
            f"{mountname} | {d.fstype} | {usage.total // 1024 ** 3} GB | "
            f"frei {usage.free // 1024 ** 3} GB | "
            f"benutzt {usage.used // 1024 ** 3} GB"
        )

    return "\n".join(infos)


def network_info():
    hostname = socket.gethostname()
    ips = []

    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and iface != "lo":
                ips.append(f"{addr.address} | {iface}")

    return f"LAN IP v4 {' | '.join(ips)}"


def gpu_info():
    try:
        # alle VGA-/3D-Geräte holen (z.B. mehrere GPUs oder VM-GPUs)
        output = os.popen(
            "lspci | egrep 'VGA compatible controller|3D controller'"
        ).read().strip()

        if not output:
            return "GPU unbekannt"

        lines = output.splitlines()

        known_manufacturers = [
            "NVIDIA",
            "Advanced Micro Devices",
            "AMD",
            "Intel",
            "ATI",
            "VMware",
            "Broadcom",
            "VirtualBox",
            "Red Hat",
            "QXL",
        ]

        results = []

        for line in lines:
            # Beispiel:
            # 01:00.0 VGA compatible controller: NVIDIA Corporation GP104 [GeForce GTX 1070] (rev a1)
            if "VGA compatible controller:" in line:
                parts = line.split("VGA compatible controller:", 1)[1].strip()
            elif "3D controller:" in line:
                parts = line.split("3D controller:", 1)[1].strip()
            else:
                parts = line.strip()

            manufacturer_found = None
            for man in known_manufacturers:
                if man in parts:
                    manufacturer_found = man
                    break

            if not manufacturer_found:
                # kein bekannter Hersteller → Rohtext zurückgeben
                results.append(parts)
                continue

            # AMD Langname vereinheitlichen
            if manufacturer_found == "Advanced Micro Devices":
                manufacturer_found = "AMD"

            # Rest nach Hersteller ist der Roh-Modelname
            model = parts.split(manufacturer_found, 1)[1].strip()

            # übliche Füllwörter entfernen
            for trash in ["Corporation", "Inc.", "Ltd."]:
                model = model.replace(trash, "")

            # alles ab einer Revision/Klammer abschneiden
            for sep in [" (rev", " [rev", "(rev", "[rev", " rev "]:
                if sep in model:
                    model = model.split(sep, 1)[0]

            # Mehrfach-Leerzeichen und störende Zeichen entfernen
            model = " ".join(model.split())
            model = model.strip("-:, ")

            results.append(f"{manufacturer_found} {model}".strip())

        return " | ".join(results)

    except Exception as e:
        return f"GPU unbekannt ({e})"


def gpu_driver():
    try:
        # -k zeigt Kernel-Treiber, -A3 nimmt ein paar Folgezeilen mit
        output = os.popen(
            "lspci -k | egrep -A3 'VGA compatible controller|3D controller'"
        ).read().strip()
        if not output:
            return "GPU Treiber unbekannt"

        lines = output.splitlines()
        drivers = []

        for line in lines:
            if "Kernel driver in use:" in line:
                # z.B. "\tKernel driver in use: nvidia"
                drv = line.split("Kernel driver in use:", 1)[1].strip()
                if not drv:
                    continue

                # Version mit modinfo holen
                cmd = f"modinfo {drv} 2>/dev/null | grep '^version'"
                out = os.popen(cmd).read().strip()
                if out:
                    parts = out.split(":", 1)
                    if len(parts) == 2:
                        ver = parts[1].strip()
                        drivers.append(f"{drv} {ver}")
                        continue

                # Fallback, falls keine Version gefunden wird
                drivers.append(f"{drv} (Version unbekannt)")

        if not drivers:
            return "GPU Treiber unbekannt"

        # bei mehreren GPUs: nvidia 535.xx | amdgpu x.y.z | ...
        return " | ".join(drivers)

    except Exception as e:
        return f"GPU Treiber unbekannt ({e})"



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
        elif arg == "gpu_driver":
            print(gpu_driver())
        else:
            print("Unbekannter Parameter")
    else:
        print("Bitte Parameter angeben: cpu | ram | disk | net | gpu | gpu_driver")
