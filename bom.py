from datetime import datetime
from ftplib import FTP
import xml.etree.ElementTree as ET
import json, utils

def getClosestForecast(lat, long):
	locations = json.load(open("bomLocations.json"))
	closestDistance = -1
	closestTown = ""
	for town in locations:
		dist = utils.coordDistance(lat, long, locations[town]["lat"], locations[town]["long"])
		if closestDistance == -1 or dist < closestDistance:
			closestDistance = dist
			closestTown = town
	output = locations[closestTown]
	output.update({"name": closestTown, "distance": closestDistance})
	return output

def getForecast(forecastID):
	locations = json.load(open("bomLocations.json"))
	if forecastID not in [l["forecast"] for l in locations.values()]:
		return "Invalid Forecast"
	
	ftp = FTP('ftp.bom.gov.au')
	ftp.login(user='anonymous')
	lines = []
	ftp.retrlines(f"RETR /anon/gen/fwo/{forecastID}.xml", lines.append)
	xmlData = '\n'.join(lines)
	return parseXML(xmlData)

def parseXML(xmlData):
	root = ET.fromstring(xmlData)
	output = []
	output.append(root.findtext(".//identifier"))
	output.append(root.find(".//area[@type='location']").attrib["description"] + " Forecast")
	output.append("Issued at " + datetime.strptime(root.findtext(".//issue-time-local"), "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M %p %Z on %A %d %B %Y"))
	output.append("")
	output.append("Warning Information")
	for warning in root.findall(".//area[@type='region']/forecast-period/text[@type='warning_summary_footer']"):
		output.append(warning.text)
	output.append("")
	output.append("")

	for day in root.findall("./forecast/area[@type='location']/forecast-period"):
		output.append("Forecast for " + datetime.strptime(day.attrib["start-time-local"], "%Y-%m-%dT%H:%M:%S%z").strftime("%A %d %B"))
		output.append(day.findtext("text[@type='forecast']"))
		if day.find("element[@type='air_temperature_minimum']") == None:
			#No temperature data
			output.append("Precis: " + day.findtext("text[@type='precis']"))
		else:
			output.append("Precis: " + day.findtext("text[@type='precis']") + "              Min " + day.findtext("element[@type='air_temperature_minimum']") + "    Max " + day.findtext("element[@type='air_temperature_maximum']"))
		if day.find("element[@type='precipitation_range']") == None:
			#No Precip range
			output.append("Chance of any rain: " + day.findtext("text[@type='probability_of_precipitation']"))
		else:
			output.append("Possible rainfall: " + day.findtext("element[@type='precipitation_range']") + "     Chance of any rain: " + day.findtext("text[@type='probability_of_precipitation']"))
		output.append("")

	output.append("The next routine forecast will be issued at " + datetime.strptime(root.findtext(".//next-routine-issue-time-local"), "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M %p %Z %A"))

	return '\n'.join(output)