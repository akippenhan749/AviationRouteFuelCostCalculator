# Adam Kippenhan ajk8sb 05/12/2022 fuelCostCalculator.py

from haversine import haversine
import json
import pandas as pd
from pymongo import MongoClient
import re
import requests
from sqlalchemy import create_engine

# function to get API response based on apiRequest, puts data in a file with name outputFilename
def getApiResponse(apiRequest, outputFilename, verbose=False):
    # make sure user entered an API request and an outputFilename
    if apiRequest == '':
        if verbose:
            print('Missing API request')
        return -1
    if outputFilename == '':
        if verbose:
            print('Missing output filename for API request data')
        return -1
    if not outputFilename.endswith('json'): # make sure user entered a filename ending with 'json'
        if verbose:
            print('Ouput file type must be json')
        return -1
    response = requests.get('https://api.aviationstack.com/v1/flights?access_key=ACCESS_KEY' + apiRequest).json() # make request to the aviationstack API
    json.dump(response, open(outputFilename, 'w')) # put request into file with name outputFilename

# function to get the estimated route fuel cost given an ICAO flight number, the fuel cost to use and a filepath from which to read flight data
def getRouteFuelCost(flightNum, apiDataFilepath, fuelCostDate='today', verbose=False):
    if fuelCostDate != 'today' and not re.match('\d{4}-\d{2}-\d{2}', fuelCostDate): # check correct date format (YYYY-MM-DD)
        if verbose:
            print('Invalid date format \'' + fuelCostDate + '\'. Valid format is: \'YYYY-MM-DD\'')
        return -1
    try:
        flightDataFile = json.load(open(apiDataFilepath)) # open the json file with the flight data
    except FileNotFoundError:
        if verbose:
            print('File \'' + apiDataFilepath + '\' does not exist')
        return -1
    flightDataDf = pd.DataFrame(flightDataFile['data']) # put json file data into Pandas dataframe
    depAirport, arrAirport = '', ''
    for i in range(flightDataDf.shape[0]): # loop through json data from API
        if flightNum == flightDataDf['flight'][i]['icao']: # find requested flight number in flight data
            depAirport = flightDataDf['departure'][i]['icao'] # get departure and arrival airport ICAO codes for the flight
            arrAirport = flightDataDf['arrival'][i]['icao']
            break # break out of the for loop when the desired flight is found
    if depAirport == '' or arrAirport == '': # exit function if the ICAO flight codes for the departure or arrival airport could not be found
        if verbose:
            print('Departure or arrival airport not found for flight ' + flightNum)
        return -1
    # get relevant airport data from MySQL database airportInfo airport-codes table
    airportCodes = pd.read_sql('SELECT * FROM airportInfo.`airport-codes` WHERE ident IN ' + str((depAirport, arrAirport)), create_engine(f'mysql+pymysql://adam:password@localhost', pool_recycle=3600).connect())
    depCoords = str(airportCodes[airportCodes['ident'] == depAirport].values.tolist()).replace('\'', '').replace(']', '').split(',')[-2:] # remove leftover characters and isolate coordinates
    arrCoords = str(airportCodes[airportCodes['ident'] == arrAirport].values.tolist()).replace('\'', '').replace(']', '').split(',')[-2:]
    try:
        # use haversine distance module haversine function which is used to calculate the distance between 2 points on Earth
        flightDistance = haversine((float(depCoords[0]), float(depCoords[1])), (float(arrCoords[0]), float(arrCoords[1])), unit='mi') # get output in miles
    except ValueError: # above line might raise ValueError if a problem occured when finding depCoords or arrCoords
        if verbose:
            print('Coordinates for departure or arrival airport not found for flight ' + flightNum)
        return -1
    aircraftMPGPerSeat, numSeats = 0, 0
    match flightDistance: # use different efficiency numbers for each flight distance class
        case flightDistance if flightDistance >= 0 and flightDistance < 1100: # regional flight range
            aircraftMPGPerSeat = 59.7 # values used for Bombardier CRJ900
            numSeats = 88
        case flightDistance if flightDistance >= 1100 and flightDistance < 2000: # short-haul flight range
            aircraftMPGPerSeat = 85 # values used for Boeing 737-800
            numSeats = 162
        case flightDistance if flightDistance >= 2000 and flightDistance < 5000: # medium-haul flight range
            aircraftMPGPerSeat = 88 # values used for Boeing 787-8
            numSeats = 238
        case flightDistance if flightDistance >= 5000: # long-haul flight range
            aircraftMPGPerSeat = 98 # values used for Airbus A350-900
            numSeats = 315
    if fuelCostDate == 'today':
        fuelCostDate = '2022-05-02' # most recent date available for jet fuel price
    # get relevant fuel cost for the specified date from the MongoDB database jetFuelPrices jetFuelPrices table
    jetFuelPricesDf = pd.DataFrame(list(MongoClient('localhost', 27017)['jetFuelPrices']['jetFuelPrices'].find({'Date': fuelCostDate})))
    if jetFuelPricesDf.empty: # make sure a fuel price exists for the specified date
        if verbose:
            print('No fuel price data for date ' + fuelCostDate + '. Select a different date')
        return -1
    jetFuelPrice = jetFuelPricesDf['Jet_fuel_spot_price'].values[0]
    return round((((flightDistance / aircraftMPGPerSeat) * jetFuelPrice) * numSeats), 2) # calculate total route fuel cost and round to 2 decimal places