# from django.contrib.gis.geoip2 import GeoIP2
# from django.contrib.gis.geoip import GeoIP
import requests
from urllib.parse import urlencode, urlparse, parse_qsl
import math 

GOOGLE_API_KEY = 'google_api_key_goes_here'

# helper functions and classes

# get the current location based on the ip address
def get_ip_address(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip


# get geographic information
# def get_geo(ip):
# 	g = GeoIP2()
# 	country = g.country(ip)
# 	city = g.city(ip)
# 	lat, lon = g.lat_lon(ip)
# 	return country, city, lat, lon

# centers the map
def get_center_coordinates(latA, longA, latB=None, longB=None):
	cord = (latA, longA)

	# if we are given an actual destination, overwrite the coordinates
	if latB:
		cord = [(latA+latB)/2, (longA+longB)/2]
	return cord

# adjusts the zoom based on the distance
def get_zoom(distance):
	if distance <= 100:
		return 8
	elif distance > 100 and distance <= 5000:
		return 4
	else:
		return 2

# the google maps client
class GoogleMapsClient(object):
	lat = None
	lng = None
	data_type = 'json'
	location_query = None
	api_key = None

	def __init__(self, api_key=None, address_or_postal_code=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.location_query = address_or_postal_code
		self.api_key = api_key
		if api_key == None:
			raise Exception("API key required")

		if self.location_query != None:
			self.extract_lat_lng()

	# given a properly formatted location, get its latitude and longitude
	def extract_lat_lng(self, location=None):
		loc_query = self.location_query

		if location != None:
			loc_query = location

		endpoint = f'https://maps.googleapis.com/maps/api/geocode/{self.data_type}'
		params = {'address': loc_query, 'key': self.api_key}

		url_params = urlencode(params)
		url = f"{endpoint}?{url_params}"
		# print(url)

		r = requests.get(url)
		if r.status_code not in range(200, 299):
			return {}

		lat_lng = {}
		try:
			lat_lng = r.json()['results'][0]['geometry']['location']
		except:
			pass

		lat, lng = lat_lng.get('lat'), lat_lng.get('lng')
		self.lat = lat
		self.lng = lng

		return lat, lng

	# perform the search based on a keywork ex: "Mexican Food" or "Bagels"
 	# radius is in meters
	def search(self, keyword="", radius=1000, location=None):
		lat, lng = self.lat, self.lng

		if location != None:
			lat, lng = self.extract_lat_lng(location=location)

		endpoint = f"https://maps.googleapis.com/maps/api/place/nearbysearch/{self.data_type}"
		params = {
			'key': self.api_key,
			'location': f'{lat},{lng}',
			'radius': radius,
			'keyword': keyword
		}

		params_encoded = urlencode(params)
		places_url = f"{endpoint}?{params_encoded}"

		r = requests.get(places_url)

		if r.status_code not in range(200, 299):
			return {}

		return r.json()

	# get the location's details (provided in fields) based on a place_id
	def detail(self, place_id="ChIJhzHBsAe6j4ARvq9oi8u-bqQ", fields=["name", "rating", "formatted_phone_number", "formatted_address"]):
		detail_base_endpoint = f"https://maps.googleapis.com/maps/api/place/details/{self.data_type}"
		detail_params = {
			"place_id": f"{place_id}",
			"fields": ",".join(fields),
			"key": self.api_key

		}
		detail_params_encoded = urlencode(detail_params)
		detail_url = f"{detail_base_endpoint}?{detail_params_encoded}"

		r = requests.get(detail_url)
		if r.status_code not in range(200, 299):
			return {}

		return r.json()


# given two points (lat, long), calculate the distance between them
def calculate_distance(start, end):

	# in km
	radius_of_earth = 6373.0

	# convert to radians
	lat_1 = math.radians(start[0])
	lon_1 = math.radians(start[1])
	lat_2 = math.radians(end[0])
	lon_2 = math.radians(end[1])

	d_lon = lon_2 - lon_1
	d_lat = lat_2 - lat_1

	a = math.sin(d_lat / 2)**2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(d_lon / 2)**2

	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	distance = radius_of_earth * c

	return distance
