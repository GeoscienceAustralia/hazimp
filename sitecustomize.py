import sys

def info(type, value, tb):
   if (hasattr(sys, "ps1") or
       not sys.stderr.isatty() or 
       not sys.stdin.isatty()):
       # stdin or stderr is redirected, just do the normal thing
       original_hook(type, value, tb)
   else:
       # a terminal is attached and stderr is not redirected, debug 
       import traceback, pdb
       traceback.print_exception(type, value, tb)
       print
       pdb.pm()
       #traceback.print_stack()

original_hook = sys.excepthook
if sys.excepthook == sys.__excepthook__:
    # if someone already patched excepthook, let them win
    sys.excepthook = info
