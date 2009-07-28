#!/bin/sh

COMMAND="call SetupScreen('$STY')"
screen -S "$STY" -p0 -X stuff "gvim -c \"call SetupScreen('"
screen -S "$STY" -p0 -X stuff "$STY"
screen -S "$STY" -p0 -X stuff "')\""
screen -S "$STY" -p0 -X stuff $'\012'

