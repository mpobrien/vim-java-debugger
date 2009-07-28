import sys, os
import re
from java.lang import Runnable, Thread, Throwable
from jvm_interface import VMConnection



def walk( dir, process ):
    '''walk a directory tree'''
    for f in os.listdir( dir ):
        fullpath = os.path.join( dir, f)
        if os.path.isdir( fullpath ) and not os.path.islink ( fullpath ):
            walk( fullpath, process )
        if os.path.isfile( fullpath ):
            process( fullpath )

class DebuggerShell:

    def __init__( self ):#{{{
        self.vm_connection = None
        self.command_processor = CommandProcessor( self )
        self.sourcefiles = [] #}}}

    def run_shell( self ):#{{{
        while True:
            print ">>> ", 
            try:
                command = raw_input()
                self.command_processor.decode_command( command )
            except EOFError:
                self.quit()#}}}

    def quit( self, *args ):#{{{
        if self.vm_connection:
            self.vm_connection.close()
        print ""
        sys.exit( 0 )#}}}


    def sourcedir(self, *args):#{{{
        """ Crawl a directory to add to the list of sources """
        if not args:
            print len(self.sourcefiles), " source files loaded"
        else:
            def processor(s):
                if s.lower().endswith('.java'):
                    print "Loading " + s
                    self.sourcefiles.append(s)
            walk(args[0], processor)
            print "Added all .java files under " + args[0]#}}}


    def classes(self, *args):
        """
        Display a list of classes loaded on the connected JPDA host
        """
        if not self.vm_connection or not self.vm_connection.is_connected():
            print "not connected to a JPDA host"
            return
        classesList = self.vm_connection.vm.allClasses()
        for c in classesList:
            try: sourcename = c.sourceName()
            except: sourcename = "(unknown)"
            print c, sourcename
        print len(classesList), "classes loaded"


    def connect(self, *args):#{{{
        """
        connect <hostname> <port> 
        Connects to a JPDA host on the specified hostname and port 
        """
        try:
            hostname, port = args[0], args[1]
            self.vm_connection = VMConnection(hostname, port)
            print "Connected to JPDA host at %s on %s" % (hostname, port)
        except Exception, e:
            print "(py) Couldn't connect: ", e
        except Throwable, t:
            print "(j) Couldn't connect: ", t#}}}


class CommandProcessor:

    def __init__(self, shell):
        self.shell = shell

    def decode_command(self, command):#{{{
        if not command.strip(): return
        command_parts = re.split('\s*', command)
        if not command_parts:
            print "invalid input"
        if command_parts[0] in  ('exit', 'quit'):
            self.shell.quit()
        else:
            func_key = command_parts[0]
            if command_parts[0] == 'help': func_key = command_parts[1]
            command_func = None
            try:
                command_func = getattr( self.shell, func_key )
            except:
                command_func = None
            if not command_func:
                print "unknown command: ", command_parts[0]
            else:
                if command_parts[0] == 'help': print command_func.__doc__
                else: command_func(*command_parts[1:])#}}}


def main():
    shell_handler = DebuggerShell()
    shell_handler.run_shell()

if __name__ == '__main__': main()
