#!/usr/bin/env python3
from threading import Thread

from con import Console
from userinput import UserInput
from interface import Interface
from global_flags import GFLAGS

__version__ = '1.0a2'

if __name__ == "__main__":
	if GFLAGS.FLG_TKINTER:
		INTERFACE = Interface(GFLAGS)
	else:
		INTERFACE = None
		INPUT = UserInput(GFLAGS)
	CON = Console(GFLAGS, INTERFACE)
	ThreadConsole = Thread(target=CON.run, daemon=True).start()
	if INTERFACE:
		INTERFACE.run()
	else:
		INPUT.run()
	FLG_RUN = False
