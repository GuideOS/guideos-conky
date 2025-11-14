#!/usr/bin/python3
# actionschnitzel for GuideOS - 2025
# adapted for guideos-conky by ktt73 - 2025

import subprocess

def get_update_count():
    try:
        # apt update: Standardausgabe und Fehlerausgabe unterdrücken
        subprocess.run(
            ["sudo", "apt", "update"], 
            check=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        # Liste der upgradbaren Pakete holen
        result = subprocess.run(
            ["apt", "list", "--upgradable"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        upgradable_lines = result.stdout.strip().split("\n")
        # Erste Zeile ist meist "Listing..."
        package_count = max(0, len(upgradable_lines) - 1)
        print(package_count)
    except subprocess.CalledProcessError:
        print(0)

if __name__ == "__main__":
    get_update_count()

