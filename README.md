# Python2-HW3-Covid-Dash
#Overview:
# Fpr ths final project, I made a web dash that visualize the Number of Novel Corona Virus 2019 cases in USA 

# dataset
#My dataset is from [kaggle](https://www.kaggle.com/sudalairajkumar/covid19-in-usa?select=us_counties_covid19_daily.csv) ,
#The number of new cases are increasing day by day around the world. This dataset has information from 50 US states and the District of Columbia at daily level.

### Description
#In file [us_mapbox/GeoJSONfactory.py](mapbox-counties-master/GeoJSONfactory.py) fit data to mapbox style json.becaue in mapbox source use HTTPS link ,
#I store treated data with GitHub , so that I can use https link access like (https://raw.githubusercontent.com/lometheus/us_mapbox/master/12/0.geojson) {mounth}/{case level}.geojson
#Dash app is the [app.py]file, by opening the app.py we can see the changes in cases in each county every month since 2020 ,and we can see the total number of deaths (single mounth) per county with Histogram. 
#attention, we will need to drag the state that you would lik to check the histgram to the right of the dash in order to visualize

#Instruction (IMPORTANT)
#I upload the data file and app.py separately, so in order to successfullt run python file, we need to put the app.py into the covid_dash folder first, please make sure to install the following package:
geopandas
dash==1.12.0 
plotly==4.7.1 
cufflinks==0.17.3 
gunicorn==20.0.4 
numpy==1.18.4 
pandas==1.0.3 

