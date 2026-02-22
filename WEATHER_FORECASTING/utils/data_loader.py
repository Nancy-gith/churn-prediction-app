"""
Enhanced Data Loader with Indian Cities and Real-time Weather
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from meteostat import Point, Daily
import streamlit as st
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WeatherDataLoader:
    """Handles loading historical and real-time weather data."""
    
    # Comprehensive list of 100+ Indian cities
    INDIAN_CITIES = {
        # Metro Cities
        'mumbai': {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'state': 'Maharashtra'},
        'delhi': {'name': 'Delhi', 'lat': 28.7041, 'lon': 77.1025, 'state': 'Delhi'},
        'bangalore': {'name': 'Bangalore', 'lat': 12.9716, 'lon': 77.5946, 'state': 'Karnataka'},
        'hyderabad': {'name': 'Hyderabad', 'lat': 17.3850, 'lon': 78.4867, 'state': 'Telangana'},
        'chennai': {'name': 'Chennai', 'lat': 13.0827, 'lon': 80.2707, 'state': 'Tamil Nadu'},
        'kolkata': {'name': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639, 'state': 'West Bengal'},
        
        # Tier 1 Cities
        'pune': {'name': 'Pune', 'lat': 18.5204, 'lon': 73.8567, 'state': 'Maharashtra'},
        'ahmedabad': {'name': 'Ahmedabad', 'lat': 23.0225, 'lon': 72.5714, 'state': 'Gujarat'},
        'surat': {'name': 'Surat', 'lat': 21.1702, 'lon': 72.8311, 'state': 'Gujarat'},
        'jaipur': {'name': 'Jaipur', 'lat': 26.9124, 'lon': 75.7873, 'state': 'Rajasthan'},
        'lucknow': {'name': 'Lucknow', 'lat': 26.8467, 'lon': 80.9462, 'state': 'Uttar Pradesh'},
        'kanpur': {'name': 'Kanpur', 'lat': 26.4499, 'lon': 80.3319, 'state': 'Uttar Pradesh'},
        'nagpur': {'name': 'Nagpur', 'lat': 21.1458, 'lon': 79.0882, 'state': 'Maharashtra'},
        'indore': {'name': 'Indore', 'lat': 22.7196, 'lon': 75.8577, 'state': 'Madhya Pradesh'},
        'thane': {'name': 'Thane', 'lat': 19.2183, 'lon': 72.9781, 'state': 'Maharashtra'},
        'bhopal': {'name': 'Bhopal', 'lat': 23.2599, 'lon': 77.4126, 'state': 'Madhya Pradesh'},
        'visakhapatnam': {'name': 'Visakhapatnam', 'lat': 17.6869, 'lon': 83.2185, 'state': 'Andhra Pradesh'},
        'patna': {'name': 'Patna', 'lat': 25.5941, 'lon': 85.1376, 'state': 'Bihar'},
        'vadodara': {'name': 'Vadodara', 'lat': 22.3072, 'lon': 73.1812, 'state': 'Gujarat'},
        'ghaziabad': {'name': 'Ghaziabad', 'lat': 28.6692, 'lon': 77.4538, 'state': 'Uttar Pradesh'},
        'ludhiana': {'name': 'Ludhiana', 'lat': 30.9010, 'lon': 75.8573, 'state': 'Punjab'},
        'agra': {'name': 'Agra', 'lat': 27.1767, 'lon': 78.0081, 'state': 'Uttar Pradesh'},
        'nashik': {'name': 'Nashik', 'lat': 19.9975, 'lon': 73.7898, 'state': 'Maharashtra'},
        'faridabad': {'name': 'Faridabad', 'lat': 28.4089, 'lon': 77.3178, 'state': 'Haryana'},
        'meerut': {'name': 'Meerut', 'lat': 28.9845, 'lon': 77.7064, 'state': 'Uttar Pradesh'},
        'rajkot': {'name': 'Rajkot', 'lat': 22.3039, 'lon': 70.8022, 'state': 'Gujarat'},
        'varanasi': {'name': 'Varanasi', 'lat': 25.3176, 'lon': 82.9739, 'state': 'Uttar Pradesh'},
        'amritsar': {'name': 'Amritsar', 'lat': 31.6340, 'lon': 74.8723, 'state': 'Punjab'},
        'allahabad': {'name': 'Allahabad', 'lat': 25.4358, 'lon': 81.8463, 'state': 'Uttar Pradesh'},
        'ranchi': {'name': 'Ranchi', 'lat': 23.3441, 'lon': 85.3096, 'state': 'Jharkhand'},
        'howrah': {'name': 'Howrah', 'lat': 22.5958, 'lon': 88.2636, 'state': 'West Bengal'},
        'coimbatore': {'name': 'Coimbatore', 'lat': 11.0168, 'lon': 76.9558, 'state': 'Tamil Nadu'},
        'jabalpur': {'name': 'Jabalpur', 'lat': 23.1815, 'lon': 79.9864, 'state': 'Madhya Pradesh'},
        'gwalior': {'name': 'Gwalior', 'lat': 26.2183, 'lon': 78.1828, 'state': 'Madhya Pradesh'},
        'vijayawada': {'name': 'Vijayawada', 'lat': 16.5062, 'lon': 80.6480, 'state': 'Andhra Pradesh'},
        'jodhpur': {'name': 'Jodhpur', 'lat': 26.2389, 'lon': 73.0243, 'state': 'Rajasthan'},
        'madurai': {'name': 'Madurai', 'lat': 9.9252, 'lon': 78.1198, 'state': 'Tamil Nadu'},
        'raipur': {'name': 'Raipur', 'lat': 21.2514, 'lon': 81.6296, 'state': 'Chhattisgarh'},
        'kota': {'name': 'Kota', 'lat': 25.2138, 'lon': 75.8648, 'state': 'Rajasthan'},
        
        # Union Territories & Capitals
        'chandigarh': {'name': 'Chandigarh', 'lat': 30.7333, 'lon': 76.7794, 'state': 'Chandigarh'},
        'guwahati': {'name': 'Guwahati', 'lat': 26.1445, 'lon': 91.7362, 'state': 'Assam'},
        'thiruvananthapuram': {'name': 'Thiruvananthapuram', 'lat': 8.5241, 'lon': 76.9366, 'state': 'Kerala'},
        'bhubaneswar': {'name': 'Bhubaneswar', 'lat': 20.2961, 'lon': 85.8245, 'state': 'Odisha'},
        'puducherry': {'name': 'Puducherry', 'lat': 11.9416, 'lon': 79.8083, 'state': 'Puducherry'},
        'panaji': {'name': 'Panaji', 'lat': 15.4909, 'lon': 73.8278, 'state': 'Goa'},
        'dispur': {'name': 'Dispur', 'lat': 26.1433, 'lon': 91.7898, 'state': 'Assam'},
        'imphal': {'name': 'Imphal', 'lat': 24.8170, 'lon': 93.9368, 'state': 'Manipur'},
        'shillong': {'name': 'Shillong', 'lat': 25.5788, 'lon': 91.8933, 'state': 'Meghalaya'},
        'aizawl': {'name': 'Aizawl', 'lat': 23.7307, 'lon': 92.7173, 'state': 'Mizoram'},
        'kohima': {'name': 'Kohima', 'lat': 25.6751, 'lon': 94.1086, 'state': 'Nagaland'},
        'itanagar': {'name': 'Itanagar', 'lat': 27.0844, 'lon': 93.6053, 'state': 'Arunachal Pradesh'},
        'port-blair': {'name': 'Port Blair', 'lat': 11.6234, 'lon': 92.7265, 'state': 'Andaman and Nicobar'},
        'silvassa': {'name': 'Silvassa', 'lat': 20.2737, 'lon': 73.0135, 'state': 'Dadra and Nagar Haveli'},
        
        # Tourist & Hill Stations
        'shimla': {'name': 'Shimla', 'lat': 31.1048, 'lon': 77.1734, 'state': 'Himachal Pradesh'},
        'manali': {'name': 'Manali', 'lat': 32.2396, 'lon': 77.1887, 'state': 'Himachal Pradesh'},
        'dharamshala': {'name': 'Dharamshala', 'lat': 32.2190, 'lon': 76.3234, 'state': 'Himachal Pradesh'},
        'nainital': {'name': 'Nainital', 'lat': 29.3919, 'lon': 79.4542, 'state': 'Uttarakhand'},
        'mussoorie': {'name': 'Mussoorie', 'lat': 30.4598, 'lon': 78.0644, 'state': 'Uttarakhand'},
        'dehradun': {'name': 'Dehradun', 'lat': 30.3165, 'lon': 78.0322, 'state': 'Uttarakhand'},
        'rishikesh': {'name': 'Rishikesh', 'lat': 30.0869, 'lon': 78.2676, 'state': 'Uttarakhand'},
        'haridwar': {'name': 'Haridwar', 'lat': 29.9457, 'lon': 78.1642, 'state': 'Uttarakhand'},
        'darjeeling': {'name': 'Darjeeling', 'lat': 27.0410, 'lon': 88.2663, 'state': 'West Bengal'},
        'gangtok': {'name': 'Gangtok', 'lat': 27.3389, 'lon': 88.6065, 'state': 'Sikkim'},
        'srinagar': {'name': 'Srinagar', 'lat': 34.0837, 'lon': 74.7973, 'state': 'Jammu and Kashmir'},
        'leh': {'name': 'Leh', 'lat': 34.1526, 'lon': 77.5771, 'state': 'Ladakh'},
        'ooty': {'name': 'Ooty', 'lat': 11.4102, 'lon': 76.6950, 'state': 'Tamil Nadu'},
        'kodaikanal': {'name': 'Kodaikanal', 'lat': 10.2381, 'lon': 77.4892, 'state': 'Tamil Nadu'},
        'munnar': {'name': 'Munnar', 'lat': 10.0889, 'lon': 77.0595, 'state': 'Kerala'},
        'wayanad': {'name': 'Wayanad', 'lat': 11.6054, 'lon': 76.0837, 'state': 'Kerala'},
        'mount-abu': {'name': 'Mount Abu', 'lat': 24.5926, 'lon': 72.7156, 'state': 'Rajasthan'},
        'mahabaleshwar': {'name': 'Mahabaleshwar', 'lat': 17.9246, 'lon': 73.6577, 'state': 'Maharashtra'},
        'lonavala': {'name': 'Lonavala', 'lat': 18.7537, 'lon': 73.4086, 'state': 'Maharashtra'},
        'coorg': {'name': 'Coorg', 'lat': 12.3375, 'lon': 75.8069, 'state': 'Karnataka'},
        
        # Major Tier-2 Cities
        'kochi': {'name': 'Kochi', 'lat': 9.9312, 'lon': 76.2673, 'state': 'Kerala'},
        'mysore': {'name': 'Mysore', 'lat': 12.2958, 'lon': 76.6394, 'state': 'Karnataka'},
        'mangalore': {'name': 'Mangalore', 'lat': 12.9141, 'lon': 74.8560, 'state': 'Karnataka'},
        'hubli': {'name': 'Hubli', 'lat': 15.3647, 'lon': 75.1240, 'state': 'Karnataka'},
        'belgaum': {'name': 'Belgaum', 'lat': 15.8497, 'lon': 74.4977, 'state': 'Karnataka'},
        'tirupati': {'name': 'Tirupati', 'lat': 13.6288, 'lon': 79.4192, 'state': 'Andhra Pradesh'},
        'guntur': {'name': 'Guntur', 'lat': 16.3067, 'lon': 80.4365, 'state': 'Andhra Pradesh'},
        'nellore': {'name': 'Nellore', 'lat': 14.4426, 'lon': 79.9865, 'state': 'Andhra Pradesh'},
        'tirunelveli': {'name': 'Tirunelveli', 'lat': 8.7139, 'lon': 77.7567, 'state': 'Tamil Nadu'},
        'salem': {'name': 'Salem', 'lat': 11.6643, 'lon': 78.1460, 'state': 'Tamil Nadu'},
        'tiruchirappalli': {'name': 'Tiruchirappalli', 'lat': 10.7905, 'lon': 78.7047, 'state': 'Tamil Nadu'},
        'vellore': {'name': 'Vellore', 'lat': 12.9165, 'lon': 79.1325, 'state': 'Tamil Nadu'},
        'erode': {'name': 'Erode', 'lat': 11.3410, 'lon': 77.7172, 'state': 'Tamil Nadu'},
        'thrissur': {'name': 'Thrissur', 'lat': 10.5276, 'lon': 76.2144, 'state': 'Kerala'},
        'kollam': {'name': 'Kollam', 'lat': 8.8932, 'lon': 76.6141, 'state': 'Kerala'},
        'kozhikode': {'name': 'Kozhikode', 'lat': 11.2588, 'lon': 75.7804, 'state': 'Kerala'},
        'palakkad': {'name': 'Palakkad', 'lat': 10.7733, 'lon': 76.6547, 'state': 'Kerala'},
        'alappuzha': {'name': 'Alappuzha', 'lat': 9.4981, 'lon': 76.3388, 'state': 'Kerala'},
        
        # North India Cities
        'noida': {'name': 'Noida', 'lat': 28.5355, 'lon': 77.3910, 'state': 'Uttar Pradesh'},
        'gurugram': {'name': 'Gurugram', 'lat': 28.4595, 'lon': 77.0266, 'state': 'Haryana'},
        'rohtak': {'name': 'Rohtak', 'lat': 28.8955, 'lon': 76.6066, 'state': 'Haryana'},
        'panipat': {'name': 'Panipat', 'lat': 29.3909, 'lon': 76.9635, 'state': 'Haryana'},
        'karnal': {'name': 'Karnal', 'lat': 29.6857, 'lon': 76.9905, 'state': 'Haryana'},
        'ambala': {'name': 'Ambala', 'lat': 30.3782, 'lon': 76.7767, 'state': 'Haryana'},
        'patiala': {'name': 'Patiala', 'lat': 30.3398, 'lon': 76.3869, 'state': 'Punjab'},
        'jalandhar': {'name': 'Jalandhar', 'lat': 31.3260, 'lon': 75.5762, 'state': 'Punjab'},
        'bathinda': {'name': 'Bathinda', 'lat': 30.2110, 'lon': 74.9455, 'state': 'Punjab'},
        'mohali': {'name': 'Mohali', 'lat': 30.7046, 'lon': 76.7179, 'state': 'Punjab'},
        'jammu': {'name': 'Jammu', 'lat': 32.7266, 'lon': 74.8570, 'state': 'Jammu and Kashmir'},
        'udaipur': {'name': 'Udaipur', 'lat': 24.5854, 'lon': 73.7125, 'state': 'Rajasthan'},
        'ajmer': {'name': 'Ajmer', 'lat': 26.4499, 'lon': 74.6399, 'state': 'Rajasthan'},
        'bikaner': {'name': 'Bikaner', 'lat': 28.0229, 'lon': 73.3119, 'state': 'Rajasthan'},
        'alwar': {'name': 'Alwar', 'lat': 27.5530, 'lon': 76.6346, 'state': 'Rajasthan'},
        'bharatpur': {'name': 'Bharatpur', 'lat': 27.2152, 'lon': 77.4899, 'state': 'Rajasthan'},
        
        # Central & East India
        'bhubaneswar': {'name': 'Bhubaneswar', 'lat': 20.2961, 'lon': 85.8245, 'state': 'Odisha'},
        'cuttack': {'name': 'Cuttack', 'lat': 20.4625, 'lon': 85.8830, 'state': 'Odisha'},
        'puri': {'name': 'Puri', 'lat': 19.8135, 'lon': 85.8312, 'state': 'Odisha'},
        'rourkela': {'name': 'Rourkela', 'lat': 22.2604, 'lon': 84.8536, 'state': 'Odisha'},
        'jamshedpur': {'name': 'Jamshedpur', 'lat': 22.8046, 'lon': 86.2029, 'state': 'Jharkhand'},
        'dhanbad': {'name': 'Dhanbad', 'lat': 23.7957, 'lon': 86.4304, 'state': 'Jharkhand'},
        'bokaro': {'name': 'Bokaro', 'lat': 23.6693, 'lon': 86.1511, 'state': 'Jharkhand'},
        'durgapur': {'name': 'Durgapur', 'lat': 23.5204, 'lon': 87.3119, 'state': 'West Bengal'},
        'asansol': {'name': 'Asansol', 'lat': 23.6739, 'lon': 86.9524, 'state': 'West Bengal'},
        'siliguri': {'name': 'Siliguri', 'lat': 26.7271, 'lon': 88.3953, 'state': 'West Bengal'},
        'gaya': {'name': 'Gaya', 'lat': 24.7955, 'lon': 85.0002, 'state': 'Bihar'},
        'bhagalpur': {'name': 'Bhagalpur', 'lat': 25.2425, 'lon': 86.9842, 'state': 'Bihar'},
        'muzaffarpur': {'name': 'Muzaffarpur', 'lat': 26.1225, 'lon': 85.3906, 'state': 'Bihar'},
        'bilaspur': {'name': 'Bilaspur', 'lat': 22.0797, 'lon': 82.1409, 'state': 'Chhattisgarh'},
        'korba': {'name': 'Korba', 'lat': 22.3595, 'lon': 82.7501, 'state': 'Chhattisgarh'},
        'bhilai': {'name': 'Bhilai', 'lat': 21.2095, 'lon': 81.3785, 'state': 'Chhattisgarh'},
        'ujjain': {'name': 'Ujjain', 'lat': 23.1765, 'lon': 75.7885, 'state': 'Madhya Pradesh'},
        'sagar': {'name': 'Sagar', 'lat': 23.8388, 'lon': 78.7378, 'state': 'Madhya Pradesh'},
        'dewas': {'name': 'Dewas', 'lat': 22.9676, 'lon': 76.0534, 'state': 'Madhya Pradesh'},
        
        # Heavy Rainfall Regions (Monsoon Paradise) 🌧️
        'cherrapunji': {'name': 'Cherrapunji', 'lat': 25.2959, 'lon': 91.7324, 'state': 'Meghalaya'},  # Wettest place!
        'mawsynram': {'name': 'Mawsynram', 'lat': 25.2975, 'lon': 91.5805, 'state': 'Meghalaya'},  # 2nd wettest
        'mahabalipuram': {'name': 'Mahabalipuram', 'lat': 12.6269, 'lon': 80.1926, 'state': 'Tamil Nadu'},
        'pondicherry': {'name': 'Pondicherry', 'lat': 11.9416, 'lon': 79.8083, 'state': 'Puducherry'},
        'kannur': {'name': 'Kannur', 'lat': 11.8745, 'lon': 75.3704, 'state': 'Kerala'},
        'kottayam': {'name': 'Kottayam', 'lat': 9.5916, 'lon': 76.5222, 'state': 'Kerala'},
        'idukki': {'name': 'Idukki', 'lat': 9.9189, 'lon': 77.1025, 'state': 'Kerala'},
        'udupi': {'name': 'Udupi', 'lat': 13.3409, 'lon': 74.7421, 'state': 'Karnataka'},
        'karwar': {'name': 'Karwar', 'lat': 14.8137, 'lon': 74.1290, 'state': 'Karnataka'},
        'ratnagiri': {'name': 'Ratnagiri', 'lat': 16.9944, 'lon': 73.3000, 'state': 'Maharashtra'},
        'alibag': {'name': 'Alibag', 'lat': 18.6414, 'lon': 72.8722, 'state': 'Maharashtra'},
        'mahabaleshwar': {'name': 'Mahabaleshwar', 'lat': 17.9246, 'lon': 73.6577, 'state': 'Maharashtra'},
        'amboli': {'name': 'Amboli', 'lat': 15.9589, 'lon': 74.0047, 'state': 'Maharashtra'},
        'tezpur': {'name': 'Tezpur', 'lat': 26.6338, 'lon': 92.8000, 'state': 'Assam'},
        'dibrugarh': {'name': 'Dibrugarh', 'lat': 27.4728, 'lon': 94.9120, 'state': 'Assam'},
        'silchar': {'name': 'Silchar', 'lat': 24.8333, 'lon': 92.7789, 'state': 'Assam'},
        'agartala': {'name': 'Agartala', 'lat': 23.8315, 'lon': 91.2868, 'state': 'Tripura'},
        
        # Snowfall Destinations ❄️
        'gulmarg': {'name': 'Gulmarg', 'lat': 34.0484, 'lon': 74.3805, 'state': 'Jammu and Kashmir'},  # Ski resort
        'pahalgam': {'name': 'Pahalgam', 'lat': 34.0161, 'lon': 75.3150, 'state': 'Jammu and Kashmir'},
        'sonamarg': {'name': 'Sonamarg', 'lat': 34.3000, 'lon': 75.2833, 'state': 'Jammu and Kashmir'},
        'dalhousie': {'name': 'Dalhousie', 'lat': 32.5448, 'lon': 75.9470, 'state': 'Himachal Pradesh'},
        'kullu': {'name': 'Kullu', 'lat': 31.9578, 'lon': 77.1093, 'state': 'Himachal Pradesh'},
        'spiti': {'name': 'Spiti', 'lat': 32.2466, 'lon': 78.0336, 'state': 'Himachal Pradesh'},
        'keylong': {'name': 'Keylong', 'lat': 32.5721, 'lon': 77.0353, 'state': 'Himachal Pradesh'},
        'chamba': {'name': 'Chamba', 'lat': 32.5562, 'lon': 76.1265, 'state': 'Himachal Pradesh'},
        'auli': {'name': 'Auli', 'lat': 30.5323, 'lon': 79.5833, 'state': 'Uttarakhand'},  # Ski destination
        'kedarnath': {'name': 'Kedarnath', 'lat': 30.7346, 'lon': 79.0669, 'state': 'Uttarakhand'},
        'badrinath': {'name': 'Badrinath', 'lat': 30.7433, 'lon': 79.4938, 'state': 'Uttarakhand'},
        'kargil': {'name': 'Kargil', 'lat': 34.5539, 'lon': 76.1313, 'state': 'Ladakh'},
        'tawang': {'name': 'Tawang', 'lat': 27.5860, 'lon': 91.8597, 'state': 'Arunachal Pradesh'},  # High altitude
        'sandakphu': {'name': 'Sandakphu', 'lat': 27.1095, 'lon': 88.0146, 'state': 'West Bengal'},  # Near Darjeeling
        'yumthang': {'name': 'Yumthang Valley', 'lat': 27.8100, 'lon': 88.7114, 'state': 'Sikkim'},  # Valley of flowers
    }
    
    def __init__(self, data_dir: str = "data/raw", cache_days: int = 1):
        """Initialize with 1-day cache for lightweight operation."""
        self.data_dir = data_dir
        self.cache_days = cache_days
        # Use Streamlit secrets for API key (renamed to OPENWEATHER_API_KEY per request)
        try:
            self.api_key = st.secrets["OPENWEATHER_API_KEY"]
        except (KeyError, AttributeError, FileNotFoundError):
            # Fallback to env var if secrets not found (useful for local development)
            self.api_key = os.getenv('OPENWEATHERMAP_API_KEY', '') or os.getenv('OPENWEATHER_API_KEY', '')
        os.makedirs(data_dir, exist_ok=True)
    
    @staticmethod
    def get_city_list():
        """Get sorted list of city names for dropdown."""
        return sorted([city['name'] for city in WeatherDataLoader.INDIAN_CITIES.values()])
    
    @staticmethod
    def get_city_info(city_name: str) -> dict:
        """Get city coordinates by name."""
        city_key = city_name.lower().replace(' ', '').replace('-', '')
        
        for key, info in WeatherDataLoader.INDIAN_CITIES.items():
            if info['name'].lower().replace(' ', '') == city_key or key == city_key:
                return info
        
        raise ValueError(f"City '{city_name}' not found in database")
    
    # NO CACHING - Always fetch fresh data for accuracy
    def get_realtime_weather(self, city_name: str) -> dict:
        """
        Fetch real-time weather from OpenWeatherMap API.
        Uses main['temp'] for actual temperature (NOT feels_like).
        
        Returns:
            dict: Current weather data with temperature, description, data_source, etc.
        """
        if not self.api_key or self.api_key == 'your_api_key_here_get_from_openweathermap_org':
            # Return mock data if no API key
            return self._get_mock_weather(city_name)
        
        try:
            city_info = WeatherDataLoader.get_city_info(city_name)
            
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': city_info['lat'],
                'lon': city_info['lon'],
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Use main['temp'] for actual temperature (NOT feels_like)
            return {
                'temperature': round(data['main']['temp'], 1),  # Actual temperature
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'icon_url': f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
                'clouds': data['clouds']['all'],
                'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
                'timestamp': datetime.fromtimestamp(data['dt']),
                'data_source': f"OpenWeatherMap API ({city_info['lat']:.2f}, {city_info['lon']:.2f})"
            }
        except Exception as e:
            st.warning(f"Could not fetch real-time data: {str(e)}. Using mock data.")
            return self._get_mock_weather(city_name)
    
    def _get_mock_weather(self, city_name: str) -> dict:
        """Fallback mock weather data when API is unavailable."""
        import random
        return {
            'temperature': round(25 + random.uniform(-5, 5), 1),
            'feels_like': round(26 + random.uniform(-5, 5), 1),
            'humidity': random.randint(40, 80),
            'pressure': random.randint(1008, 1018),
            'wind_speed': round(random.uniform(5, 20), 1),
            'description': random.choice(['Clear Sky', 'Partly Cloudy', 'Light Rain', 'Haze']),
            'icon': '01d',
            'icon_url': 'http://openweathermap.org/img/wn/01d@2x.png',
            'clouds': random.randint(0, 50),
            'visibility': round(random.uniform(5, 10), 1),
            'timestamp': datetime.now(),
            'data_source': 'Mock Data (No API Key)'
        }
    
    # NO CACHING on historical data to ensure fresh data
    def fetch_historical_data(self, city_name: str, days: int = 30) -> pd.DataFrame:
        """
        Fetch historical data from Meteostat (default 30 days).
        Falls back to Delhi if city has no data.
        
        Parameters:
            city_name (str): Name of the city
            days (int): Number of days to fetch (default 30)
        
        Returns:
            pd.DataFrame: Historical weather data with 'meteostat_source' attribute
        """
        # Check file cache (still useful for offline)
        cache_file = os.path.join(self.data_dir, f"{city_name.lower().replace(' ', '_')}_30days.csv")
        
        if os.path.exists(cache_file):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_age.days < self.cache_days:
                df = pd.read_csv(cache_file, parse_dates=['date'])
                df.set_index('date', inplace=True)
                df.attrs['meteostat_source'] = f"File cache: {city_name}"
                return df
        
        # Fetch fresh data
        city_info = WeatherDataLoader.get_city_info(city_name)
        original_city = city_name
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Try fetching data with increasing search radius
        location = Point(city_info['lat'], city_info['lon'])
        meteostat_source = f"Meteostat: {city_name} ({city_info['lat']:.2f}, {city_info['lon']:.2f})"
        
        # First attempt: Default radius
        data = Daily(location, start_date, end_date)
        df = data.fetch()
        
        # Second attempt: Expand radius to find nearby stations
        if df.empty:
            for lat_offset in [0.5, -0.5, 1.0, -1.0]:
                for lon_offset in [0.5, -0.5, 1.0, -1.0]:
                    nearby_location = Point(
                        city_info['lat'] + lat_offset,
                        city_info['lon'] + lon_offset
                    )
                    data = Daily(nearby_location, start_date, end_date)
                    df = data.fetch()
                    if not df.empty:
                        meteostat_source = f"Meteostat: Nearby station ({city_info['lat'] + lat_offset:.2f}, {city_info['lon'] + lon_offset:.2f})"
                        break
                if not df.empty:
                    break
        
        # Third attempt: FALLBACK TO DELHI if still no data
        if df.empty:
            st.warning(f"⚠️ No Meteostat data for {city_name}. Using Delhi as fallback.")
            delhi_info = WeatherDataLoader.get_city_info('Delhi')
            delhi_location = Point(delhi_info['lat'], delhi_info['lon'])
            data = Daily(delhi_location, start_date, end_date)
            df = data.fetch()
            meteostat_source = f"Meteostat: Delhi fallback (28.70, 77.10)"
            
            # If even Delhi fails, generate synthetic
            if df.empty:
                st.warning(f"⚠️ Meteostat unavailable. Using estimated data.")
                df = self._generate_synthetic_data(city_name, start_date, end_date)
                meteostat_source = f"Synthetic data (estimated for {city_name})"
        
        # Save to cache
        df.reset_index(inplace=True)
        df.rename(columns={'time': 'date'}, inplace=True)
        df.to_csv(cache_file, index=False)
        
        df.set_index('date', inplace=True)
        df.attrs['meteostat_source'] = meteostat_source
        return df
    
    def _generate_synthetic_data(self, city_name: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Generate realistic synthetic weather data for cities without weather stations.
        Based on regional climate patterns, elevation, and seasons.
        """
        import random
        import numpy as np
        
        city_info = WeatherDataLoader.get_city_info(city_name)
        lat = city_info['lat']
        city_key = city_name.lower().replace(' ', '')
        
        # Hill stations and elevated cities (much cooler than plains)
        hill_stations = {
            'shimla', 'manali', 'kullu', 'dalhousie', 'dharamshala', 'mcleodganj',
            'dehradun', 'mussoorie', 'nainital', 'almora', 'ranikhet',
            'ooty', 'kodaikanal', 'munnar', 'darjeeling', 'gangtok',
            'shillong', 'cherrapunji', 'mawsynram', 'tawang', 'aizawl',
            'mahabaleshwar', 'lonavala', 'panchgani', 'coorg', 'wayanad',
            'gulmarg', 'pahalgam', 'sonamarg', 'leh', 'kargil',
            'spitivalley', 'keylong', 'auli', 'kedarnath', 'badrinath',
            'sandakphu', 'yumthangvalley'
        }
        
        # Coastal cities (moderate temperature, high humidity)
        coastal_cities = {
            'mumbai', 'goa', 'kochi', 'thiruvananthapuram', 'kozhikode',
            'mangalore', 'udupi', 'karwar', 'ratnagiri', 'alibag',
            'chennai', 'visakhapatnam', 'puducherry', 'mahabalipuram',
            'portblair', 'panjim', 'vasco', 'margao'
        }
        
        # Desert/hot regions
        hot_dry_cities = {
            'jaisalmer', 'bikaner', 'jodhpur', 'ajmer', 'udaipur',
            'ahmedabad', 'rajkot', 'surat', 'vadodara'
        }
        
        # Determine climate zone
        if city_key in hill_stations or 'hill' in city_key or 'ganj' in city_key:
            # Hill stations: Cool year-round
            if lat > 32:  # High altitude (Leh, Kargil)
                base_temp = 10
                temp_variation = 12
            elif lat > 28:  # Medium altitude (Shimla, Dehradun)
                base_temp = 18
                temp_variation = 10
            else:  # Southern hills (Ooty, Munnar)
                base_temp = 20
                temp_variation = 6
        elif city_key in coastal_cities:
            # Coastal: Moderate, less variation
            base_temp = 28
            temp_variation = 4
        elif city_key in hot_dry_cities:
            # Desert/hot: Very hot in summer
            base_temp = 32
            temp_variation = 14
        else:
            # Regular cities by latitude
            if lat > 30:  # Northern regions
                base_temp = 15
                temp_variation = 15
            elif lat > 25:  # Northern plains
                base_temp = 25
                temp_variation = 12
            elif lat > 20:  # Central India
                base_temp = 28
                temp_variation = 8
            elif lat > 15:  # South Central
                base_temp = 27
                temp_variation = 6
            else:  # Deep South
                base_temp = 28
                temp_variation = 5
        
        # Generate dates
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        num_days = len(dates)
        
        # Generate realistic temperature with seasonal variation
        day_of_year = np.array([d.timetuple().tm_yday for d in dates])
        
        # Seasonal cycle (peaks in summer around day 150-180)
        seasonal_factor = np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Base temperature with seasonality
        tavg = base_temp + seasonal_factor * temp_variation + np.random.normal(0, 2, num_days)
        tmax = tavg + np.random.uniform(3, 7, num_days)
        tmin = tavg - np.random.uniform(3, 7, num_days)
        
        # Generate precipitation (monsoon-aware)
        month = np.array([d.month for d in dates])
        
        # Different monsoon patterns
        if city_key in ['cherrapunji', 'mawsynram']:  # Wettest places
            monsoon_factor = np.where((month >= 6) & (month <= 9), 3.0, 0.5)
        elif city_key in coastal_cities or lat < 20:  # Coastal/South
            monsoon_factor = np.where((month >= 6) & (month <= 9), 1.5, 0.3)
        else:  # Regular cities
            monsoon_factor = np.where((month >= 6) & (month <= 9), 1.0, 0.2)
        
        prcp = np.random.exponential(5, num_days) * monsoon_factor
        prcp = np.clip(prcp, 0, 150)  # Realistic limits
        
        # Generate other weather parameters
        wspd = np.random.uniform(5, 25, num_days)
        
        # Pressure varies with elevation (approximate)
        if city_key in hill_stations:
            base_pressure = 950  # Lower at elevation
        else:
            base_pressure = 1013  # Sea level
        pres = np.random.normal(base_pressure, 5, num_days)
        
        # Create DataFrame
        df = pd.DataFrame({
            'time': dates,
            'tavg': tavg.round(1),
            'tmin': tmin.round(1),
            'tmax': tmax.round(1),
            'prcp': prcp.round(1),
            'wspd': wspd.round(1),
            'pres': pres.round(1)
        })
        
        df.set_index('time', inplace=True)
        return df

    
    @staticmethod
    def get_weather_emoji(icon_code: str) -> str:
        """
        Map OpenWeatherMap icon codes to animated emojis.
        
        Args:
            icon_code (str): Icon code from API (e.g. '01d')
            
        Returns:
            str: HTML string with animated emoji
        """
        # Mapping base icons to (emoji, animation_class)
        icon_map = {
            '01d': ('☀️', 'sun-motion'),        # Clear sun
            '01n': ('🌙', 'moon-motion'),       # Clear moon (night)
            '02d': ('🌤️', 'cloud-motion'),      # Partly cloudy day
            '01n': ('🌙', 'moon-motion'),       # Night moon priority
            '02n': ('🌙', 'moon-motion'),       # Partly cloudy night -> Moon (user request)
            '03d': ('☁️', 'cloud-motion'),       # Scattered clouds
            '03n': ('☁️', 'cloud-motion'),
            '04d': ('☁️', 'cloud-motion'),       # Broken clouds
            '04n': ('☁️', 'cloud-motion'),
            '09d': ('🌧️', 'rain-motion'),        # Shower rain
            '09n': ('🌧️', 'rain-motion'),
            '10d': ('🌧️', 'rain-motion'),        # Rain (rain with clouds)
            '10n': ('🌧️', 'rain-motion'),
            '11d': ('⛈️', 'thunder-motion'),     # Thunderstorm (cloud with lightning)
            '11n': ('⛈️', 'thunder-motion'),
            '13d': ('❄️', 'snow-motion'),        # Snowy
            '13n': ('❄️', 'snow-motion'),
            '50d': ('🌫️', 'cloud-motion'),       # Mist/Haze
            '50n': ('🌫️', 'cloud-motion'),
        }
        
        emoji, animation_class = icon_map.get(icon_code, ('🌤️', 'cloud-motion'))
        return f'<span class="{animation_class}">{emoji}</span>'


# Quick test
if __name__ == "__main__":
    loader = WeatherDataLoader()
    print(f"Total Indian cities: {len(loader.INDIAN_CITIES)}")
    print(f"City list sample: {loader.get_city_list()[:10]}")
    
    # Test city lookup
    mumbai_info = WeatherDataLoader.get_city_info("Mumbai")
    print(f"\nMumbai Info: {mumbai_info}")
