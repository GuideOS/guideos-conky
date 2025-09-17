# guideos-conky

- `conky-all` must be installed
- Ubunto Mono Nerd Regular Font must be installed (https://www.nerdfonts.com/font-downloads)
- Python3 must be installed
- `wget` must be installed

# Instructions for correct functioning

In order to display your own hardware correctly, you have to adjust it.

In `/usr/lib/guideos-conky/GuideOS`

- to add more hard drives, simply use the lines

```
  ${voffset 5}${goto 0}${color1}${font1}   Root - ${fs_type /} ${alignr} ${fs_used /} / ${fs_size /}  
```
- copy and paste underneath. Then adjust the addresses e.g. `/home/{$username}`

- for the correct display of the network category, the correct network card must be entered e.g. `enp34s0`

- to change the length or width of the window, you can do this with the following parameters

```
  	minimum_height = 490,
	maximum_width = 450,
	minimum_width = 450,
```


# Screenshot

<img width="658" height="585" alt="Auswahl_025" src="https://github.com/user-attachments/assets/93972d00-d3d1-4f94-8df5-d6b2a95add63" />
