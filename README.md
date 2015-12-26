# Readme

## About

xr3 (x-ray 3) is a tool for modelling scintillator x-ray detector or detector array characteristics.
It was designed for educational purposes only.

## Physics

The program uses simple exponential attenuation formulae and tables of attenuation coefficients to determine x-ray absorption and detector efficiency values. No Monte-Carlo methods or obscure nuclear processes were taken into account.

## Requirements

- [python3](https://www.python.org) (tested on 3.5)
- [matplotlib](http://matplotlib.org) and [numpy](http://www.numpy.org) (only if you need plots)

## Platform support

Because it uses tkinter for the GUI, it's likely to run on any Mac, Windows or Linux computer. Tested on OSX 10.10. It can be compiled using cython (except interface.py module, I guess).

## How to use

Run the main script:

	python3 xr3.py

Default template will be automatically loaded from templates/default.scene file. You can overwrite this file or change 'default_template' value in config.ini to a custom path.
Set parameters you want. If you'd like to edit a particular detector/source, first adjust values, then select item in the list and press 'Rewrite'.
Press simulate.

### Source options

- Isotope
- Mass or activity (you cannot set both for obvious reasons)
- Absolute position (1D)
- Casing/moderator type
- Casing/moderator thickness

### Scintillator options

- Scintillator
- Cross-section
- Absolute position (1D)
- Casing/moderator type
- Casing/moderator thickness
- Scintillator thickness

### Experiment options

- Exposition time
- Number of ADC channels
- Detector energy resolution (sadly you should set it by yourself)
- ADC CFD threshold in MeV
- ADC max energy/ max signal in MeV

### What you can get

- Console data about all energy lines (events, efficiency, absorption values, etc.). If you just want some basic info about detector efficiency, in config.ini set 'console_output_type' to PARTIAL
- Modelled spectra (if matplotlib/numpy installed)
- Save detectors/isotope compositions and share them with your friends ( just joking, don't do that, I'm serious)

## Issues

- Possibly it won't work properly at a very close source-detector relative positioning.
- No other radiation (excl x-ray/gamma)
- Linear interpolation of mass attenuation / photoabsorption coefficients
- Point isotropic sources only
- All detectors are source-oriented cylinders
- Technically only 1D scene configuration
- Faked Compton-effect simulation
- No pair production yet
- No simultaneous detection events or temporal resolution
- No inner radioactivity (for LaBr3 for example)
- Background simulation is still kinda stupid

## ToDo list

- User-friendly app settings
- Python2.7 support
- Experiment options saves
- Console (no-gui) interface
- More scintillator materials / media / moderators
- Better interaction physics
- Energy resolution calculations (mb)
- Basic PMT simulation (mb)
- More geometries (mb)
- Working tags
- Optimization

## App structure

- xr3.py — main module
- config.ini — program preferences
- /templates/ - list of saved source/detector configurations (scenes) including default scene
- /media/ - scene media data (air, water, etc.)
- /materials/ - moderators, cases
- /scintillators/	 
— /isotopes/	 
- /docs/ - additional documentation

## Adding data

Basically each data file is a table of values. You can add/modify anything on your own risk.
.isotope file consist of a header with isotope name, atomic mass, half-life and tags; and energy(kev)/probability(%) values (i.e. x-ray spectrum)
.mat file consists of name and density(g/cm3) values and a table of energy(MeV)/mass attenuation k/mass photoabsorption k data. Moderator files use only the first two columns of data.
