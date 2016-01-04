from mycls import Scene, Isotope, Material, Detector, Source
from loader import Loader
from myarr import TList
from myvec import V3


class ConstructDetector:

	def __init__(self):
		pass

	def __new__(self, name, pos, q, d, mat, d_cover, mat_cover):
		try:
			q = float(q)
			d = float(d)
			d_cover = float(d_cover)
			pos = V3(*pos)
		except Exception as err:
			print(err)
			return None
		if type(mat) != Material or type(mat_cover) != Material:
			return None
		if q <= 0 or d <= 0:
			return None
		DET = Detector(name, pos, q, d, mat, d_cover, mat_cover)
		return DET


class ConstructSource:

	def __init__(self):
		pass

	def __new__(self, name, isotope, m, d_cover, mat_cover, pos, activity):
		try:
			d_cover = float(d_cover)
			pos = V3(*pos)
			if activity:
				activity = float(activity)
			else:
				m = float(m)
		except Exception as err:
			return None
		if type(mat_cover) != Material or type(isotope) != Isotope:
			return None
		SOURCE = Source(name, isotope, pos, m, d_cover, mat_cover, activity)
		return SOURCE


class ConstructScene:

	def __init__(self):
		pass

	def __new__(self, detectors, sources, medium, t, bkg):
		try:
			t = float(t)
			bkg = float(bkg)
			detectors = TList(Detector, detectors)
			sources = TList(Source, sources)
		except Exception:
			return None
		if type(medium) != Material:
			return None
		SCENE = Scene(detectors, sources, medium, t, bkg)
		return SCENE
