#!/usr/bin/python3

# actionschnitzel for GuideOS - 2025
# adjusted for guideos-conky ktt73 - 11/2025
# pkcon-Variant added  ktt73 - 12/2025
# flatpak added ktt73 - 12/2025

import subprocess

def get_pkcon_update_count():
    try:
        subprocess.run(
            ["sudo", "pkcon", "refresh"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        result = subprocess.run(
            ["pkcon", "--noninteractive", "get-updates"],
            capture_output=True,
            text=True,
            check=True
        )

        lines = result.stdout.strip().split("\n")
        package_lines = [
            l for l in lines
            if l.startswith("Normal") or l.startswith("Sicherheit")
        ]
        return len(package_lines)
    except subprocess.CalledProcessError:
        return 0

def get_flatpak_update_count():
    try:
        result = subprocess.run(
            ["flatpak", "remote-ls", "--updates"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split("\n")

        data_lines = [l for l in lines if l.strip()]
        if len(data_lines) > 0 and "NAME" in data_lines[0]:
            data_lines = data_lines[1:]

        return len(data_lines)
    except subprocess.CalledProcessError:
        return 0

if __name__ == "__main__":
    pkcon_count = get_pkcon_update_count()
    flatpak_count = get_flatpak_update_count()

    # Choose the output as you need it for Conky, e.g.:
    # only pkcon:
    # print(pkcon_count) APT

    # or only flatpak:
    # print(flatpak_count) Flatpak

    # or both:
    print(f"{pkcon_count} APT | {flatpak_count} Flatpak")
