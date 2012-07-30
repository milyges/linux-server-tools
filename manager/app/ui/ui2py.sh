#!/bin/sh

for x in *.ui
do
	pyuic4 $x > $(echo $x | sed -e 's/\.ui/\.py/')
done

