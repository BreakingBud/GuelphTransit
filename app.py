import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests
from google.transit import gtfs_realtime_pb2

# Title of the Streamlit app
st.title("Guelph Transit Map")

# Input field for searching locations in Guelph
search_location = st.text_input("Search for a location in Guelph:")

# Geocoding function
def geocode_address(address):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude) if location else (None, None)

# Fetch real-time vehicle positions from the Guelph Transit API
def fetch_vehicle_positions():
    url = "https://glphprdtmgtfs.glphtrpcloud.com/tmgtfsrealtimewebservice/vehicle/vehiclepositions.pb"
    response = requests.get(url)
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    vehicles = []
    for entity in feed.entity:
        vehicle = entity.vehicle
        vehicles.append({
            'id': vehicle.vehicle.id,
            'latitude': vehicle.position.latitude,
            'longitude': vehicle.position.longitude,
            'timestamp': vehicle.timestamp
        })
    return vehicles

# Default map center
map_center = [43.5448, -80.2482]

# Create the map
m = folium.Map(location=map_center, zoom_start=13)

# If a search location is provided, geocode it and add a marker
if search_location:
    search_coords = geocode_address(search_location + ", Guelph")
    if search_coords:
        folium.Marker(search_coords, popup="Search Location", icon=folium.Icon(color='red')).add_to(m)
        m.location = search_coords
        m.zoom_start = 15
    else:
        st.write("Could not find the location. Please try again.")

# Fetch and add vehicle positions to the map
vehicle_data = fetch_vehicle_positions()
for vehicle in vehicle_data:
    folium.Marker(
        location=[vehicle['latitude'], vehicle['longitude']],
        popup=f"Bus ID: {vehicle['id']}",
        icon=folium.Icon(color='blue', icon='bus', prefix='fa')
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=700, height=500)
