#!/usr/bin/env python
from threading import Thread

from interface import *
from global_flags import GFLAGS
from constructor import *

data_loc = GFLAGS.LOADER.parser['LOC']

def simulate(detectors, sources, medium, exposition):
	detectors = [ ConstructDetector(*v) for v in detectors ]
	sources = [ ConstructSource(*v) for v in sources ]
	scene = ConstructScene(detectors, sources, medium, exposition, 1)
	DATA = scene.get()
	return DATA

def save(filepath):
	with open(filepath, 'w') as f:
		f.write(GFLAGS.BUF_DETECTORS)
		f.write(GFLAGS.BUF_SOURCES)
		
def console_output(data, show='FULL'):
	s_det = data_loc['CON_DET_LINE_OUT']
	s_source = data_loc['CON_SOURCE_LINE_OUT']
	s_line = data_loc['CON_E_LINE_OUT']
	PLOT_DATA = []
	for det_name, ntotal, source_data in data:
		xval, yval, ycval = [], [], []
		sources_yc = 0
		G = source_data[0][5][0][4]
		if show!='NONE':
			print(s_det.format(det_name, ntotal, G * 100))
		for source in source_data:
			name, true, eff, dec, yn_total, band_data = source
			if show!='NONE':
				print(s_source.format(name, true, dec/10**6, yn_total/10**6, 
										G * yn_total/10**6, eff * 100))
			for band in band_data:
				e, p, N, E, G, I, M, Nph, Eph, Mph = band
				if show=='FULL':
					print(s_line.format( e * 1000, p * 100, N, E * 100, 
										100 - I * 100, M * 100., 
										Nph, Eph * 100.))
				xval.append(e)
				yval.append(Nph)
				ycval.append(N-Nph)
			if show!='NONE':
				print('\n')
			sources_yc += (N - Nph)
		PLOT_DATA.append( ( det_name, xval, yval, ycval, sources_yc ) )	
	return PLOT_DATA

def console(*args):
	gflags, interface = args
	while gflags.FLG_RUN:
		if gflags.FLG_SIMULATE:
			gflags.FLG_SIMULATE = False
			data = simulate(gflags.BUF_DETECTORS, gflags.BUF_SOURCES, 
							gflags.BUF_MEDIUM_TYPE, gflags.BUF_EXPOSITION)
			gflags.BUF_PLOT_DATA = console_output(data, 
				gflags.FLG_CONSOLE_OUTPUT_TYPE)
			if interface:
				interface.plot()
			gflags.reload_buffer()

if __name__=="__main__":
	if GFLAGS.FLG_TKINTER:
		INTERFACE = Interface( GFLAGS )
	else:
		INTERFACE = None
	ThreadConsole = Thread( target=console, args=(GFLAGS, INTERFACE) )
	ThreadConsole.daemon = True
	ThreadConsole.start()
	if INTERFACE:
		INTERFACE.run()
	FLG_RUN = False
