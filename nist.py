import re

_regex_default = re.compile('\S+')


def parse_save_file(filedata):
	detectors, sources = [], []
	for line in filedata:
		if line.startswith('[SOURCE]'):
			data = _regex_default.findall(line[len('[SOURCE]'):])
			name, isotope, m, d_cover, mat_cover, pos, activity = data
			pos = (0, 0, float(pos))
			if m.lower() == 'none':
				m = None
				activity = float(activity)
			else:
				activity = None
				m = float(m)
			d_cover = float(d_cover)
			args = name, isotope, m, d_cover, mat_cover, pos, activity
			sources.append(args)
		elif line.startswith('[DETECTOR]'):
			data = _regex_default.findall(line[len('[DETECTOR]'):])
			name, pos, q, d, mat, d_cover, mat_cover = data
			pos = (0, 0, float(pos))
			q = float(q)
			d = float(d)
			d_cover = float(d_cover)
			args = name, pos, q, d, mat, d_cover, mat_cover
			detectors.append(args)
	return detectors, sources


def parse_isotope_file(filedata):
	const_time = {'s': 1., 'm': 60., 'h': 3600., 'd': 86400., 'y': 31577600.}
	SPECTRUM = []
	try:
		header = _regex_default.findall(filedata.pop(0))
		NAME, MOLAR, HALF_LIFE = header[:3]
		FLAGS = header[3:]
		if HALF_LIFE[-1] in const_time:
			HALF_LIFE = const_time[HALF_LIFE[-1]] * float(HALF_LIFE[:-1])
		else:
			HALF_LIFE = float(HALF_LIFE)
		for line in filedata:
			band = _regex_default.findall(line)
			e, p = band[:2]
			SPECTRUM.append((float(e) * 0.001, float(p) * 0.01))
		return NAME, FLAGS, float(MOLAR), float(HALF_LIFE), SPECTRUM
	except Exception as err:
		print(err)
		return None


def parse_material_file(filedata):
	try:
		NAME, DENSITY = _regex_default.findall(filedata.pop(0))
		ATTENUATIONS = []
		k_ph = 0
		for line in filedata:
			_l = _regex_default.findall(line)
			e, k = float(_l[0]), float(_l[1])
			if len(_l) > 2:
				k_ph = float(_l[2])
			ATTENUATIONS.append((e, k, k_ph))
		_v1 = (0, ATTENUATIONS[0][1], ATTENUATIONS[0][2])
		_v2 = (float('inf'), ATTENUATIONS[-1][1], ATTENUATIONS[-1][2])
		ATTENUATIONS = [_v1] + ATTENUATIONS + [_v2]
		return NAME, float(DENSITY), ATTENUATIONS
	except Exception as err:
		print(err)
		return None
