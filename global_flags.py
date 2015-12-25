from loader import Loader

class GlobalFlags:
	def __init__(self):
		self.LOADER = Loader()
		self.DATA = self.LOADER.data
		self.FLG_RUN = True
		self.FLG_SIMULATE = False
		self.FLG_TKINTER =\
		 bool(self.LOADER.parser['INTERFACE'].get('tkinter', True))
		self.FLG_CONSOLE_OUTPUT_TYPE =\
		 self.LOADER.parser['INTERFACE'].get('console_output_type', 'FULL')
		self.reload_buffer()

	def reload_buffer(self):
		self.BUF_MEDIUM_TYPE = None
		self.BUF_EXPOSITION = None
		self.BUF_DETECTORS = None
		self.BUF_SOURCES = None
		self.BUF_PLOT_DATA = None


GFLAGS = GlobalFlags()