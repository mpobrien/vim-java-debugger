from com.sun.jdi import VirtualMachine, Bootstrap;
from com.sun.jdi.connect import *;
from com.sun.jdi.request import EventRequest
from com.sun.jdi.event import *
from java.util import Map, List, Iterator, HashMap
from java.io import PrintWriter, FileWriter, IOException
from java.lang import Runnable, Thread, Throwable
from java.lang import Exception as JavaException
import sys, os, tempfile

logfile = open('/home/mike/debugger_log.log', 'w')
def log(x): logfile.write( str(x)+'\n' ); logfile.flush()

def get_classrefs_from_filename(vm,filename):
    possible_classes = []
    for c in vm.allClasses():
        try:
            if c.sourceName() == filename: possible_classes.append( c )
        except: continue
    return possible_classes

class VMConnection:
    def __init__(self, hostname="localhost", port=8000):#{{{
        connector = Bootstrap.virtualMachineManager().attachingConnectors()[0]
        args = connector.defaultArguments()
        host, timeout, port = [args.get(x) for x in ("hostname", "timeout","port")]
        host.setValue(hostname)
        timeout.setValue(100)
        port.setValue(8000)
        self.vm = connector.attach(args)
        self.breakpoints = []#}}}

class Debugger:
    def __init__(self, srcdir, session_id, hostname="localhost", port=8000):#{{{
        self.commands = {'quit':self.quit,
                         'add_bp':self.add_breakpoint,
                         'clear_bp':self.clear_breakpoint,
                         'list_bp':None,
                         'resume':self.resume,
                         'show_classes':self.printclasses,
                         'clearall_bp':self.clearall_breakpoints}
        log('debugger started.')
        self.session_id = session_id
        self.vm = VMConnection(hostname, port)
        self.eventwatcher = Thread( VirtualMachineEventHandler(self.vm.vm, self) )
        self.eventwatcher.start()
        commandreader = Thread(CommandReader('vim_jpda_com.' + str( self.session_id ), self.handle_command ))
        commandreader.start()
        #self.send_vim_keys("<Esc>:call Jy_DebuggerReady()<CR>")
    #}}}

    def vm_callback(self, next_event):#{{{
        if isinstance(next_event, BreakpointEvent):
            fileinfo = open('/home/mike/Desktop/cfiletemp.txt', 'w')
            #fileinfo=tempfile.TemporaryFile()
            log( next_event.location().sourceName() + ":" + str( next_event.location().lineNumber() ) )
            fileinfo.write( next_event.location().sourceName() + ":" + str( next_event.location().lineNumber() ) )
            result = self.eval_vim_command("JumpTo('" +fileinfo.name + "')")
            log(result)
            fileinfo.close()
        log(str(next_event))#}}}

    def quit(self, *args):#{{{
        log('quitting.')
        self.vm.vm.dispose()
        sys.exit(0)#}}}

    def printclasses(self, *args):#{{{
        for c in self.vm.vm.allClasses():
            try: sourcename = c.sourceName()
            except: sourcename = "(unknown)"
            log(c.name() + ' ' + sourcename)#}}}

    def resume(self, *args):
        self.vm.vm.resume()

    def add_breakpoint(self, *args):#{{{
        log('add breakpoint: ' + ','.join(args))
        filename, linenumber = args[0], int(args[1])
        classes = get_classrefs_from_filename(self.vm.vm, args[0])
        log(classes)
        if len(classes) == 1:
            locs = [l for l in classes[0].allLineLocations() if l.lineNumber()==linenumber]
            log(locs)
            if locs:
                bp_req = self.vm.vm.eventRequestManager().createBreakpointRequest(locs[0])
                bp_req.setSuspendPolicy(EventRequest.SUSPEND_NONE)
                bp_req.enable()
                log('added breakpoint.')#}}}

    def clearall_breakpoints(self, *args):#{{{
        self.vm.vm.eventRequestManager().deleteAllBreakPoints()
        log('clearall breakpoint: ' + ','.join(args))#}}}

    def clear_breakpoint(self, *args):#{{{
        log('clear breakpoint: ' + ','.join(args))#}}}

    def handle_command(self, command):#{{{
        log(command)
        commandargs = command.split('|')
        commandfunc = None
        try:
            if commandargs: commandfunc = self.commands.get(commandargs[0],None)
            if commandfunc: commandfunc(*commandargs[1:])
            else: log("received unknown command: " + ','.join(commandargs))
        except Exception:
            log(traceback.format_exc())
        except Throwable, t:
            log(t.getMessage()) #}}}

    def send_vim_keys(self, keys):#{{{
        os.system( 'gvim --servername %s --remote-send "%s"' % (self.session_id, keys) )#}}}

    def eval_vim_command(self, command):#{{{
        try:
            child = os.popen( 'gvim --servername %s --remote-expr "%s"' % (self.session_id, command) )
            return child.read()
        except:
            return None#}}}
    
class CommandReader(Runnable):
    def __init__(self, filename, callback):#{{{
        self.filename = filename
        self.callback    = callback
        self.stopflag    = False#}}}
    
    def run(self):#{{{
        log( "starting command thread" )
        while not self.stopflag:
            data = raw_input()
            self.callback(data)#}}}

class VirtualMachineEventHandler( Runnable ):

    def __init__(self, vm, dbi):#{{{
        self.queue = vm.eventQueue()
        self.stopflag = False
        self.mgr = vm.eventRequestManager()
        self.dbi = dbi
        cpr = self.mgr.createClassPrepareRequest()
        cpr.setSuspendPolicy(EventRequest.SUSPEND_NONE)
        cpr.enable()#}}}

    def run(self):#{{{
        while not self.stopflag:
            try:
                event_set = self.queue.remove()
                iter = event_set.eventIterator()
                while iter.hasNext():
                    nevent = iter.nextEvent()
                    self.dbi.vm_callback(nevent)
            except Exception, e:
                print str(e)
                log(str(e))
            except Throwable, t:
                print t.getMessage()
                log(t.getMessage())#}}}

def main(argv):#{{{
    if not argv: sys.exit(0)
    dbi = JavaVMDebugger(argv[0], argv[1])
    try:
        log("starting")
        dbi.cleanup()
        dbi.make_pipes()
        dbi.startdebugger()
        log("done")
    except Exception, e:
        print str(e)
        log(str(e))
    except Throwable, t:
        print t.getMessage()
        log(t.getMessage())
        dbi.cleanup()
        sys.exit(0)#}}}

def main(args):
    if args:
        session_id = args[0]
        debugger = Debugger( session_id )

if __name__ == '__main__':
    main(sys.argv[1:])
