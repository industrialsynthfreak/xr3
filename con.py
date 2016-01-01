from constructor import ConstructScene, ConstructSource, ConstructDetector


class Console:

	def __init__(self, gflags, interface):
		self.gflags = gflags
		self.interface = interface
		self.data_loc = gflags.LOADER.parser['LOC']

	def run(self):
		while self.gflags.FLG_RUN:
			if self.gflags.FLG_SIMULATE:
				self.simulate()
				self.plot()
				self.gflags.reload_buffer()

	def simulate(self):
		self.gflags.FLG_SIMULATE = False
		detectors = [ConstructDetector(*v) for v in self.gflags.BUF_DETECTORS]
		sources = [ConstructSource(*v) for v in self.gflags.BUF_SOURCES]
		scene = ConstructScene(
			detectors,
			sources,
			self.gflags.BUF_MEDIUM_TYPE,
			self.gflags.BUF_EXPOSITION,
			1
		)
		self.gflags.BUF_PLOT_DATA = self.console_output(scene.get())

	def plot(self):
		if self.interface:
			self.interface.plot()

	def console_output(self, data):

		def __line_add(line):
			if self.gflags.LOADER.parser['INTERFACE']['console_output_type']\
				!= 'NONE':
				print(line)

		def __line_if_full(line):
			if self.gflags.LOADER.parser['INTERFACE']['console_output_type']\
				== 'FULL':
				print(line)

		def __det_print(args):
			det_name, ntotal, source_data = args
			xval, yval, ycval = [], [], []
			sources_yc = 0
			G = source_data[0][5][0][4]
			__line_add(s_det.format(det_name, ntotal, G * 100))
			__line_add('-' * 70)
			for source in source_data:
				name, true, eff, dec, yn_total, band_data = source
				__line_add(
					s_source.format(name, true, dec / 10**6, yn_total / 10**6,
									G * yn_total / 10**6, eff * 100)
				)
				for band in band_data:
					e, p, N, E, G, I, M, Nph, Eph, Mph = band
					xval.append(e)
					yval.append(Nph)
					ycval.append(N - Nph)
					sources_yc += (N - Nph)
					__line_if_full(
						s_line.format(e * 1000, p * 100, N, E * 100,
							100 - I * 100, M * 100., Nph, Eph * 100.)
					)
				__line_add('\n')
			__line_add('\n')
			return det_name, xval, yval, ycval, sources_yc

		s_det = self.data_loc['CON_DET_LINE_OUT']
		s_source = self.data_loc['CON_SOURCE_LINE_OUT']
		s_line = self.data_loc['CON_E_LINE_OUT']
		__line_add('-' * 70)
		return [__det_print(args) for args in data]
