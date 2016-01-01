from math import pi, sin, cos, tan, atan, log, exp
from functools import lru_cache, partial

from myvec import V3
from myarr import TList


class Data:

	def __init__(self):
		self.materials = TList(Material)
		self.scintillators = TList(Material)
		self.media = TList(Material)
		self.isotopes = TList(Isotope)
		self.find_isotope = partial(self.__find, self.isotopes)
		self.find_scintillator = partial(self.__find, self.scintillators)
		self.find_material = partial(self.__find, self.materials)
		self.find_medium = partial(self.__find, self.media)
		self.names_isotopes = partial(self.__names, self.isotopes)
		self.names_media = partial(self.__names, self.media)
		self.names_scintillators = partial(self.__names, self.scintillators)
		self.names_materials = partial(self.__names, self.materials)

	def flags_isotopes(self):
		flags = []
		for i in self.isotopes:
			flags += i.flags
		return set(flags)

	def names_isotopes_by_flag(self, flags):
		if not flags:
			return self.names_isotopes
		isotopes = self.isotopes
		for flag in flags:
			isotopes = [i for i in isotopes if flag in i.flags]
		return [i.name for i in isotopes]

	def __names(self, db):
		return [i.name for i in db]

	def __find(self, db, name):
		for item in db:
			if item.name == name:
				return item
		else:
			return None


class Detector:

	def __init__(self, *args):
		self.name, self.pos, self.q, self.d,\
			self.mat, self.d_cover, self.mat_cover = args
		self.r = (self.q / pi)**0.5
		self.average_path_in_scintillator = partial(
			self.__average_path, shift=self.d_cover, d=self.d)
		self.average_path_in_cover = partial(
			self.__average_path, shift=0, d=self.d_cover)

	def angular_size(self, point):
		x = self.pos**point
		ANGULAR = self.q / (4 * pi * x * x)
		return ANGULAR

	@lru_cache(maxsize=64)
	def __average_path(self, point, shift, d):

		def _path2_function(v):
			return self.r * (
				log(sin(v * .5) + cos(v * .5)) -
				log(cos(v * .5) - sin(v * .5))
			) - x / cos(v)

		if not d:
			return 0
		if not shift:
			shift = 0
		x = self.pos**point + shift
		p1 = atan(self.r / (d + x))
		p2 = atan(self.r / x)
		path1_integrate_0_p1 = d * log(self.r / (d + x) + (1 / cos(p1)))
		path1_average = path1_integrate_0_p1 / p1
		path2_integrate_p1_p2 = _path2_function(p2) - _path2_function(p1)
		path2_average = path2_integrate_p1_p2 / (p2 - p1)
		AVERAGE = path1_average * p1 / p2 + path2_average * (p2 - p1) / p2
		return AVERAGE


class Source():

	def __init__(self, *args):
		self.name, self.isotope, self.pos, self.m, self.d_cover,\
			self.mat_cover, self.activity_pre = args

	def activity(self):
		if self.activity_pre:
			return self.activity_pre
		na = 6.022 * 10**23
		A = (na * self.m / self.isotope.mu) * self.isotope.const
		return A

	def decays(self, t):
		if self.activity_pre:
			return self.activity_pre * t
		return int(self.activity() * t)

	def events(self, t):
		probs = [p for (e, p) in self.isotope.spectrum]
		return sum(probs) * self.decays(t)


class Isotope():

	def __init__(self, *args):
		self.name, self.flags, self.mu, self.half_life, self.spectrum = args
		self.const = log(2) / self.half_life


class Material():

	def __init__(self, *args):
		self.name, self.p, self.attenuations = args
		self.mass_attenuation = partial(self.__attenuation, ph=False)
		self.mass_photo_absorption = partial(self.__attenuation, ph=True)
		self.linear_attenuation = partial(
			self.__convert_to_linear, f=self.mass_attenuation)
		self.linear_photo_absorption = partial(
			self.__convert_to_linear, f=self.mass_photo_absorption)

	@lru_cache(maxsize=32)
	def __attenuation(self, e, ph=False):
		for i, (e1, k1, k2) in enumerate(self.attenuations[1:], 1):
			if ph:
				k1 = k2
				ii = 2
			else:
				ii = 1
			if e <= e1:
				e0, k0 = (
					self.attenuations[i - 1][0],
					self.attenuations[i - 1][ii]
				)
				if k1 <= k0:
					ke = (e1 - e) / (e1 - e0)
					ka = k1 + ke * (k0 - k1)
				elif i > 1:
					e00, k00 = (
						self.attenuations[i - 2][0],
						self.attenuations[i - 2][ii]
					)
					ke = (e - e0) / (e0 - e00)
					ka = max(k0 - ke * abs((k00 - k0)), 0)
				else:
					ke = (e - e0) / (e1 - e0)
					ka = k0 + ke * (k1 - k0)
				return ka
		else:
			return k1

	def __convert_to_linear(self, e, f):
		return self.p * f(e)


class Scene:

	def __init__(self, *args):
		self.detectors, self.sources, self.medium, self.t, self.bkg = args

	@lru_cache(maxsize=32)
	def average_path_in_medium(self, pos1, pos2, r):
		x = pos1**pos2
		p1 = atan(r / x)
		path_integrate_0_p1 = x * (
			log(sin(p1 * .5) + cos(p1 * .5)) -
			log(cos(p1 * .5) - sin(p1 * .5))
		)
		AVERAGE = path_integrate_0_p1 / p1
		return AVERAGE

	def G(self, det, source):
		return det.angular_size(source.pos)

	def I(self, det, source, e, simple=False):
		x3 = source.d_cover
		if simple:
			x1, x2 = det.pos**source.pos, det.d_cover
		else:
			x1 = self.average_path_in_medium(det.pos, source.pos, det.r)
			x2 = det.average_path_in_cover(source.pos)
		mu1 = self.medium.linear_attenuation(e)
		mu2 = det.mat_cover.linear_attenuation(e)
		mu3 = source.mat_cover.linear_attenuation(e)
		return exp(-(x1 * mu1 + x2 * mu2 + x3 * mu3))

	def M(self, det, source, e, simple=False):
		if simple:
			x = det.d
		else:
			x = det.average_path_in_scintillator(source.pos)
		mu = det.mat.linear_attenuation(e)
		mu2 = det.mat.linear_photo_absorption(e)
		M = 1 - exp(-(x * mu))
		Mph = 1 - exp(-(x * mu2))
		return M, Mph

	def get_detector_data(self, det, source, simple=False):
		BAND_DATA = []
		G = self.G(det, source)
		DEC = source.decays(self.t)
		N_TRUE = 0
		yN_TOTAL = 0
		for (e, p) in source.isotope.spectrum:
			I = self.I(det, source, e, simple)
			M, Mph = self.M(det, source, e, simple)
			E = G * I * M
			Eph = G * I * Mph
			yN = int(DEC * p)
			yN_TOTAL += yN
			N = int(E * yN)
			Nph = int(Eph * DEC * p)
			N_TRUE += N
			BAND_DATA.append((e, p, N, E, G, I, M, Nph, Eph, Mph))
		if source.events(self.t) == 0:
			EFFICIENCY = 1
		else:
			EFFICIENCY = N_TRUE / source.events(self.t)
		return source.name, int(N_TRUE), EFFICIENCY, DEC, yN_TOTAL, BAND_DATA

	def get_detector_data_from_all_sources(self, det, simple=False):
		N_TRUE = 0
		SOURCE_DATA = []
		for source in self.sources:
			data = self.get_detector_data(det, source, simple)
			N_TRUE += data[1]
			SOURCE_DATA.append(data)
		return N_TRUE, SOURCE_DATA

	def get_detector_events(self, det_id, simple=False):
		det = self.detectors[det_id]
		N_TRUE, SOURCE_DATA =\
			self.get_detector_data_from_all_sources(det, simple)
		return det.name, N_TRUE, SOURCE_DATA

	def get(self, simple=False):
		DATA = []
		for i, det in enumerate(self.detectors):
			DATA.append(self.get_detector_events(i, simple))
		return DATA
