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

#Installation
```
sudo apt update
sudo apt install guideos-conky
```

#Requirement

- `conky-all` must be installed
- Ubunto Mono Nerd Regular Font must be installed (https://www.nerdfonts.com/font-downloads)
- Python3 must be installed
- `wget` must be installed
- `psutils` must be installed

# Screenshot

<img width="505" height="527" alt="screenshot" src="https://github.com/user-attachments/assets/40215fdc-2054-4e50-9964-c18bb69bfa58" />
