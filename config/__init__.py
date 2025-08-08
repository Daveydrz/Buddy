"""
Main configuration module for Buddy Voice Assistant
Re-exports from modular config files to maintain backward compatibility
"""

# Import all modular configs
from config.core import *
from config.audio import *  
from config.models import *

# Import remaining config from original config.py
import os
from datetime import datetime
import pytz

# ==== LOCATION & TIME DETECTION ====
try:
    # Try to import precise location manager
    from utils.location_manager import get_precise_location, get_current_time, get_time_info, get_precise_location_summary, get_weather_location_data
    PRECISE_LOCATION_AVAILABLE = True
    
    # PRIORITIZE GPS LOCATION: Check for GPS file first, then fallback to IP
    print(f"[Config] 🔍 Checking for GPS location file...")
    
    # Try to load GPS location first
    gps_location_found = False
    try:
        import json
        gps_files = [
            'buddy_gps_location.json',
            'buddy_gps_location_birtinya.json',
            'buddy_gps_location_2025-07-06.json'
        ]
        
        for gps_file in gps_files:
            if os.path.exists(gps_file):
                with open(gps_file, 'r') as f:
                    gps_data = json.load(f)
                
                print(f"[Config] 📍 Found GPS location file: {gps_file}")
                print(f"[Config] 🎯 GPS Location: {gps_data.get('suburb')}, {gps_data.get('state')}")
                
                # Use GPS data instead of IP location
                USER_STREET_ADDRESS = gps_data.get('street_address', '')
                USER_SUBURB = gps_data.get('suburb', '')
                USER_DISTRICT = gps_data.get('district', '')
                USER_LOCATION = gps_data.get('city', gps_data.get('suburb', ''))
                USER_STATE = gps_data.get('state', '')
                USER_COUNTRY = gps_data.get('country', 'Australia')
                USER_POSTAL_CODE = gps_data.get('postal_code', '')
                USER_TIMEZONE = gps_data.get('timezone', 'Australia/Brisbane')
                USER_TIMEZONE_OFFSET = gps_data.get('timezone_offset', '+10:00')
                USER_COORDINATES = (gps_data.get('latitude'), gps_data.get('longitude'))
                USER_PUBLIC_IP = "GPS-Based"
                USER_LOCAL_IP = "GPS-Based"
                USER_ISP = "GPS-Based"
                LOCATION_SOURCE = "GPS"
                LOCATION_CONFIDENCE = gps_data.get('confidence', 'HIGH')
                LOCATION_ACCURACY = 10.0  # GPS is very accurate
                
                gps_location_found = True
                print(f"[Config] ✅ Using GPS location: {USER_SUBURB}, {USER_STATE}")
                break
                
    except Exception as e:
        print(f"[Config] ⚠️ Could not load GPS location: {e}")
    
    # If no GPS location, use IP location manager
    if not gps_location_found:
        print(f"[Config] 🌐 No GPS file found, using IP-based location...")
        precise_location = get_precise_location()
        time_info = get_time_info()
        
        print(f"[Config] 🎯 IP LOCATION DETECTED:")
        print(f"  Confidence: {precise_location.confidence}")
        print(f"  Source: {precise_location.source}")
        print(f"  Accuracy: {precise_location.accuracy_meters:.0f} meters")
        
        # Use detected IP-based information
        USER_STREET_ADDRESS = precise_location.street_address
        USER_SUBURB = precise_location.suburb
        USER_DISTRICT = precise_location.district
        USER_LOCATION = precise_location.city
        USER_STATE = precise_location.state  
        USER_COUNTRY = precise_location.country
        USER_POSTAL_CODE = precise_location.postal_code
        USER_TIMEZONE = precise_location.timezone
        USER_TIMEZONE_OFFSET = precise_location.timezone_offset
        USER_COORDINATES = (precise_location.latitude, precise_location.longitude)
        USER_PUBLIC_IP = precise_location.public_ip
        USER_LOCAL_IP = precise_location.local_ip
        USER_ISP = precise_location.isp
        LOCATION_SOURCE = precise_location.source
        LOCATION_CONFIDENCE = precise_location.confidence
        LOCATION_ACCURACY = precise_location.accuracy_meters
    
    # For weather API
    WEATHER_LOCATION_DATA = get_weather_location_data() if not gps_location_found else {
        'latitude': str(USER_COORDINATES[0]),
        'longitude': str(USER_COORDINATES[1]),
        'city': USER_LOCATION,
        'state': USER_STATE,
        'country': USER_COUNTRY,
        'postal_code': USER_POSTAL_CODE,
        'timezone': USER_TIMEZONE
    }
    
except ImportError as e:
    print(f"[Config] ⚠️ Location manager not available: {e}")
    PRECISE_LOCATION_AVAILABLE = False
    
    # Fallback location data
    USER_STREET_ADDRESS = ""
    USER_SUBURB = ""
    USER_DISTRICT = ""
    USER_LOCATION = "Brisbane"
    USER_STATE = "Queensland"
    USER_COUNTRY = "Australia"
    USER_POSTAL_CODE = "4000"
    USER_TIMEZONE = "Australia/Brisbane"
    USER_TIMEZONE_OFFSET = "+10:00"
    USER_COORDINATES = (-27.4698, 153.0251)
    USER_PUBLIC_IP = "unknown"
    USER_LOCAL_IP = "unknown"
    USER_ISP = "unknown"
    LOCATION_SOURCE = "fallback"
    LOCATION_CONFIDENCE = "LOW"
    LOCATION_ACCURACY = 10000.0
    
    WEATHER_LOCATION_DATA = {
        'latitude': str(USER_COORDINATES[0]),
        'longitude': str(USER_COORDINATES[1]),
        'city': USER_LOCATION,
        'state': USER_STATE,
        'country': USER_COUNTRY,
        'postal_code': USER_POSTAL_CODE,
        'timezone': USER_TIMEZONE
    }

# Re-export all the remaining config variables from the original huge config
# This maintains backward compatibility while allowing gradual migration

# Import modular startup functions and call them
if __name__ != "__main__":
    # Only run startup when imported, not when run directly
    from config.core import startup_summary as core_startup
    from config.audio import startup_summary as audio_startup  
    from config.models import startup_summary as models_startup
    
    core_startup()
    audio_startup()
    models_startup()