import os
from functools import partial
import configparser

from nist import parse_isotope_file, parse_material_file, parse_save_file
from mycls import Data

class Loader:

	def __init__(self):
		self.working_dir = os.path.dirname( __file__ )
		self.config_path = os.path.join( self.working_dir, 'config.ini' )
		self.parser = configparser.ConfigParser()
		self.parser.read( self.config_path )
		self.load_isotopes = partial( self.__load_folder, 'isotopes', 
			'.isotope', parse_isotope_file )
		self.load_media = partial( self.__load_folder, 'media', 
			'.mat', parse_material_file )
		self.load_scintillators = partial( self.__load_folder, 
			'scintillators', '.mat', parse_material_file )
		self.load_materials = partial( self.__load_folder, 'materials', 
			'.mat', parse_material_file )
		self.data = self.reload_data()

	def __load_folder(self, data_type, file_type, function):
		ARG_LIST = []
		folder_name = self.parser['PATHS'].get( data_type , None )
		if not folder_name:
			return None
		folder = os.path.join( self.working_dir, folder_name )
		filenames = [ f for f in os.listdir( folder ) 
						if f.endswith( file_type ) ]
		for name in filenames:
			path = os.path.join( folder, name )
			with open( path, 'r' ) as f:
				ARG_LIST.append( function( f.readlines() ) )
		return ARG_LIST

	def save_save(self, f, d_args, s_args):
		with open(f, 'w') as f:
			for args in s_args:
				f.write('\n[SOURCE]')
				for arg in args:
					f.write(str(arg)+'\t')
			for args in d_args:
				f.write('\n[DETECTOR]')
				for arg in args:
					f.write(str(arg)+'\t')

	def load_save(self, f):
		with open(f, 'r') as f:
			data = f.readlines()
		return parse_save_file(data)

	def reload_data(self):

			def __load(func, arr):
				args_list = func()
				if not args_list:
					return None
				for args in args_list:
					if args==None:
						continue
					arr.append( arr.value_type(*args) )

			DATA = Data()
			__load( self.load_isotopes, DATA.isotopes )
			__load( self.load_scintillators, DATA.scintillators )
			__load( self.load_materials, DATA.materials )
			__load( self.load_media, DATA.media )
			return DATA