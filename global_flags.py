from loader import Loader

class GlobalFlags:
	def __init__(self):
		self.reload_buffer()
		self.LOADER = Loader()
		self.DATA = self.LOADER.data
		self.FLG_RUN = True
		self.FLG_SIMULATE = False
		self.FLG_TKINTER = bool(int(self.LOADER.parser['INTERFACE']['tkinter']))

	def reload_buffer(self):
		self.BUF_MEDIUM_TYPE = None
		self.BUF_EXPOSITION = None
		self.BUF_DETECTORS = None
		self.BUF_SOURCES = None
		self.BUF_PLOT_DATA = None


GFLAGS = GlobalFlags()