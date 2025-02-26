import math
import pandas as pd
import geopandas as gpd
#from geopy.geocoders import Nominatim            # What you'd normally run
from learntools.geospatial.tools import Nominatim # Just for this exercise

import folium 
from folium import Marker
from folium.plugins import MarkerCluster

from learntools.core import binder
binder.bind(globals())
from learntools.geospatial.ex4 import *

def embed_map(m, file_name):
    from IPython.display import IFrame
    m.save(file_name)
    return IFrame(file_name, width='100%', height='500px')

# Load and preview Starbucks locations in California
starbucks = pd.read_csv("../input/geospatial-learn-course-data/starbucks_locations.csv")
starbucks.head()


Store Number	Store Name	Address	City	Longitude	Latitude
0	10429-100710	Palmdale & Hwy 395	14136 US Hwy 395 Adelanto CA	Adelanto	-117.40	34.51
1	635-352	Kanan & Thousand Oaks	5827 Kanan Road Agoura CA	Agoura	-118.76	34.16
2	74510-27669	Vons-Agoura Hills #2001	5671 Kanan Rd. Agoura Hills CA	Agoura Hills	-118.76	34.15
3	29839-255026	Target Anaheim T-0677	8148 E SANTA ANA CANYON ROAD AHAHEIM CA	AHAHEIM	-117.75	33.87
4	23463-230284	Safeway - Alameda 3281	2600 5th Street Alameda CA	Alameda	-122.28	37.79

# How many rows in each column have missing values?
print(starbucks.isnull().sum())

# View rows with missing locations
rows_with_missing = starbucks[starbucks["City"]=="Berkeley"]
rows_with_missing

Store Number    0
Store Name      0
Address         0
City            0
Longitude       5
Latitude        5
dtype: int64

Store Number	Store Name	Address	City	Longitude	Latitude
153	5406-945	2224 Shattuck - Berkeley	2224 Shattuck Avenue Berkeley CA	Berkeley	NaN	NaN
154	570-512	Solano Ave	1799 Solano Avenue Berkeley CA	Berkeley	NaN	NaN
155	17877-164526	Safeway - Berkeley #691	1444 Shattuck Place Berkeley CA	Berkeley	NaN	NaN
156	19864-202264	Telegraph & Ashby	3001 Telegraph Avenue Berkeley CA	Berkeley	NaN	NaN
157	9217-9253	2128 Oxford St.	2128 Oxford Street Berkeley CA	Berkeley	NaN	NaN

# Create the geocoder
geolocator = Nominatim(user_agent="kaggle_learn")

# Your code here
def my_geocoder(row):
    point = geolocator.geocode(row).point
    return pd.Series({'Latitude': point.latitude, 'Longitude': point.longitude})
berkeley_locations = rows_with_missing.apply(lambda x: my_geocoder(x['Address']), axis=1)
starbucks.update(berkeley_locations)

# Check your answer
q_1.check()

# Create a base map
m_2 = folium.Map(location=[37.88,-122.26], zoom_start=13)

# Your code here: Add a marker for each Berkeley location
for idx, row in starbucks[starbucks["City"]=='Berkeley'].iterrows():
    Marker([row['Latitude'], row['Longitude']]).add_to(m_2)

# Uncomment to see a hint
q_2.a.hint()

# Show the map
embed_map(m_2, 'q_2.html')

CA_counties = gpd.read_file("../input/geospatial-learn-course-data/CA_county_boundaries/CA_county_boundaries/CA_county_boundaries.shp")
CA_counties.crs = {'init': 'epsg:4326'}
CA_counties.head()


GEOID	name	area_sqkm	geometry
0	6091	Sierra County	2491.995494	POLYGON ((-120.65560 39.69357, -120.65554 39.6...
1	6067	Sacramento County	2575.258262	POLYGON ((-121.18858 38.71431, -121.18732 38.7...
2	6083	Santa Barbara County	9813.817958	MULTIPOLYGON (((-120.58191 34.09856, -120.5822...
3	6009	Calaveras County	2685.626726	POLYGON ((-120.63095 38.34111, -120.63058 38.3...
4	6111	Ventura County	5719.321379	MULTIPOLYGON (((-119.63631 33.27304, -119.6360...

                                                    CA_pop = pd.read_csv("../input/geospatial-learn-course-data/CA_county_population.csv", index_col="GEOID")
CA_high_earners = pd.read_csv("../input/geospatial-learn-course-data/CA_county_high_earners.csv", index_col="GEOID")
CA_median_age = pd.read_csv("../input/geospatial-learn-course-data/CA_county_median_age.csv", index_col="GEOID")

             # Your code here
cols_to_add = CA_pop.join([CA_high_earners, CA_median_age]).reset_index()
CA_stats = CA_counties.merge(cols_to_add, on ="GEOID")

# Check your answer
q_3.check()

CA_stats["density"] = CA_stats["population"] / CA_stats["area_sqkm"]

# Your code here
sel_counties = CA_stats[((CA_stats.high_earners > 100000) &
                         (CA_stats.median_age < 38.5) &
                         (CA_stats.density > 285) &
                         ((CA_stats.median_age < 35.5) |
                         (CA_stats.density > 1400) |
                         (CA_stats.high_earners > 500000)))]

print(sel_counties)

# Check your answer
q_4.check()

             GEOID                  name     area_sqkm  \
5    6037    Los Angeles County  12305.376879   
8    6073      San Diego County  11721.342229   
10   6075  San Francisco County    600.588247   

                                             geometry  population  \
5   MULTIPOLYGON (((-118.66761 33.47749, -118.6682...    10105518   
8   POLYGON ((-117.43744 33.17953, -117.44955 33.1...     3343364   
10  MULTIPOLYGON (((-122.60025 37.80249, -122.6123...      883305   

    high_earners  median_age      density  
5         501413        36.0   821.227834  
8         194676        35.4   285.237299  
10        114989        38.3  1470.733077  

starbucks_gdf = gpd.GeoDataFrame(starbucks, geometry=gpd.points_from_xy(starbucks.Longitude, starbucks.Latitude))
starbucks_gdf.crs = {'init': 'epsg:4326'}

# Fill in your answer
locations_of_interest = gpd.sjoin(starbucks_gdf, sel_counties)
num_stores = len(locations_of_interest)

# Check your answer
q_5.check()

          # Create a base map
m_6 = folium.Map(location=[37,-120], zoom_start=6)

# Your code here: show selected store locations
mc = MarkerCluster()

locations_of_interest = gpd.sjoin(starbucks_gdf, sel_counties)
for idx, row in locations_of_interest.iterrows():
    if not math.isnan(row['Longitude']) and not math.isnan(row['Latitude']):
        mc.add_child(folium.Marker([row['Latitude'], row['Longitude']]))
        
m_6.add_child(mc)
# Uncomment to see a hint
q_6.hint()

# Show the map
embed_map(m_6, 'q_6.html')
