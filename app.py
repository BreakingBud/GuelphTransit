import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests
from google.transit import gtfs_realtime_pb2

# Title of the Streamlit app
st.title("Guelph Transit Map")

# Initialize session state for map center and zoom level
if 'map_center' not in st.session_state:
    st.session_state['map_center'] = [43.5448, -80.2482]
if 'zoom_level' not in st.session_state:
    st.session_state['zoom_level'] = 13

# Print debug information
st.write("Map Center:", st.session_state['map_center'])
st.write("Zoom Level:", st.session_state['zoom_level'])

# Input field for searching locations in Guelph
search_location = st.text_input("Search for a location in Guelph:")

# Geocoding function
def geocode_address(address):
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        else:
            st.error("Geocoding failed: location not found.")
            return (None, None)
    except Exception as e:
        st.error(f"Geocoding failed: {e}")
        return (None, None)

# Fetch real-time vehicle positions from the Guelph Transit API
def fetch_vehicle_positions():
    try:
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
    except Exception as e:
        st.error(f"Failed to fetch vehicle positions: {e}")
        return []

# Ensure valid map center
if isinstance(st.session_state['map_center'], (list, tuple)) and len(st.session_state['map_center']) == 2:
    try:
        m = folium.Map(location=st.session_state['map_center'], zoom_start=st.session_state['zoom_level'])
    except Exception as e:
        st.error(f"Failed to create map: {e}")
else:
    st.error("Invalid map center or zoom level.")

# If a search location is provided, geocode it and add a marker
if search_location:
    search_coords = geocode_address(search_location + ", Guelph")
    if search_coords[0] is not None:
        folium.Marker(search_coords, popup="Search Location", icon=folium.Icon(color='red')).add_to(m)
        st.session_state['map_center'] = search_coords
        st.session_state['zoom_level'] = 15
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

# Display the map in Streamlit and update session state
map_data = st_folium(m, width=700, height=500)
if map_data:
    st.session_state['map_center'] = map_data['center']
    st.session_state['zoom_level'] = map_data['zoom']
