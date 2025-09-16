#!/bin/bash -l

# Let the desktop load for a few seconds before running
sleep 3

# Kill all current conky processes.
killall conky

conky -c /home/ktt73/.conky/GuideOS &
sleep 2 && conky -c /home/ktt73/.conky/GuideOS-Time &
#sleep 1 && killall conky &
#conky -c /home/ktt73/.conky/GuideOS &
#sleep 2 && conky -c /home/ktt73/.conky/GuideOS-Time &