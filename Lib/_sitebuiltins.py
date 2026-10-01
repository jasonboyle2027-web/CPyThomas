"""
The objects used by the site module to add custom builtins.
"""

# Those objects are almost immortal and they keep a reference to their module
# globals.  Defining them in the site module would keep too many references
# alive.
# Note this means this module should also avoid keep things alive in its
# globals.

import sys

class Quitter(object):
    def __init__(self, name, eof):
        self.name = name
        self.eof = eof
    def __repr__(self):
        return 'Use %s() or %s to exit' % (self.name, self.eof)
    def __call__(self, code=None):
        # Shells like IDLE catch the SystemExit, but listen when their
        # stdin wrapper is closed.
        try:
            sys.stdin.close()
        except:
            pass
        raise SystemExit(code)


class _Printer(object):
    """interactive prompt objects for printing the license text, a list of
    contributors and the copyright notice."""

    MAXLINES = 23

    def __init__(self, name, data, files=(), dirs=()):
        import os
        self.__name = name
        self.__data = data
        self.__lines = []
        self.__filenames = [os.path.join(dir, filename)
                            for dir in dirs
                            for filename in files]

    def __setup(self):
        if self.__lines:
            return
        data = None
        for filename in self.__filenames:
            try:
                with open(filename, encoding='utf-8') as fp:
                    data = fp.read()
                break
            except OSError:
                pass
        if not data:
            data = self.__data
        self.__lines = data.split('\n')
        self.__linecnt = len(self.__lines)

    def __repr__(self):
        self.__setup()
        if len(self.__lines) <= self.MAXLINES:
            return "\n".join(self.__lines)
        else:
            return "Type %s() to see the full %s text" % ((self.__name,)*2)

    def __call__(self):
        from _pyrepl.pager import get_pager
        self.__setup()

        pager = get_pager()
        text = "\n".join(self.__lines)
        pager(text, title=self.__name)


class _Helper(object):
    """Define the builtin 'help'.

    This is a wrapper around pydoc.help that provides a helpful message
    when 'help' is typed at the Python interactive prompt.

    Calling help() at the Python prompt starts an interactive help session.
    Calling help(thing) prints help for the python object 'thing'.
    """

    def __repr__(self):
        return "Type help() for interactive help, " \
               "or help(object) for help about object."
    def __call__(self, *args, **kwds):
        import pydoc
        return pydoc.help(*args, **kwds)

# ====================================================================
# CUSTOM FORK ENTRANCE: CINEMATIC BOOT TYPEWRITER
# ====================================================================

import time
import sys

def run_intro():
    try:
        # 1. SEND ANSI ESCAPE CODES: Clear terminal window and snap cursor to top (0,0)
        # This forces the screen completely black instantly
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

        # 2. DEFINED SYNTAX PAYLOAD
        message = 'print("Hello, world!")\n'

        # 3. LIVE TYPEWRITER ITERATOR MATRIX
        for letter in message:
            sys.stdout.write(letter)
            sys.stdout.flush()
            time.sleep(0.3)  # Speed of the typing animation delay

        # Brief dramatic pause on the text frame layout
        time.sleep(1)

        # 4. CLEAR CANVAS AND PREPARE FOR APP LAUNCH
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write("=====================================================================\n")
        sys.stdout.write("APEX-FORCE CONTROL STUDIOS — CORE TERMINAL\n")
        sys.stdout.write("=====================================================================\n")
        sys.stdout.write("System status: SECURE RAM-SMASH ACTIVE\n")
        sys.stdout.write("=====================================================================\n\n")
        sys.stdout.flush()

    except Exception:
        # Failsafe: If anything goes wrong during startup, bypass quietly
        # so the standard terminal prompt doesn't brick entirely.
        pass

# Run the boot animation immediately as the platform prepares initialization frames
run_intro()
