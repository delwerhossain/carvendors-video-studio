#!/bin/sh
# Re-mounts every component instance of the test composition (run from anywhere).
cd "$(dirname "$0")" || exit 1
M() { python3 ../tools/mount.py add . "$@" || exit 1; }
M logo-top logo --start 0 --dur 9 --track 8 --vars '{"x":80,"y":120}'
M hero-model hero --start 0 --dur 2.8 --track 3 --vars '{"make":"ABARTH","model":"595","x":570,"y":250,"size":235}'
M localized-contrast hero-veil --start 0 --dur 2.8 --track 2 --below hero --vars '{"x":200,"y":318,"w":740,"h":226,"opacity":0.46,"feather":0.4,"shape":"soft-rect","delay":0.1}'
M detail-line detail --start 2.8 --dur 2.0 --track 3 --vars '{"line1":"In the","line2":"details.","x":570,"y":330,"align":"center","size":90,"scrim":0.3}'
M shape-text standout --start 4.8 --dur 2.6 --track 3 --vars '{"line1":"Made to","word":"stand out","x":570,"y":330,"align":"center","tilt":-3,"scrim":0.25}'
M verified-feature feat --start 7.4 --dur 1.6 --track 3 --vars '{"items":"Sporty styling|Compact design","x":363,"y":352,"scrim":0.32}'
M outro-real-showroom outro --start 9 --dur 3 --track 4 --vars '{"src":"../assets/showroom/front-side-view.png","focus":"79% 50%","shade":0.72}'
M caption-line captions --start 0 --dur 9 --track 9 --vars '{"chunks":[{"s":3.0,"e":4.65,"text":"A closer look at the Abarth 595."},{"s":5.05,"e":7.25,"text":"Bold side stripes, white mirror caps, black alloys."}]}'
