# -*- coding: utf-8 -*-
# !/usr/bin/python3

import json
import logging
import math
import os
import traceback
from FlightRadar24 import FlightRadar24API
from Misc import get911, sendEmail


def haversine_distance(coord1, coord2):
    """
    Calculate the haversine distance between two geographical coordinates.

    Args:
        coord1 (tuple): Latitude and longitude of the first point.
        coord2 (tuple): Latitude and longitude of the second point.

    Returns:
        float: The distance in kilometers between the two coordinates.
    """
    # Coordinates are in (latitude, longitude) format
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Radius of the Earth in kilometers
    earth_radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c

    return round(distance, 2)


def getFlights():
    """
    Retrieve flight information from FlightRadar24 API within specified bounds.

    Returns:
        list: List of flight objects.
    """
    fr_api = FlightRadar24API()
    zones = fr_api.get_zones()
    bounds = fr_api.get_bounds(zone=zones["europe"]["subzones"]["spain"])
    flights = fr_api.get_flights(bounds=bounds)
    return flights


def main():
    """
    Main function to check and print flights within a certain distance from a center point.
    """
    flights = getFlights()
    for flight in flights:
        if haversine_distance((flight.latitude, flight.longitude), CENTER_POINT) < MAX_DISTANCE:
            print(flight.callsign)
    return


if __name__ == '__main__':
    # Set Logging
    LOG_FILE = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{os.path.abspath(__file__).replace(".py", ".log")}")}"
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    # Load Config File
    configFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(configFile, "r") as inFile:
        config = json.loads(inFile.read())
    MAX_DISTANCE = config["MAX_DISTANCE"]
    CENTER_POINT = (config["CENTER_POINT"]["LAT"], config["CENTER_POINT"]["LONG"])

    # Load saved_info File
    savedInfoFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_info.json")
    if not os.path.exists(savedInfoFile):
        with open(savedInfoFile, "w") as outFile:
            json.dump([], outFile, indent=2)
    with open(savedInfoFile, "r") as inFile:
        SAVED_FLIGHTS = json.loads(inFile.read())

    # Main
    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        sendEmail(os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
