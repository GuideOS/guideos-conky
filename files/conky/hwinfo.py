#!/usr/bin/env python3

# ktt73 for GuideOS - 2025

# - Festplatten inkl. fatex, ntfs (angezeigt werden nur Platten welche in /media, /run/media 
#   oder /home eingebunden sind 
# - Festpattenausgabe Reihenfolge 1. Label, 2. Pfad, "/" als ROOT und "/home" als HOME
# - Netwerkkarten untereinander mit IP Adressen (IPv4 und IPv6)
# - WAN IPv4/IPv6 Abfrage untereinander
# - Hybrit GPUs untereinander gelistet
# - GPU Treiber untereinander gelistet
# - korrektes Auslesen aller GPU Treiber (inkl. nouveau (Kernel))
# - RAM belegter Speicher entfernt (zu lang)
# - GPU Speicher (total und free) via glxinfo oder sysfs (AMD, Nvidia)
# - Kürzere GPU Bezeichnungen für integrierte Grafiken von Intel und AMD
# - Fehlerbehandlung bei allen Abfragen verbessert
# - Code optimiert und bereinigt
# - Script komplett in english übersetzt
# - Übersetzung ins Deutsche vorbereitet (gettext)

import sys
import platform
import psutil
import socket
import os
import requests
import re
import gettext

locale_path = os.path.join(os.path.dirname(__file__), 'locale')
lang = gettext.translation('hwinfo', localedir=locale_path, languages=['de'], fallback=True)
_ = lang.gettext

def cpu_type():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception as e:
        return _("CPU type unknown ({})").format(e)

def cpu_info():
    cpu = platform.processor()
    phys = psutil.cpu_count(logical=False)
    logical = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    return _("{}| {} cores | {} threads").format(cpu, phys, logical)

def ram_info():
    mem = psutil.virtual_memory()
    return _("total {} MB | free {} MB").format(
        mem.total // (1024 ** 2),
        mem.available // (1024 ** 2)
    )

def get_label(device):
    try:
        output = os.popen(f"blkid -o value -s LABEL {device}").read().strip()
        return output if output else None
    except:
        return None

def disk_info():
    invalid_mountpoints = ["/proc", "/sys", "/run", "/dev", "/var/lib/snapd", "/snap", "/boot/efi"]
    valid_fs = ["ext4", "xfs", "btrfs", "ntfs", "vfat", "exfat"]
    disks = psutil.disk_partitions(all=False)
    infos = []
    seen_devices = set()
    seen_mounts = set()

    for d in disks:
        if any(d.mountpoint.startswith(m) for m in invalid_mountpoints):
            continue
        if d.fstype.lower() not in valid_fs:
            continue
        if d.device in seen_devices or d.mountpoint in seen_mounts:
            continue

        seen_devices.add(d.device)
        seen_mounts.add(d.mountpoint)
        usage = psutil.disk_usage(d.mountpoint)
        label = get_label(d.device)

        if label:
            mount_name = label.upper()
        elif d.mountpoint == "/":
            mount_name = "ROOT"
        elif d.mountpoint == "/home":
            mount_name = "HOME"
        else:
            mount_name = os.path.basename(d.mountpoint.rstrip("/")).upper()

        infos.append(
            _("{} | {} | {} GB | free {} GB | used {} GB").format(
                mount_name, d.fstype, usage.total // 1024**3,
                usage.free // 1024**3, usage.used // 1024**3
            )
        )

    return "\n".join(infos)

def get_wan_ipv4():
    try:
        return requests.get("https://api.ipify.org", timeout=3).text.strip()
    except Exception:
        return None

def get_wan_ipv6():
    try:
        return requests.get("https://api64.ipify.org", timeout=3).text.strip()
    except Exception:
        return None

def network_info():
    label_lan = _("LAN IP v4")
    pad_lan = label_lan + " "
    ips = []

    for iface, addrs in psutil.net_if_addrs().items():
        if iface == "lo":
            continue
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ips.append(f"{addr.address} | {iface}")

    lines = []
    if ips:
        if len(ips) == 1:
            lines.append(f"{pad_lan}{ips[0]}")
        else:
            first_lan = f"\n{pad_lan}{ips[0]}"
            indent_lan = " " * len(pad_lan)
            rest_lan = [f"{indent_lan}{ip}" for ip in ips[1:]]
            lines.append(first_lan)
            lines.extend(rest_lan)
    else:
        lines.append(f"{pad_lan}{_('none')}")

    wan4 = get_wan_ipv4()
    label_wan4 = _("WAN IP v4")
    pad_wan4 = label_wan4 + " "
    if wan4:
        lines.append(f"{pad_wan4}{wan4}")
    else:
        lines.append(f"{pad_wan4}{_('unknown')}")

    wan6 = get_wan_ipv6()
    label_wan6 = _("WAN IP v6")
    pad_wan6 = label_wan6 + " "
    if wan6:
        lines.append(f"{pad_wan6}{wan6}")
    else:
        lines.append(f"{pad_wan6}{_('unknown')}")

    return "\n".join(lines)

def shorten_gpu_name(model, manufacturer):
    model_lower = model.lower()

    if manufacturer == "Intel":
        if "2nd generation core processor family" in model_lower:
            return "Intel 2nd Gen integrated"
        elif "3rd generation core processor family" in model_lower:
            return "Intel 3rd Gen integrated"
        elif "4th generation core processor family" in model_lower:
            return "Intel 4th Gen integrated"
        elif any(x in model_lower for x in ["uhd graphics", "hd graphics"]):
            if "11th" in model_lower or "12th" in model_lower or "13th" in model_lower:
                return "Intel 11th+ Gen iGPU"
            elif "iris" in model_lower:
                return "Intel Iris Xe"
            elif "10th" in model_lower:
                return "Intel 10th Gen iGPU"
            else:
                return "Intel HD/UHD"
        elif "xeon" in model_lower:
            return "Intel Xeon iGPU"

    elif manufacturer == "AMD":
        if "radeon" in model_lower and "rx" not in model_lower:
            if "ryzen" in model_lower or "zen" in model_lower:
                return "AMD Ryzen APU"
            elif "athlon" in model_lower:
                return "AMD Athlon APU"
            else:
                return "AMD iGPU"
        elif any(x in model_lower for x in ["integrated graphics", "family graphics"]):
            return "AMD integrated"

    return f"{manufacturer} {model}"

def gpu_info():
    try:
        output = os.popen(
            "lspci | egrep 'VGA compatible controller|3D controller'"
        ).read().strip()

        if not output:
            return _("GPU unknown")

        lines = output.splitlines()
        known_manufacturers = [
            "NVIDIA", "Advanced Micro Devices", "AMD", "Intel", "ATI",
            "VMware", "Broadcom", "VirtualBox", "Red Hat", "QXL"
        ]

        models = []
        for line in lines:
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
                models.append(parts)
                continue

            if manufacturer_found == "Advanced Micro Devices":
                manufacturer_found = "AMD"

            model = parts.split(manufacturer_found, 1)[1].strip()
            for trash in ["Corporation", "Inc.", "Ltd."]:
                model = model.replace(trash, "")

            for sep in [" (rev", " [rev", "(rev", "[rev", " rev "]:
                if sep in model:
                    model = model.split(sep, 1)[0]

            model = " ".join(model.split())
            model = model.strip("-, :")

            short_model = shorten_gpu_name(model, manufacturer_found)
            models.append(short_model)

        label = _("GPU")
        lines_out = []

        if models:
            # Alle Zeilen linksbündig mit Label
            for m in models:
                lines_out.append(f"{label} {m}")
        else:
            lines_out.append(f"{label} {_('unknown')}")

        return "\n".join(lines_out)

    except Exception as e:
        return _("GPU unknown ({})").format(e)

def gpu_driver():
    try:
        output = os.popen(
            "lspci -k | egrep -A3 'VGA compatible controller|3D controller'"
        ).read().strip()

        if not output:
            return _("GPU driver unknown")

        lines = output.splitlines()
        drivers = []

        for line in lines:
            if "Kernel driver in use:" in line:
                drv = line.split("Kernel driver in use:", 1)[1].strip()

                if not drv or drv == "unknown":
                    continue

                driver_info = f"{drv}"

                if drv == "nvidia" and os.path.exists("/proc/driver/nvidia/version"):
                    with open("/proc/driver/nvidia/version") as f:
                        content = f.read()
                    version_match = re.search(
                        r"NVRM version:.*?(\d+\.\d+(?:\.\d+)?)", content
                    )
                    if version_match:
                        driver_info = f"nvidia {version_match.group(1)}"

                elif drv == "amdgpu":
                    out = os.popen(
                        "modinfo amdgpu 2>/dev/null | grep '^version:'"
                    ).read().strip()
                    if out:
                        ver = out.split(":", 1)[1].strip()
                        driver_info = f"amdgpu {ver}"

                elif drv == "nouveau":
                    if os.path.exists("/proc/driver/nvidia/version"):
                        with open("/proc/driver/nvidia/version") as f:
                            content = f.read()
                        version_match = re.search(r"release (\d+(?:\.\d+)*)", content)
                        if version_match:
                            driver_info = f"nouveau {version_match.group(1)}"
                        else:
                            driver_info = _("nouveau (Kernel)")
                    else:
                        driver_info = _("nouveau (Kernel)")

                elif drv in ["i915", "iris"]:
                    out = os.popen(
                        f"modinfo {drv} 2>/dev/null | grep '^version:'"
                    ).read().strip()
                    if out:
                        ver = out.split(":", 1)[1].strip()
                        driver_info = f"{drv} {ver}"

                drivers.append(driver_info)

        label = _("GPU driver")
        lines_out = []

        if drivers:
            # Alle Zeilen linksbündig mit Label
            for d in drivers:
                lines_out.append(f"{label} {d}")
        else:
            lines_out.append(f"{label} {_('unknown')}")

        return "\n".join(lines_out)

    except Exception as e:
        return _("GPU driver unknown ({})").format(e)

def gpu_memory():
    """Get GPU memory information (total and free) via glxinfo"""
    try:
        # Try NVIDIA GL_NVX_gpu_memory_info first
        nvidia_total = os.popen(
            "glxinfo 2>/dev/null | grep 'Total available memory' | head -1"
        ).read().strip()

        nvidia_free = os.popen(
            "glxinfo 2>/dev/null | grep 'Currently available dedicated video memory' | head -1"
        ).read().strip()

        total_mb = None
        free_mb = None

        if nvidia_total and nvidia_free:
            # NVIDIA format: values are already in MB, not KB!
            total_match = re.search(r'(\d+)', nvidia_total)
            free_match = re.search(r'(\d+)', nvidia_free)

            if total_match and free_match:
                total_mb = int(total_match.group(1))
                free_mb = int(free_match.group(1))
                return f"total {total_mb} MB | free {free_mb} MB"

        # Try AMD via sysfs
        amd_total_path = "/sys/class/drm/card0/device/mem_info_vram_total"
        amd_used_path = "/sys/class/drm/card0/device/mem_info_vram_used"

        if os.path.exists(amd_total_path) and os.path.exists(amd_used_path):
            with open(amd_total_path, 'r') as f:
                total_bytes = int(f.read().strip())
            with open(amd_used_path, 'r') as f:
                used_bytes = int(f.read().strip())

            total_mb = total_bytes // (1024 * 1024)
            free_mb = (total_bytes - used_bytes) // (1024 * 1024)

            return f"total {total_mb} MB | free {free_mb} MB"

        # Fallback: try to parse video memory from glxinfo
        output = os.popen("glxinfo 2>/dev/null | grep -i 'video memory'").read().strip()

        if output:
            match = re.search(r'(\d+)\s*MB', output, re.IGNORECASE)
            if match:
                total_mb = int(match.group(1))
                return f"total {total_mb} MB"

        return _("GPU memory unknown")

    except Exception as e:
        return _("GPU memory unknown ({})").format(e)

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
        elif arg == "gpu_memory":
            print(gpu_memory())
        else:
            print(_("Unknown parameter"))
    else:
        print(_("Please specify parameter: cpu | ram | disk | net | gpu | gpu_driver | gpu_memory"))

