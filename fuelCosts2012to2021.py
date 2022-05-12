# Adam Kippenhan ajk8sb 05/12/2022 fuelCosts2012to2021.py

import fuelCostCalculator
import json
import pandas as pd
import plotly.express as px

# list of the dates of the second Friday of July between 2012 and 2021
dates = ['2012-07-13', '2013-07-12', '2014-07-11', '2015-07-10', '2016-07-08', '2017-07-07', '2018-07-13', '2019-07-12', '2020-07-10', '2021-07-09']
# list of output filenames for the json output of the API requests
filepaths = ['data/flights712.json', 'data/flights713.json', 'data/flights714.json', 'data/flights715.json', 'data/flights716.json', 'data/flights717.json', 'data/flights718.json', 'data/flights719.json', 'data/flights720.json', 'data/flights721.json']

for i in range(len(dates)):
    fuelCostCalculator.getApiResponse('&amp;flight_date=' + dates[i], filepaths[i]) # get an API response for every date and filepath in the dates and filepaths lists

flightDates, flightNums, fuelCosts = [], [], []
for i in range(len(dates)):
    flightDataFile = json.load(open(filepaths[i])) # load the json data from the API located in filepaths[i]
    flightDataDf = pd.DataFrame(flightDataFile['data']) # load the data into a Pandas dataframe
    for j in range(flightDataDf.shape[0]): # loop through json data from API
        # calculate the fuel cost for this route using fuelCostCalculator
        fuelCost = fuelCostCalculator.getRouteFuelCost(flightDataDf['flight'][j]['icao'], filepaths[i], dates[i])
        if fuelCost != -1: # only use valid calculated value for fuelCost
            flightDates.append(dates[i]) # append values to flightDates, flightNums and fuelCosts lists
            flightNums.append(flightDataDf['flight'][j]['icao'])
            fuelCosts.append(fuelCost)

flightData2012to2021 = pd.DataFrame({'Date':flightDates, 'FlightNum':flightNums, 'FuelCost':fuelCosts}) # make a Pandas dataframe from the lists

# plot the data in a scatterplot using Plotly Express
fig1 = px.scatter(data_frame=flightData2012to2021,
                  x='Date', 
                  y='FuelCost',
                  custom_data=['FlightNum', 'Date'], # custom_data for hovertemplate
                  labels={'Date':'Year of Second Friday of July', 'FuelCost':'Estimated Total Route Fuel Cost (USD)'}, # add x-axis and y-axis titles
                  title='Estimated Fuel Costs for 100 Flights on each Second Friday of July Between 2012 and 2021') # add plot title

fig1.update_traces(marker_color='red', # change marker color to red
                   hovertemplate='<br>'.join(['<b>ICAO Flight Number:</b> %{customdata[0]}', # customize info for when hovering over data points
                                              '<b>Date:</b> %{customdata[1]|%Y-%m-%d}',
                                              '<b>Fuel Cost:</b> $%{y}']))
fig1.show() # display the plot

flightData2012to2021Sub2000 = flightData2012to2021[flightData2012to2021['FuelCost'] < 2000] # make a new Pandas dataframe with fuel costs from flightData2012to2021 under $2000

# make the same plot for the flightData2012to2021Sub2000 dataframe
fig2 = px.scatter(data_frame=flightData2012to2021Sub2000,
                  x='Date', 
                  y='FuelCost',
                  custom_data=['FlightNum', 'Date'],
                  labels={'Date':'Year of Second Friday of July', 'FuelCost':'Estimated Total Route Fuel Cost (USD)'},
                  title='Estimated Fuel Costs for 100 Flights on each Second Friday of July Between 2012 and 2021')

fig2.update_traces(marker_color='red',
                   hovertemplate='<br>'.join(['<b>ICAO Flight Number:</b> %{customdata[0]}',
                                              '<b>Date:</b> %{customdata[1]|%Y-%m-%d}',
                                              '<b>Fuel Cost:</b> $%{y}']))
fig2.show()