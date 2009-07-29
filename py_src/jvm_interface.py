from com.sun.jdi import VirtualMachine, Bootstrap;
from com.sun.jdi.connect import *;
from com.sun.jdi.request import EventRequest
from com.sun.jdi.event import *
from java.util import Map, List, Iterator, HashMap
from java.io import PrintWriter, FileWriter, IOException
from java.lang import Runnable, Thread, Throwable
from java.lang import Exception as JavaException

class VMConnection:
    def __init__(self, hostname="localhost", port=8000):#{{{
        self.host, self.port = hostname, port
        connector = Bootstrap.virtualMachineManager().attachingConnectors()[0]
        args = connector.defaultArguments()
        host, timeout, port = [args.get(x) for x in ("hostname", "timeout","port")]
        host.setValue(hostname)
        timeout.setValue(100)
        port.setValue(8000)
        self.vm = connector.attach(args)

    def close(self):
        if not self.vm:
            self.vm.dispose()

    def is_connected(self):
        return self.vm is not None
