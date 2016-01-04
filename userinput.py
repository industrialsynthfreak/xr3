import re

from functools import partial


class UserInput:

	def __init__(self, gflags):
		self.scale_source = []
		self.scale_det = []
		self.def_values_source = [1, 0.1, 0, None]
		self.def_values_det = [1, 100, 1, 0.1]
		self.gflags = gflags
		self.data = self.gflags.DATA
		self.data_loc = self.gflags.LOADER.parser['LOC']
		self.regexp = re.compile('\S+')
		self.detectors = []
		self.sources = []
		self.medium = None
		self.c_isotope_table = partial(
			self.__namespace_search,
			self.data.names_isotopes()
		)
		self.c_scintillator_table = partial(
			self.__namespace_search,
			self.data.names_scintillators()
		)
		self.c_media_table = partial(
			self.__namespace_search,
			self.data.names_media()
		)
		self.c_materials_table = partial(
			self.__namespace_search,
			self.data.names_materials()
		)

		self.commands = {
			'quit': (
				self.c_quit,
				self.data_loc['NOGUI_STR_QUIT']
			),
			'is': (
				self.c_isotope_table,
				self.data_loc['NOGUI_STR_IS']
			),
			'sc': (
				self.c_scintillator_table,
				self.data_loc['NOGUI_STR_SC']
			),
			'ma': (
				self.c_materials_table,
				self.data_loc['NOGUI_STR_MA']
			),
			'me': (
				self.c_media_table,
				self.data_loc['NOGUI_STR_ME']
			),
			'help': (
				self.c_help,
				self.data_loc['NOGUI_STR_HELP']
			),
			'setm': (
				self.c_set_medium,
				self.data_loc['NOGUI_STR_SETM']
			),
			'adds': (
				self.c_add_source,
				self.data_loc['NOGUI_STR_ADDS']
			),
			'addd': (
				self.c_add_detector,
				self.data_loc['NOGUI_STR_ADDD']
			),
			'ls': (
				self.c_list,
				self.data_loc['NOGUI_STR_LS']
			),
		}

	def __namespace_search(self, db, *args):
		if args[0]:
			key = args[0].lower()
			for name in db:
				if name.lower().startswith(key):
					print(name)
		else:
			print(db)

	def run(self):
		self.__intro()
		self.__set_default_values()
		while self.gflags.FLG_RUN:
			self.parse_user_input(input())

	def parse_user_input(self, arg):
		args = self.regexp.findall(arg) + [None]
		f = self.commands.get(args[0], (self.__no_such_cmd,))[0]
		return f(*args[1:])

	def c_help(self, *args):
		s = self.data_loc['NOGUI_STR_HELP_OUTPUT'] + '\n'
		for c in self.commands:
			print(s.format(c, self.commands[c][1]))

	def c_quit(self, *args):
		self.gflags.FLG_RUN = False

	def c_list(self, *args):

		def __list_d():
			_s = self.data_loc['NOGUI_STR_LS_D']
			for i, d in enumerate(self.detectors):
				name, pos, q, d, mat, d_cover, mat_cover = d
				mat = mat.name
				mat_cover = mat_cover.name
				print(_s.format(
					i, mat, d, d_cover, mat_cover, q, pos))

		def __list_s():
			_s = self.data_loc['NOGUI_STR_LS_S']
			for i, s in enumerate(self.sources):
				name, isotope, m, d_cover, mat_cover, pos, activity = s
				if activity:
					units = 'Mbk'
					m = activity
				else:
					units = 'ng'
				isotope = isotope.name
				mat_cover = mat_cover.name
				print(_s.format(
					i, isotope, m, units, d_cover, mat_cover, pos))

		def __list_other():
			print(self.medium)

		if args[0] == 'd':
			__list_d()
		elif args[0] == 's':
			__list_s()
		else:
			__list_other()
			__list_s()
			__list_d()

	def c_add_detector(self, *args):
		args = (args[:-1] + ('*',) * 6)[:6]
		mat, q, d, d_cover, mat_cover, pos = args
		values = [pos, q, d, d_cover]
		for i, v in enumerate(values):
			if v == '*':
				values[i] = self.def_values_det[i]
			else:
				try:
					values[i] = float(v)
				except:
					print(self.data_loc['NOGUI_STR_INVALID_INPUT'].format(v))
					return
		pos, q, d, d_cover = values
		if mat and mat.capitalize() in self.data.names_scintillators():
			mat = self.data.find_scintillator(mat)
		else:
			mat = self.data.scintillators[0]
		if mat_cover and mat_cover in self.data.names_materials():
			mat_cover = self.data.find_material(mat_cover)
		else:
			mat_cover = self.data.materials[0]
		name = ''
		d = [name, pos, q, d, mat, d_cover, mat_cover]
		self.detectors.append(d)

	def c_add_source(self, *args):
		args = (args[:-1] + ('*',) * 6)[:6]
		isotope, m, d_cover, mat_cover, pos, activity = args
		values = [m, d_cover, pos, activity]
		for i, v in enumerate(values):
			if v == '*':
				values[i] = self.def_values_source[i]
			else:
				try:
					values[i] = float(v)
				except:
					print(self.data_loc['NOGUI_STR_INVALID_INPUT'].format(v))
					return
		m, d_cover, pos, activity = values
		if activity is not None:
			m = None
		if isotope and isotope.capitalize() in self.data.names_isotopes():
			isotope = self.data.find_isotope(isotope)
		else:
			isotope = self.data.isotopes[0]
		if mat_cover and mat_cover in self.data.names_materials():
			mat_cover = self.data.find_material(mat_cover)
		else:
			mat_cover = self.data.materials[0]
		name = ''
		s = [name, isotope, m, d_cover, mat_cover, pos, activity]
		self.sources.append(s)

	def c_set_medium(self, *args):
		name = args[0]
		if name in self.data.names_media():
			self.medium = name
			print(self.data_loc['NOGUI_STR_MEDIUM_SET'].format(name))
		else:
			print(self.data_loc['NOGUI_STR_NO_MEDIUM'])

	def __set_default_values(self, *args):
		self.medium = self.data.names_media()[0]

	def __intro(self, *args):
		print(self.data_loc['NOGUI_STR_INTRO'])

	def __no_such_cmd(self, *args):
		print(self.data_loc['NOGUI_STR_NOCMDWARNING'])
