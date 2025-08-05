# utils/gps_location_manager.py - GPS Location Manager for Buddy
import json
import os
import time
from datetime import datetime
import pytz
from dataclasses import dataclass
from typing import Optional

@dataclass
class GPSLocationInfo:
    """GPS-precise location information"""
    # Precise coordinates
    latitude: float
    longitude: float
    
    # Detailed address
    house_number: str
    street_name: str
    street_address: str
    suburb: str
    district: str
    city: str
    state: str
    country: str
    postal_code: str
    
    # Geographic details
    region: str
    county: str
    
    # Timezone information
    timezone: str
    timezone_offset: str
    current_time: str
    
    # Network information
    public_ip: str
    local_ip: str
    isp: str
    
    # GPS accuracy and source
    accuracy_meters: float
    source: str
    confidence: str
    timestamp: str
    user: str

class GPSLocationManager:
    """GPS Location Manager with browser integration"""
    
    def __init__(self):
        self.gps_location_file = "buddy_gps_location.json"
        self.manual_location_file = "buddy_manual_location.json"
        self.cached_location = None
        self.last_update = None
        
    def get_gps_location(self) -> Optional[GPSLocationInfo]:
        """Get GPS location from browser-generated file"""
        
        # Check for GPS location file first
        gps_files = [
            self.gps_location_file,
            "buddy_gps_location_2025-07-06.json",
            # Look for any GPS location file
        ]
        
        # Also check for any file starting with buddy_gps_location
        try:
            for filename in os.listdir('.'):
                if filename.startswith('buddy_gps_location') and filename.endswith('.json'):
                    gps_files.append(filename)
        except:
            pass
        
        for filepath in gps_files:
            if os.path.exists(filepath):
                try:
                    print(f"[GPSLocation] 📍 Found GPS location file: {filepath}")
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    # Convert dict to GPSLocationInfo
                    gps_location = GPSLocationInfo(
                        latitude=data.get('latitude', -27.4698),
                        longitude=data.get('longitude', 153.0251),
                        house_number=data.get('house_number', ''),
                        street_name=data.get('street_name', ''),
                        street_address=data.get('street_address', ''),
                        suburb=data.get('suburb', ''),
                        district=data.get('district', ''),
                        city=data.get('city', 'Brisbane'),
                        state=data.get('state', 'Queensland'),
                        country=data.get('country', 'Australia'),
                        postal_code=data.get('postal_code', ''),
                        region=data.get('region', 'Oceania'),
                        county=data.get('county', 'Queensland'),
                        timezone=data.get('timezone', 'Australia/Brisbane'),
                        timezone_offset=data.get('timezone_offset', '+10:00'),
                        current_time=data.get('current_time', ''),
                        public_ip=data.get('public_ip', 'auto-detect'),
                        local_ip=data.get('local_ip', 'auto-detect'),
                        isp=data.get('isp', 'GPS Location'),
                        accuracy_meters=data.get('accuracy_meters', 10.0),
                        source=data.get('source', 'GPS'),
                        confidence=data.get('confidence', 'GPS_HIGH'),
                        timestamp=data.get('timestamp', ''),
                        user=data.get('user', 'Daveydrz')
                    )
                    
                    print(f"[GPSLocation] ✅ GPS location loaded:")
                    print(f"  Address: {gps_location.street_address}")
                    print(f"  Suburb: {gps_location.suburb}")
                    print(f"  Accuracy: {gps_location.accuracy_meters}m")
                    print(f"  Confidence: {gps_location.confidence}")
                    
                    self.cached_location = gps_location
                    self.last_update = time.time()
                    
                    return gps_location
                    
                except Exception as e:
                    print(f"[GPSLocation] Error reading {filepath}: {e}")
        
        return None
    
    def get_current_location(self) -> GPSLocationInfo:
        """Get current location (GPS preferred, fallback to manual/IP)"""
        
        # Try GPS location first
        gps_location = self.get_gps_location()
        if gps_location:
            return gps_location
        
        # Try manual location
        manual_location = self.get_manual_location()
        if manual_location:
            return manual_location
        
        # Fallback to Brisbane
        print("[GPSLocation] ⚠️ No GPS or manual location found, using Brisbane fallback")
        return self.get_fallback_location()
    
    def get_manual_location(self) -> Optional[GPSLocationInfo]:
        """Get manually set location"""
        if os.path.exists(self.manual_location_file):
            try:
                with open(self.manual_location_file, 'r') as f:
                    data = json.load(f)
                return GPSLocationInfo(**data)
            except Exception as e:
                print(f"[GPSLocation] Manual location error: {e}")
        return None
    
    def get_fallback_location(self) -> GPSLocationInfo:
        """Brisbane fallback location"""
        try:
            brisbane_tz = pytz.timezone("Australia/Brisbane")
            current_time = datetime.now(brisbane_tz).strftime("%Y-%m-%d %H:%M:%S")
            timezone_offset = "+10:00"
        except:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timezone_offset = "+10:00"
        
        return GPSLocationInfo(
            latitude=-27.4698,
            longitude=153.0251,
            house_number="",
            street_name="",
            street_address="",
            suburb="",
            district="",
            city="Brisbane",
            state="Queensland",
            country="Australia",
            postal_code="4000",
            region="Oceania",
            county="Brisbane",
            timezone="Australia/Brisbane",
            timezone_offset=timezone_offset,
            current_time=current_time,
            public_ip="auto-detect",
            local_ip="auto-detect",
            isp="Unknown",
            accuracy_meters=10000.0,
            source="fallback",
            confidence="LOW",
            timestamp=datetime.now().isoformat(),
            user="Daveydrz"
        )
    
    def get_location_summary(self) -> str:
        """Get human-readable location summary"""
        location = self.get_current_location()
        
        parts = []
        
        # Add street address if available
        if location.street_address:
            parts.append(location.street_address)
        
        # Add suburb if available and different from city
        if location.suburb and location.suburb != location.city:
            parts.append(location.suburb)
        
        # Add city
        if location.city:
            parts.append(location.city)
        
        # Add state
        if location.state:
            parts.append(location.state)
        
        # Add postal code if available
        if location.postal_code:
            parts.append(location.postal_code)
        
        summary = ", ".join(parts) if parts else "Unknown location"
        
        print(f"[GPSLocation] 📍 Summary: {summary} ({location.confidence} confidence, {location.accuracy_meters}m accuracy)")
        
        return summary
    
    def get_weather_coordinates(self) -> tuple:
        """Get coordinates for weather API"""
        location = self.get_current_location()
        return (location.latitude, location.longitude)
    
    def save_manual_location(self, location_data: dict):
        """Save manual location override"""
        try:
            with open(self.manual_location_file, 'w') as f:
                json.dump(location_data, f, indent=2)
            print("[GPSLocation] ✅ Manual location saved")
        except Exception as e:
            print(f"[GPSLocation] Manual save error: {e}")

# Global instance
gps_location_manager = GPSLocationManager()

# Public interface functions
def get_gps_location() -> GPSLocationInfo:
    """Get GPS location information"""
    return gps_location_manager.get_current_location()

def get_gps_location_summary() -> str:
    """Get GPS location summary"""
    return gps_location_manager.get_location_summary()

def get_gps_coordinates() -> tuple:
    """Get GPS coordinates for weather"""
    return gps_location_manager.get_weather_coordinates()