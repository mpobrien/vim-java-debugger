#!/bin/sh


alias jy='/usr/local/meetup/tools/jython'

#COMMAND="call SetupScreen('$STY')"
SERVERNAME="vim$STY"
gvim --servername $SERVERNAME &
jy /home/mike/projects/github_mpobrien/vim-java-debugger/py_src/shell.py -s /usr/local/meetup -h localhost -p 8000
#screen -S "$STY" -p0 -X stuff "gvim -c \"call SetupScreen('"
#screen -S "$STY" -p0 -X stuff "$STY"
#screen -S "$STY" -p0 -X stuff "')\" &"
#screen -S "$STY" -p0 -X stuff $'\012'

#sleep 3

#   jy

