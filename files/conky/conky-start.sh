#!/bin/bash -l

sleep 5
# Kill all current conky processes.
killall conky

conky -c /usr/lib/guideos-conky/GuideOS
#sleep 5 && conky -c /usr/lib/guideos-conky/GuideOS-Time &
