from math import radians, sin, cos, acos

def coordDistance(lat1, lon1, lat2, lon2):
	#Distance between two coords in km
	mlat = radians(float(lat1))
	mlon = radians(float(lon1))
	plat = radians(float(lat2))
	plon = radians(float(lon2))
	
	dist = 6371.01 * acos(sin(mlat)*sin(plat) + cos(mlat)*cos(plat)*cos(mlon - plon))
	return dist