# Adam Kippenhan ajk8sb 05/12/2022 fuelCostsActiveFlights510.py

import fuelCostCalculator
import json
import pandas as pd
import plotly.express as px

# get active flights from aviationstack API and put the data into 'activeFlights510.json' in the data folder
fuelCostCalculator.getApiResponse('&amp;flight_status=active', 'data/activeFlights510.json')

# load the activeFlights510.json file and put it into a Pandas dataframe
flightDataFile = json.load(open('data/activeFlights510.json'))
flightDataDf = pd.DataFrame(flightDataFile['data'])

flightNums, fuelCosts = [], []
for i in range(flightDataDf.shape[0]): # loop through json data from API
    # calculate the fuel cost for this route using fuelCostCalculator
    fuelCost = fuelCostCalculator.getRouteFuelCost(flightDataDf['flight'][i]['icao'], 'data/activeFlights510.json')
    if fuelCost != -1: # only use valid calculated value for fuelCost
        flightNums.append(flightDataDf['flight'][i]['icao']) # append values to flightNums and fuelCosts lists
        fuelCosts.append(fuelCost)

flightData510 = pd.DataFrame({'FlightNum':flightNums, 'FuelCost':fuelCosts}) # make a Pandas dataframe from the lists

# plot the data in a histogram using Plotly Express
fig = px.histogram(data_frame=flightData510,
                   x='FlightNum',
                   y='FuelCost',
                   labels={'FlightNum':'ICAO Flight Number'}, # add x-axis title
                   title='Estimated Fuel Costs for 100 Active Flights at 6:55 PM EDT 2022-05-10') # add plot title

fig.update_traces(marker_color='red', # change marker color to red
                  hovertemplate='<br>'.join(['<b>ICAO Flight Number:</b> %{x}', # customize info for when hovering over data points
                                             '<b>Fuel Cost:</b> $%{y}']))

fig.update_layout(yaxis_title='Estimated Total Route Fuel Cost (USD)') # add y-axis title
fig.show() # display the plot
