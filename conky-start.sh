#!/bin/bash -l

#created from KTT73 for GuideOS

# Let the desktop load for a few seconds before running
sleep 3

# Kill all current conky processes.
killall conky

conky -c /home/ktt73/.conky/GuideOS &
sleep 2 && conky -c /home/ktt73/.conky/GuideOS-Time &
