#!/bin/sh

touch __init__.py

for x in *.ui
do
	pyuic4 $x > $(echo $x | sed -e 's/\.ui/\.py/')
done

