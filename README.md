# guideos-conky

This Conky tool determines the hardware used via a Python script, as well as update information. Therefore, no user intervention is required.

The following information is retrieved via Python: 
- CPU type
- RAM
- GPU type
- network interface and IP address
- mounted hard drive partitions
- mounted USB drives
- number of updates

Conky himself reads the following:
- nodename
- GuideOS version
- ext. IP's
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

<img width="488" height="542" alt="guideos-conky" src="https://github.com/user-attachments/assets/fad628e8-f89d-4c02-848a-47b4619d9c9b" />

