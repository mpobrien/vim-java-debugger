import sys, os
import re
from java.lang import Runnable, Thread, Throwable
from jvm_interface import VMConnection
import getopt
from com.sun.jdi import *
from com.sun.jdi.request import *
from com.sun.jdi.event import *


class EventHandler (Thread):
    def __init__(self, vm):
        self.vm = vm
        self.currentThread = None

    def run(self):
        queue = self.vm.eventQueue();
        while True:
            try:
                eventSet = queue.remove();
                resumeStoppedApp = False;
                it = eventSet.eventIterator();
                while it.hasNext():
                    self.handleEvent( it.nextEvent() )
                    #resumeStoppedApp |= !handleEvent(it.nextEvent());
                eventSet.resume()
#                 if (resumeStoppedApp):
#                     eventSet.resume()
#                 elif eventSet.suspendPolicy() == EventRequest.SUSPEND_ALL:
#                     pass
                    #setCurrentThread(eventSet);
                    #notifier.vmInterrupted();
            except Throwable, t:
                t.printStackTrace();

    def handleEvent(self, event):
        print event
        if isinstance(event, ClassPrepareEvent):
            try:
                print "EVENT: loaded class named: %s in source file %s" % ( event.referenceType().name(), event.referenceType().sourceName() )
            except: # no source information available
                print "EVENT: loaded class named: %s" % ( event.referenceType().name() )

