# guideos-conky

This Conky tool determines the hardware used via a Python script, as well as update information. Therefore, no user intervention is required.

The following information is retrieved via Python: 
- CPU type
- RAM
- GPU type
- GPU driver
- GPU Memory (only AMD and Nvidia)
- network interface and IP address
- mounted hard drive partitions
- mounted USB drives
- number of updates
- ext. IP's

Conky himself reads the following:
- nodename
- GuideOS version
- kernel
- runtime

# Installation
```
sudo apt update
sudo apt install guideos-conky
```

# Requirement

- `conky-all` must be installed
- Ubunto Mono Nerd Regular Font must be installed Download von https://www.nerdfonts.com (https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/UbuntuMono.zip)
- Python3 must be installed
- `wget` must be installed
- `psutils` must be installed

# Screenshot

<img width="434" height="563" alt="Bildschirmfoto vom 2026-01-09 16-16-55" src="https://github.com/user-attachments/assets/e1ecba44-4df7-45e7-9837-c7e78fa2f944" />

