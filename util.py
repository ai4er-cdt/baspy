#!/usr/bin/python
# Filename: util.py

import numpy as np
import iris
import iris.coord_categorisation

cmip5_dir = '/badc/cmip5/data/cmip5/output1/'


def months2seasons(cube, time_coord=None):
	"""
	Create seasons from monthly data
	
	"""
	
	if (time_coord == None): time_coord = 'time'
	
	### Create seasonal means (unique and specified 3-month seasons)
	seasons=['mam', 'jja', 'son', 'djf']
	iris.coord_categorisation.add_season(cube, time_coord, name='clim_season', seasons=seasons)
	iris.coord_categorisation.add_season_year(cube, time_coord, name='season_year', seasons=seasons)
	seasons = cube.aggregated_by(['clim_season', 'season_year'], iris.analysis.MEAN)
	
	### Remove all of the resultant times which do not cover a three month period.
	### Check bounds and units (e.g., seasons[4].coord('time') ) 
	### before you specify your lambda function
	#with iris.FUTURE.context(cell_datetime_objects=False):
		#spans_three_months = lambda t: (t.bound[1] - t.bound[0]) > 3 * 28.
		#three_months_bound = iris.Constraint(time_coord=spans_three_months)
		#seasons = seasons.extract(three_months_bound)

	return seasons



def months2annual(cube, time_coord=None):
	"""
	Create annual data from monthly data
	
	"""
	
	if (time_coord == None): time_coord = 'time'
	
	### Create annual means
	iris.coord_categorisation.add_year(cube, time_coord, name='year')
	annual = cube.aggregated_by(['year'], iris.analysis.MEAN)

	#### Remove all of the resultant times which do not cover a 12 month period.
	#### Check bounds and units (e.g., annual[4].coord('time') ) 
	#### before you specify your lambda function
	#with iris.FUTURE.context(cell_datetime_objects=False):
		#spans_twelve_months = lambda t: (t.bound[1] - t.bound[0]) > 12 * 29.
		#twelve_months_bound = iris.Constraint(time=spans_twelve_months)
		#annual = annual.extract(twelve_months_bound)

	return annual




def unify_grid_coords(cubelist, cube_template):
	"""
	If cube[i].dim_coords[n] != cube[j].dim_coords[n] but you know that 
	they are on the same grid then place all cubes on an identical 
	grid (matching cube[0])
	
	Usage:
		unify_grid_coords(cubelist, cube_template, dimensions)
		
	Example:
		unify_grid_coords(my_cubes, my_cubes[0], [1,2])
		
	"""

	if (cube_template.__class__ != iris.cube.Cube):
		raise ValueError('cube_template is not a cube')


	if (cubelist.__class__ == iris.cube.CubeList):
		n_cubes = len(cubelist)

	if (cubelist.__class__ == iris.cube.Cube):
		n_cubes = 1
	
	for j in ['latitude','longitude']:
		edits = 0
		A =  cube_template.coords(j)[0]
		for i in range(0,n_cubes):
			
			if (cubelist.__class__ == iris.cube.CubeList): B =  cubelist[i].coords(j)[0]
			if (cubelist.__class__ == iris.cube.Cube):     B =  cubelist.coords(j)[0]			
			
			if ((A != B) & (A.points.shape == B.points.shape)):
				print('>>> Grid coordinates are different between cubes <<<')
				if (np.max(np.abs(A.points - B.points)) < 0.001):
					edits = edits + 1
					B.points = A.points
					B.bounds = A.bounds
		
		if (edits > 0): 
			print ">>> unify_grid_coords: "+str(edits)+" edits to coords["+str(j)+"] <<<"
		
	return cubelist



def rm_time_overlaps(cubelist):
	"""
	Remove time overlaps from a cubelist
	keeping the duplicated period from the cube that
	comes before the two within the cubelist
	"""	
	if (cubelist.__class__ != iris.cube.CubeList):
		return cubelist
	
	if (len(cubelist) == 1): return cubelist
	
	### add check that all cubes are of the same var, exp etc !!!!
	#
	# TO DO !
	#
	
	### Unify time coordinates to identify overlaps
	iris.util.unify_time_units(cubelist)
	
	### Sort cubelist by start time !!!!
	#
	# TO DO !
	#

	i = 1
	while i < len(cubelist):

		max1 = np.max(cubelist[i-1].coord('time').points)
		min2 = np.min(cubelist[i].coord('time').points)
		
		if (min2 <= max1):
			print('>>> WARNING: Removing temporal overlaps'
					' from cubelist <<<')
			con = iris.Constraint(time=lambda t: t > max1)
			cubelist[i] = cubelist[i].extract(con)

		if (cubelist[i].__class__ != iris.cube.Cube):
			cubelist.pop(i)
		else:
			i = i + 1
	
	return cubelist


def eg_cube():
	""" 
	Load an example cube
	"""
	cube = iris.load_cube(cmip5_dir + 
			'MOHC/HadGEM2-A/amip/mon/atmos/Amon/r1i1p1/latest/'
			'tas/tas_Amon_HadGEM2-A_amip_r1i1p1_197809-200811.nc')
	return cube


def eg_cubelist():
	"""
	Load an example cubelist
	"""
	cubelist = iris.load(
			[cmip5_dir+'MOHC/HadGEM2-A/amip/mon/atmos/Amon/r1i1p1/latest/'
			'psl/psl_Amon_HadGEM2-A_amip_r1i1p1_197809-200811.nc', 
			cmip5_dir +'MOHC/HadGEM2-A/amip/mon/atmos/Amon/r1i1p1/latest/'
			'tas/tas_Amon_HadGEM2-A_amip_r1i1p1_197809-200811.nc']
			)
	return cubelist


# End of util.py
