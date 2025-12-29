#!/bin/bash -l

sleep 5

# Kill all current conky processes.
killall conky

# Load speech recognition and appropriate configuration
LANG=$(echo $LANG | cut -d'_' -f1)
if [ -f /usr/lib/guideos-conky/GuideOS.$LANG ]; then
    conky -c /usr/lib/guideos-conky/GuideOS.$LANG
else
    conky -c /usr/lib/guideos-conky/GuideOS.en
fi

# sleep 5 && conky -c /usr/lib/guideos-conky/GuideOS-Time
