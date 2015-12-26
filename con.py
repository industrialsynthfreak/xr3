from constructor import ConstructScene, ConstructSource, ConstructDetector

class Console:

	def __init__(self, gflags, interface):
		self.gflags = gflags
		self.interface = interface
		self.show =\
		 gflags.LOADER.parser['INTERFACE'].get('console_output_type', 'FULL')
		self.data_loc = gflags.LOADER.parser['LOC']

	def run(self):
		while self.gflags.FLG_RUN:
			if self.gflags.FLG_SIMULATE:
				self.gflags.FLG_SIMULATE = False
				data = self.simulate(self.gflags.BUF_DETECTORS, 
										self.gflags.BUF_SOURCES, 
										self.gflags.BUF_MEDIUM_TYPE, 
										self.gflags.BUF_EXPOSITION)
				self.gflags.BUF_PLOT_DATA = self.console_output(data)
				if self.interface:
					self.interface.plot()
				self.gflags.reload_buffer()

	def simulate(self, detectors, sources, medium, exposition):
		detectors = [ConstructDetector(*v) for v in self.gflags.BUF_DETECTORS]
		sources = [ConstructSource(*v) for v in sources]
		scene = ConstructScene(detectors, sources, medium, exposition, 1)
		DATA = scene.get()
		return DATA

	def console_output(self, data):

		def __empty_line_add():
			if self.show!='NONE':
				print('\n')

		def __border_add():
			if self.show!='NONE':
				print('-'*70)

		s_det = self.data_loc['CON_DET_LINE_OUT']
		s_source = self.data_loc['CON_SOURCE_LINE_OUT']
		s_line = self.data_loc['CON_E_LINE_OUT']
		PLOT_DATA = []
		__border_add()
		for det_name, ntotal, source_data in data:
			xval, yval, ycval = [], [], []
			sources_yc = 0
			G = source_data[0][5][0][4]
			if self.show!='NONE':
				print(s_det.format(det_name, ntotal, G * 100))
				__border_add()
				for source in source_data:
					name, true, eff, dec, yn_total, band_data = source
					print(s_source.format(name, true, dec/10**6, 
											yn_total/10**6, 
											G * yn_total/10**6, eff * 100))
					for band in band_data:
						e, p, N, E, G, I, M, Nph, Eph, Mph = band
						xval.append(e)
						yval.append(Nph)
						ycval.append(N-Nph)
						sources_yc += (N - Nph)
						if self.show=='FULL':
							print(s_line.format( e * 1000, p * 100, 
												N, E * 100, 
												100 - I * 100, M * 100., 
												Nph, Eph * 100.))
					__empty_line_add()
			__empty_line_add()
			PLOT_DATA.append( ( det_name, xval, yval, ycval, sources_yc ) )	
		return PLOT_DATA