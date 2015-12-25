#!/usr/bin/env python
from threading import Thread

from con import Console
from interface import Interface
from global_flags import GFLAGS

if __name__=="__main__":
	if GFLAGS.FLG_TKINTER:
		INTERFACE = Interface(GFLAGS)
	else:
		INTERFACE = None
	CON = Console(GFLAGS, INTERFACE)
	ThreadConsole = Thread(target=CON.run, daemon=True).start()
	if INTERFACE:
		INTERFACE.run()
	FLG_RUN = False