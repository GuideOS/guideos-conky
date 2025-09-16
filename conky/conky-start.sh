#!/bin/bash -l

# Let the desktop load for a few seconds before running
sleep 3

# Kill all current conky processes.
killall conky

conky -c /usr/lib/conky/GuideOS &
sleep 2 && conky -c /usr/lib/conky/GuideOS-Time &
