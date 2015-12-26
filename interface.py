import os
import sys
from functools import partial
import tkinter as tk
from tkinter import filedialog as tkFileDialog

try:
	from numpy import random, zeros, ones
	import matplotlib
	matplotlib.use("TkAgg")
	from matplotlib import pyplot as plt
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
	from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
	from matplotlib.figure import Figure
	PLOT_ENABLE = True
except Exception as Err:
	print(Err)
	PLOT_ENABLE = False

class Interface:
	def __init__(self, gflags):
		self.sources, self.detectors = [], []
		self.gflags = gflags
		self.load_save = self.gflags.LOADER.load_save
		self.save_save = self.gflags.LOADER.save_save
		self.data = self.gflags.DATA
		self.data_loc = self.gflags.LOADER.parser['LOC']
		self.data_int = self.gflags.LOADER.parser['INTERFACE']
		self.template = os.path.join( os.path.dirname( __file__ ), 
			gflags.LOADER.parser['PATHS']['default_template'] )
		self.activity_det_types = [ self.data_loc['INT_STR_MASS'], 
									self.data_loc['INT_STR_ACTIVITY'] ]
		self.w = int( self.data_int.get('width', 1000) )
		self.h = int( self.data_int.get('height', 800) )
		self.bg = self.data_int.get('background', 'black')
		self.fg = self.data_int.get('foreground', 'orange')
		self.plot_enable = PLOT_ENABLE & \
							bool( int( self.data_int.get('plot', True) ) )
		self.plot_quality = int(self.data_int.get('plotsize', 100))
		self.plot_gauss_f = int(self.data_int['plot_gaussian_factor'])
		self.plot_fg = self.data_int.get('plot_fg', 'orange')
		self.plot_bg = self.data_int.get('plot_bg', 'black')
		self.plot_lg = self.data_int.get('plot_line_color', 'white')
		self.plot_linewidth = int(self.data_int.get('plot_linewidth', 0))
		self.plot_font_size = int(self.data_int.get('plot_font_size', 8))
		self.plot_font_color = self.data_int.get('plot_font_color', 'orange')
		self.plot_axis_color = self.data_int.get('plot_axis_color', 'orange')
		self.str_source_name = self.data_loc['INT_STR_SOURCE_NAMES']
		self.str_det_name = self.data_loc['INT_STR_DET_NAMES']
		self.str_plot_label_x = self.data_loc['INT_PLOT_LABEL_X']
		self.str_plot_label_y = self.data_loc['INT_PLOT_LABEL_Y']

		self.__find_detector = partial(self.__find, self.detectors)
		self.__find_source = partial(self.__find, self.sources)
		self.init_str = partial(self.__init_and_set, tk.StringVar)
		self.init_float = partial(self.__init_and_set, tk.DoubleVar)
		self.init_bool = partial(self.__init_and_set, tk.BooleanVar)
		self.init_int = partial(self.__init_and_set, tk.IntVar)

		self.root, self.frame = self.__init_root()
		self.__init_widget_vars()
		self.__init_widgets()
		self.__init_menus()

		self.c_action_load(self.template)

	def run(self):
		self.root.mainloop()
		
	def __init_root(self):
		ROOT = tk.Tk()
		ROOT.resizable(False, False)
		ROOT.configure( bg=self.bg )
		FRAME = tk.Frame( master=ROOT, bg=self.bg )
		x = ( ROOT.winfo_screenwidth() - self.w ) // 2
		y = ( ROOT.winfo_screenheight() - self.h ) // 2
		ROOT.geometry( '%dx%d+%d+%d' % ( self.w, self.h, x, y ) )
		FRAME.pack()
		return ROOT, FRAME

	def __init_menus(self):
		menubar = tk.Menu(self.root)

		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label="Open", command=self.c_action_load)
		filemenu.add_command(label="Save", command=self.c_action_save)
		filemenu.add_command(label="Exit", command=None)
		menubar.add_cascade(label='File', menu=filemenu)

		optmenu = tk.Menu(menubar, tearoff=0)
		optmenu.add_command(label="Plots Enabled", command=None)
		optmenu.add_command(label="Console Output", command=None)
		optmenu.add_command(label="Help", command=None)
		menubar.add_cascade(label='Options', menu=optmenu)

		self.root.config(menu=menubar)

	def __init_and_set(self, tk_var_type, var_name, default, scale):
		value = tk_var_type()
		value.set(default)
		setattr(self, var_name, value)
		if scale:
			setattr(self, '{}_scale'.format(var_name), scale)

	def __init_widget_vars(self):
		self.init_str('w_v_medium_type', 
						self.data.names_media()[0], None)
		self.init_str('w_v_source_type', 
						default=self.data.names_isotopes()[0], 
						scale=None)
		self.init_str('w_v_detector_cover_type', 
						default=self.data.names_materials()[0], 
						scale=None)
		self.init_str('w_v_source_cover_type', 
						default=self.data.names_materials()[0], 
						scale=None)
		self.init_str('w_v_scintillator_type', 
						default=self.data.names_scintillators()[0], 
						scale=None)
		self.init_float('w_v_scintillator_width', default=1, scale=1)
		self.init_float('w_v_detector_cover_width', default=0.1, scale=1)
		self.init_float('w_v_source_cover_width', default=0.1, scale=1)
		self.init_float('w_v_scintillator_q', default=100, scale=1)
		self.init_float('w_v_source_mass', default=1, scale=10**-9)
		self.init_str('w_v_source_activity_det', 
						default=self.activity_det_types[0], 
						scale=10**6)
		#positions
		self.init_float('w_v_source_x_pos', default=0, scale=100)
		self.init_float('w_v_detector_x_pos', default=1, scale=100)
		#experiment
		self.init_float('w_v_exposition', default=300, scale=1)
		#prefs
		self.init_float('w_v_energy_res', default=10, scale=0.01)
		#ADC
		self.init_int('w_v_adc_channels', default=64, scale=None)
		self.init_float('w_v_adc_threshold', default=0.05, scale=None)
		self.init_float('w_v_adc_max', default=3.0, scale=None)

	def __init_widgets(self):
		#source widgets
		x, y = 0, 0
		self.__create_label(x+1, y, 3, 1, self.data_loc['INT_LBL_SOURCES'])
		self.w_list_sources = self.__create_listbox(x+1, y+1, 3, 1, 
			self.c_action_select_source)
		self.w_btn_add_source = self.__create_button(x+1, y+2, 1, 1, 
			self.data_loc['INT_BTN_ADD'], self.c_action_add_source)
		self.w_btn_edit_source = self.__create_button(x+2, y+2, 1, 1, 
			self.data_loc['INT_BTN_MOD'], self.c_action_edit_source)
		self.w_btn_del_source = self.__create_button(x+3, y+2, 1, 1, 
			self.data_loc['INT_BTN_DEL'], self.c_action_del_source)
		self.w_opt_source_isotope = self.__create_option(x+1, y+4, 1, 1, 
			self.w_v_source_type, self.data.names_isotopes())
		self.w_opt_source_activity_det = self.__create_option(x+2, y+4, 1, 1, 
			self.w_v_source_activity_det, self.activity_det_types)
		self.w_txt_source_mass = self.__create_textbox(x+3, y+4, 1, 1, 
			self.w_v_source_mass)
		self.w_medium_type = self.__create_option(x+1, y+5, 1, 1, 
			self.w_v_medium_type, self.data.names_media())
		self.__create_label(x+2, y+5, 1, 1, self.data_loc['INT_LBL_POS'])
		self.w_txt_source_pos = self.__create_textbox(x+3, y+5, 1, 1, 
			self.w_v_source_x_pos)
		self.w_opt_source_cover = self.__create_option(x+1, y+6, 1, 1, 
			self.w_v_source_cover_type, self.data.names_materials())
		self.__create_label(x+2, y+6, 1, 1, 
			self.data_loc['INT_LBL_COV_WIDTH'])
		self.w_txt_source_cover_width = self.__create_textbox(x+3, y+6, 1, 1, 
			self.w_v_source_cover_width)
		#detector widgets
		x, y = 3, 0
		self.__create_label(x+1, y, 3, 1, self.data_loc['INT_LBL_DETECTORS'])
		self.w_list_detectors = self.__create_listbox(x+1, y+1, 3, 1, 
			self.c_action_select_detector)
		self.w_btn_add_detector = self.__create_button(x+1, y+2, 1, 1, 
			self.data_loc['INT_BTN_ADD'], self.c_action_add_detector)
		self.w_btn_edit_detector = self.__create_button(x+2, y+2, 1, 1, 
			self.data_loc['INT_BTN_MOD'], self.c_action_edit_detector)
		self.w_btn_del_detector = self.__create_button(x+3, y+2, 1, 1, 
			self.data_loc['INT_BTN_DEL'], self.c_action_del_detector)
		self.w_opt_detector = self.__create_option(x+1, y+4, 1, 1, 
			self.w_v_scintillator_type, self.data.names_scintillators())
		self.__create_label(x+2, y+4, 1, 1, self.data_loc['INT_LBL_Q'])
		self.w_txt_scintillator_q = self.__create_textbox(x+3, y+4, 1, 1, 
			self.w_v_scintillator_q)
		self.__create_label(x+2, y+5, 1, 1, self.data_loc['INT_LBL_POS'])
		self.w_txt_detector_pos = self.__create_textbox(x+3, y+5, 1, 1, 
			self.w_v_detector_x_pos)
		self.w_opt_detector_cover = self.__create_option(x+1, y+6, 1, 1, 
			self.w_v_detector_cover_type, self.data.names_materials())
		self.__create_label(x+2, y+6, 1, 1, 
			self.data_loc['INT_LBL_COV_WIDTH'])
		self.w_txt_detector_cover_width = self.__create_textbox(x+3, y+6, 1, 1, 
			self.w_v_detector_cover_width)
		self.__create_label(x+2, y+7, 1, 1, self.data_loc['INT_LBL_WIDTH'])
		self.w_txt_scintillator_width = self.__create_textbox(x+3, y+7, 1, 1, 
			self.w_v_scintillator_width)
		self.__create_label(x+2, y+9, 1, 1, 
			self.data_loc['INT_LBL_ENERGY_RES'])
		self.w_txt_resolution = self.__create_textbox(x+3, y+9, 1, 1, 
			self.w_v_energy_res)
		#other widgets
		x, y = 0, 9
		self.__create_label(x+1, y, 1, 1, self.data_loc['INT_LBL_EXP'])
		self.w_txt_exposition = self.__create_textbox(x+2, y, 1, 1, 
			self.w_v_exposition)
		self.__create_label(x+3, y, 1, 1, 
			self.data_loc['INT_LBL_ADC_CHANNELS'])
		self.w_txt_adc_ch = self.__create_textbox(x+4, y, 1, 1, 
			self.w_v_adc_channels)
		self.__create_label(x+1, y+1, 1, 1, 
			self.data_loc['INT_LBL_ADC_THRESHOLD'])
		self.w_txt_adc_thr = self.__create_textbox(x+2, y+1, 1, 1, 
			self.w_v_adc_threshold)
		self.__create_label(x+3, y+1, 1, 1, 
			self.data_loc['INT_LBL_ADC_RANGE'])
		self.w_txt_adc_max = self.__create_textbox(x+4, y+1, 1, 1, 
			self.w_v_adc_max)
		#actions
		x, y = 0, 9
		self.w_btn_simulate = self.__create_button(x+5, y+1, 2, 1, 
			self.data_loc['INT_BTN_SIMULATE'], self.c_action_simulate)

	def update_list_sources(self):
		self.w_list_sources.delete(0, tk.END)
		cursor = 0
		for s in self.sources:
			name, isotope, m, d_cover, mat_cover, pos, activity = s
			if not m:
				m = activity / self.w_v_source_activity_det_scale
				var = self.activity_det_types[1][-4:-1]
			else:
				m = m / self.w_v_source_mass_scale
				var = self.activity_det_types[0][-4:-1]
			s[0] = self.str_source_name.format(cursor, 
				isotope.name, m, var, mat_cover.name, 
				d_cover / self.w_v_source_cover_width_scale, 
				pos[2] / self.w_v_source_x_pos_scale)
			self.w_list_sources.insert(cursor, s[0])
			cursor += 1

	def update_list_detectors(self):
		self.w_list_detectors.delete(0, tk.END)
		cursor = 0
		for s in self.detectors:
			name, pos, q, d, mat, d_cover, mat_cover = s
			s[0] = self.str_det_name.format(cursor, mat.name, 
				q / self.w_v_scintillator_q_scale, 
				d / self.w_v_scintillator_width_scale, 
				mat_cover.name, 
				d_cover / self.w_v_detector_cover_width_scale, 
				pos[2] / self.w_v_detector_x_pos_scale)
			self.w_list_detectors.insert(cursor, s[0])
			cursor += 1

	def __find(self, db, name):
		for i, d in enumerate(db):
			if d[0]==name:
				return i, d
		else:
			return None

	def c_action_select_detector(self, event):
		try:
			name = self.w_list_detectors.get(self.list_layers.curselection())
		except:
			name = self.w_list_detectors.get(tk.ACTIVE)
		return name

	def c_action_select_source(self, event):
		try:
			name = self.w_list_sources.get(self.list_layers.curselection())
		except:
			name = self.w_list_sources.get(tk.ACTIVE)
		return name

	def __update_lists(f):

		def wrapper(self, *args, **kws):
			values = f(self, *args, **kws)
			self.update_list_sources()
			self.update_list_detectors()
			return values

		return wrapper

	def __create_detector(self, name, pos, q, d, mat, d_cover, mat_cover):
		mat = self.data.find_scintillator( mat )
		mat_cover = self.data.find_material( mat_cover )
		return [ name, pos, q, d, mat, d_cover, mat_cover ]

	
	def __create_source(self, name, isotope, m, d_cover, 
						mat_cover, pos, activity):
		isotope = self.data.find_isotope( isotope )
		mat_cover = self.data.find_material( mat_cover )
		return [ name, isotope, m, d_cover, mat_cover, pos, activity ]

	def __use_source_int_data(self):
		name = ''
		isotope = self.w_v_source_type.get()
		mat_cover = self.w_v_source_cover_type.get()
		pos = ( 0, 0, 
				self.w_v_source_x_pos.get() * self.w_v_source_x_pos_scale )
		d_cover = ( self.w_v_source_cover_width.get() * 
					self.w_v_source_cover_width_scale )
		if self.w_v_source_activity_det.get()==self.activity_det_types[0]:
			m = self.w_v_source_mass.get() * self.w_v_source_mass_scale
			activity = None
		else:
			m = None
			activity = ( self.w_v_source_mass.get() * 
						self.w_v_source_activity_det_scale )
		return [ name, isotope, m, d_cover, mat_cover, pos, activity ]

	def __use_detector_int_data(self):
		name = ''
		mat = self.w_v_scintillator_type.get()
		mat_cover = self.w_v_detector_cover_type.get()
		pos = (0, 0, 
				self.w_v_detector_x_pos.get() * self.w_v_detector_x_pos_scale)
		q = self.w_v_scintillator_q.get() * self.w_v_scintillator_q_scale
		d = ( self.w_v_scintillator_width.get() * 
				self.w_v_scintillator_width_scale )
		d_cover = ( self.w_v_detector_cover_width.get() * 
					self.w_v_detector_cover_width_scale )
		return [ name, pos, q, d, mat, d_cover, mat_cover ]
	
	@__update_lists
	def c_action_add_detector(self, event):
		d = self.__create_detector(*self.__use_detector_int_data())
		self.detectors.append(d)

	@__update_lists
	def c_action_add_source(self, event):
		s = self.__create_source(*self.__use_source_int_data())
		self.sources.append(s)

	@__update_lists
	def c_action_edit_detector(self, event):
		i, d = self.__find_detector(self.c_action_select_detector(None))
		args = self.__use_detector_int_data()
		self.detectors[i] = self.__create_detector(*args)

	@__update_lists
	def c_action_edit_source(self, event):
		i, d = self.__find_source(self.c_action_select_source(None))
		args = self.__use_source_int_data()
		self.sources[i] = self.__create_source(*args)

	@__update_lists
	def c_action_del_detector(self, event):
		i, d = self.__find_detector(self.c_action_select_detector(None))
		del self.detectors[i]

	@__update_lists
	def c_action_del_source(self, event):
		i, s = self.__find_source(self.c_action_select_source(None))
		del self.sources[i]

	def c_action_save(self):
		dlg = tkFileDialog.asksaveasfilename()
		if dlg:
			dlg = '{}.{}'.format(dlg, 'scene')
			s_args, d_args = [], []
			for args in self.sources:
				name, isotope, m, d_cover, mat_cover, pos, activity = args
				isotope, mat_cover, pos = isotope.name, mat_cover.name, pos[2]
				args = [name, isotope, m, d_cover, mat_cover, pos, activity]
				s_args.append(args)
			for args in self.detectors:
				name, pos, q, d, mat, d_cover, mat_cover = args
				mat, mat_cover, pos = mat.name, mat_cover.name, pos[2]
				args = [name, pos, q, d, mat, d_cover, mat_cover]
				d_args.append(args)
			self.save_save(dlg, d_args, s_args)

	@__update_lists
	def c_action_load(self, filepath=None):
		if not filepath:
			ftypes = [ ('Scene files', '*.scene'), 
						('.txt files', '*.txt'), 
						('All files', '*') ]
			dlg = tkFileDialog.Open(self.frame, filetypes=ftypes)
			fl = dlg.show()
		else:
			fl = filepath
		if fl!='':
			detectors, sources = self.load_save(fl)
			self.detectors = [ self.__create_detector(*d) for d in detectors ]
			self.sources = [ self.__create_source(*s) for s in sources ]
			self.__find_detector = partial(self.__find, self.detectors)
			self.__find_source = partial(self.__find, self.sources)

	def c_action_simulate(self, event):
		self.gflags.BUF_DETECTORS = self.detectors
		self.gflags.BUF_SOURCES = self.sources
		self.gflags.BUF_EXPOSITION = ( self.w_v_exposition.get() * 
										self.w_v_exposition_scale )
		med_name = self.w_v_medium_type.get()
		self.gflags.BUF_MEDIUM_TYPE = self.data.find_medium(med_name)
		self.gflags.FLG_SIMULATE = True

	def plot(self):

		def __load_interface_data():
			channels = self.w_v_adc_channels.get()
			discr = self.w_v_adc_threshold.get()
			rng = self.w_v_adc_max.get()
			if str(channels).endswith('bit'):
				channels = 2**int(channels[:-3])
			e_res_ref = self.w_v_energy_res.get() * self.w_v_energy_res_scale
			e_ref = 0.6617
			return channels, discr, rng, e_res_ref, e_ref

		def __create_graph_window(title):

			def __init__plot_area():
				f = Figure(figsize=(5, 4), dpi=self.plot_quality, 
							facecolor=self.plot_bg, edgecolor=self.plot_fg)
				canvas = FigureCanvasTkAgg(f, master=t)
				canvas.show()
				canvas.get_tk_widget().pack(side=tk.TOP, 
											fill=tk.BOTH, 
											expand=1)
				toolbar = NavigationToolbar2TkAgg(canvas, t)
				toolbar.update()
				canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
				return f, canvas

			t = tk.Toplevel(self.frame)
			t.wm_title(title)
			return __init__plot_area()

		def __draw_single(name, channels, discr, rng, yr):
			f, canvas = __create_graph_window(name)
			mpl_graph = f.add_subplot(111)
			mpl_graph.bar( range(channels), yr, color=self.plot_fg, 
							edgecolor=self.plot_lg, 
							linewidth=self.plot_linewidth)
			mpl_graph.tick_params(axis='both', which='major', 
									labelsize=self.plot_font_size, 
									color=self.plot_axis_color, 
									labelcolor=self.plot_font_color)
			mpl_graph.set_title(name, fontsize=self.plot_font_size, 
								color=self.plot_font_color)
			mpl_graph.set_axis_bgcolor(self.plot_bg)
			mpl_graph.set_ylabel(self.str_plot_label_y, 
									fontsize=self.plot_font_size, 
									color=self.plot_font_color)
			mpl_graph.spines['bottom'].set_color(self.plot_axis_color)
			mpl_graph.spines['left'].set_color(self.plot_axis_color)
			mpl_graph.spines['top'].set_color('none')
			mpl_graph.spines['right'].set_color('none')
			mpl_graph.xaxis.set_ticks_position('bottom')
			mpl_graph.yaxis.set_ticks_position('left')
			s = self.str_plot_label_x.format(channels, discr, rng)
			mpl_graph.set_xlabel(s, fontsize=self.plot_font_size, 
									color=self.plot_font_color)
			mpl_graph.set_xlim(0, channels)
			mpl_graph.set_ylim( 0, 5 + max(yr) * 1.2 )
			canvas.draw()

		def __plot_single(xy_data, N_YC, DX, CHANNELS, 
							DISCR, G_FACTOR, E_RES_REF, E_REF):

			def __compton_scattering(X, YC):
				i = int( X / DX )
				comptons = ones(i, float) / range(1, i+1)
				c_sum = sum(comptons)
				comptons = comptons / c_sum
				for i, c in enumerate(comptons):
					if i * DX > DISCR:
						dy = int(c * YC)
						if dy==0:
							break
						YR[i] += dy

			def __gauss_plot(X, Y):
				E_RES = E_RES_REF * ( E_REF / X )**0.5
				val = random.normal(X, E_RES, G_FACTOR )
				dy = Y // G_FACTOR
				for vv in val:
					if vv > DISCR:
						i = int( vv / DX )
						if i < CHANNELS:
							YR[i] += dy
						else:
							YR[-1] += dy

			def __delta_plot(X, Y):
				if X > DISCR:
					i = int( X / DX )
					if i < CHANNELS:
						YR[i] += Y
					else:
						YR[-1] += Y
			
			YR = zeros(channels, int)
			for X, Y, YC in xy_data:
				if G_FACTOR > 1 and E_RES_REF and Y > 3:
					__gauss_plot(X, Y)
				else:
					__delta_plot(X, Y)
				__compton_scattering(X, YC)
			return tuple(YR)

		if not self.plot_enable:
			return None
		plot_data = self.gflags.BUF_PLOT_DATA
		channels, discr, rng, e_res_ref, E_ref = __load_interface_data()
		dx = rng / channels
		gauss_factor = channels // self.plot_gauss_f
		for v in plot_data:
			name, xval, yval, ycval, n_yc = v
			values = __plot_single( zip(xval, yval, ycval), n_yc, dx, channels, 
									discr, gauss_factor, e_res_ref, E_ref)
			__draw_single( name, channels, discr, rng, values )
		self.gflags.BUF_PLOT_DATA = None
	
	def __dec_setpos(f):

		def wrapper(self, x, y, w, h, *args, **kws):
			wg = f(self, *args, **kws)
			wg.grid(row=y, column=x, rowspan=h, columnspan=w, sticky=tk.NSEW)
			return wg

		return wrapper

	@__dec_setpos
	def __create_listbox(self, command=None):
		wg = tk.Listbox(self.frame, bd=0, selectmode=tk.SINGLE, 
						fg=self.fg, bg=self.bg)
		wg.bind('<<ListboxSelect>>', command)
		return wg

	@__dec_setpos
	def __create_textbox(self, textvar=None):
		return tk.Entry(self.frame, bd=0, textvariable=textvar,
						fg=self.fg, bg=self.bg, 
						highlightbackground=self.bg, highlightcolor=self.fg)

	@__dec_setpos
	def __create_label(self, text, textvar=None):
		return tk.Label(self.frame, text=text, textvariable=textvar, 
						fg=self.fg, bg=self.bg)

	@__dec_setpos
	def __create_option(self, variable, options, command=None):
		wg = tk.OptionMenu(self.frame, variable, *options)
		wg.bind('<Leave>', command)
		return wg

	@__dec_setpos
	def __create_checkbutton(self, text, variable):
		return tk.Checkbutton(self.frame, text=text, variable=variable,
								highlightbackground=self.bg, 
								highlightcolor=self.fg)

	@__dec_setpos
	def __create_button(self, text, command=None):
		wg = tk.Button(self.frame, text=text, fg=self.fg, bg=self.bg, 
						highlightbackground=self.bg, 
						highlightcolor=self.fg)
		wg.bind('<Button-1>', command)
		return wg