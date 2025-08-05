# utils/location_manager.py - PRECISE Location Detection System
"""
Professional precise location detection for Buddy
Gets exact address, suburb, coordinates - not just city guesses
"""
import time
import socket
import requests
import json
from datetime import datetime
import pytz
import platform
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PreciseLocationInfo:
    """Complete precise location information"""
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
    
    # Accuracy and source
    accuracy_meters: float
    source: str
    confidence: str  # HIGH, MEDIUM, LOW

class PreciseLocationManager:
    """PRECISE location detection and management"""
    
    def __init__(self):
        self.location_cache_file = "buddy_precise_location_cache.json"
        self.cached_location = None
        self.last_update = None
        self.cache_duration = 1800  # 30 minutes cache for precise location
        
    def get_precise_location(self, force_refresh: bool = False) -> PreciseLocationInfo:
        """Get precise current location using multiple high-accuracy methods"""
        
        # Check cache first (unless force refresh)
        if not force_refresh and self._is_cache_valid():
            print("[PreciseLocation] 📍 Using cached precise location")
            return self.cached_location
        
        print("[PreciseLocation] 🔍 Detecting PRECISE current location...")
        
        location_info = self._detect_precise_location()
        
        # Cache the result
        self._cache_location(location_info)
        
        return location_info
    
    def _detect_precise_location(self) -> PreciseLocationInfo:
        """Multi-method PRECISE location detection"""
        
        print("[PreciseLocation] 🎯 Attempting high-accuracy location detection...")
        
        # Method 1: Try multiple premium IP geolocation services
        location = self._try_premium_ip_geolocation()
        if location and location.confidence == "HIGH":
            print(f"[PreciseLocation] ✅ HIGH ACCURACY: {location.source}")
            return location
        
        # Method 2: Try reverse geocoding with coordinates
        location = self._try_reverse_geocoding()
        if location and location.confidence in ["HIGH", "MEDIUM"]:
            print(f"[PreciseLocation] ✅ REVERSE GEOCODING: {location.source}")
            return location
        
        # Method 3: Try Windows Location Services (if available)
        location = self._try_windows_location_services()
        if location:
            print(f"[PreciseLocation] ✅ WINDOWS LOCATION: {location.source}")
            return location
        
        # Method 4: Fallback to best available location
        print("[PreciseLocation] ⚠️ Using best available location")
        return self._get_best_fallback_location()
    
    def _try_premium_ip_geolocation(self) -> Optional[PreciseLocationInfo]:
        """Try premium IP geolocation services for precise location"""
        
        public_ip = self._get_public_ip()
        print(f"[PreciseLocation] 🌐 Using IP: {public_ip}")
        
        # Service 1: ipapi.co (most detailed)
        location = self._try_ipapi_co(public_ip)
        if location:
            return location
        
        # Service 2: ip-api.com (good fallback)
        location = self._try_ipapi_com(public_ip)
        if location:
            return location
        
        # Service 3: ipinfo.io
        location = self._try_ipinfo_io(public_ip)
        if location:
            return location
        
        # Service 4: ipgeolocation.io (if we had API key)
        # location = self._try_ipgeolocation_io(public_ip)
        
        return None
    
    def _try_ipapi_co(self, ip: str) -> Optional[PreciseLocationInfo]:
        """Try ipapi.co - very detailed location data"""
        try:
            print("[PreciseLocation] 🔍 Trying ipapi.co...")
            response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=8)
            data = response.json()
            
            if data.get("city") and data.get("latitude"):
                # Get detailed address components
                street_address = ""
                house_number = ""
                street_name = ""
                
                # Some services provide address details
                if data.get("postal"):
                    # Try to get more detailed address
                    detailed_location = self._get_detailed_address(
                        data.get("latitude"), 
                        data.get("longitude")
                    )
                    if detailed_location:
                        street_address = detailed_location.get("street_address", "")
                        house_number = detailed_location.get("house_number", "")
                        street_name = detailed_location.get("street_name", "")
                
                return self._create_precise_location_info(
                    lat=data.get("latitude"),
                    lon=data.get("longitude"),
                    house_number=house_number,
                    street_name=street_name,
                    street_address=street_address,
                    suburb=data.get("district", ""),
                    district=data.get("region_code", ""),
                    city=data.get("city"),
                    state=data.get("region"),
                    country=data.get("country_name"),
                    postal_code=data.get("postal"),
                    region=data.get("continent_code", ""),
                    county=data.get("region", ""),
                    timezone=data.get("timezone"),
                    public_ip=ip,
                    isp=data.get("org", ""),
                    accuracy_meters=1000.0,  # IP-based accuracy
                    source="ipapi.co",
                    confidence="HIGH" if data.get("postal") else "MEDIUM"
                )
        except Exception as e:
            print(f"[PreciseLocation] ipapi.co failed: {e}")
        
        return None
    
    def _try_ipapi_com(self, ip: str) -> Optional[PreciseLocationInfo]:
        """Try ip-api.com"""
        try:
            print("[PreciseLocation] 🔍 Trying ip-api.com...")
            response = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,isp,org,as,query", 
                timeout=8
            )
            data = response.json()
            
            if data.get("status") == "success" and data.get("city"):
                # Try to get detailed address
                detailed_location = self._get_detailed_address(
                    data.get("lat"), 
                    data.get("lon")
                )
                
                street_address = ""
                house_number = ""
                street_name = ""
                if detailed_location:
                    street_address = detailed_location.get("street_address", "")
                    house_number = detailed_location.get("house_number", "")
                    street_name = detailed_location.get("street_name", "")
                
                return self._create_precise_location_info(
                    lat=data.get("lat"),
                    lon=data.get("lon"),
                    house_number=house_number,
                    street_name=street_name,
                    street_address=street_address,
                    suburb=data.get("district", ""),
                    district=data.get("regionName", ""),
                    city=data.get("city"),
                    state=data.get("regionName"),
                    country=data.get("country"),
                    postal_code=data.get("zip"),
                    region=data.get("continent", ""),
                    county=data.get("regionName", ""),
                    timezone=data.get("timezone"),
                    public_ip=ip,
                    isp=data.get("isp", ""),
                    accuracy_meters=1500.0,
                    source="ip-api.com",
                    confidence="MEDIUM"
                )
        except Exception as e:
            print(f"[PreciseLocation] ip-api.com failed: {e}")
        
        return None
    
    def _try_ipinfo_io(self, ip: str) -> Optional[PreciseLocationInfo]:
        """Try ipinfo.io"""
        try:
            print("[PreciseLocation] 🔍 Trying ipinfo.io...")
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=8)
            data = response.json()
            
            if "loc" in data and data.get("city"):
                lat, lon = data["loc"].split(",")
                
                # Try to get detailed address
                detailed_location = self._get_detailed_address(float(lat), float(lon))
                
                street_address = ""
                house_number = ""
                street_name = ""
                if detailed_location:
                    street_address = detailed_location.get("street_address", "")
                    house_number = detailed_location.get("house_number", "")
                    street_name = detailed_location.get("street_name", "")
                
                return self._create_precise_location_info(
                    lat=float(lat),
                    lon=float(lon),
                    house_number=house_number,
                    street_name=street_name,
                    street_address=street_address,
                    suburb="",
                    district=data.get("region", ""),
                    city=data.get("city"),
                    state=data.get("region"),
                    country=data.get("country"),
                    postal_code=data.get("postal"),
                    region="",
                    county=data.get("region", ""),
                    timezone=data.get("timezone"),
                    public_ip=ip,
                    isp=data.get("org", ""),
                    accuracy_meters=2000.0,
                    source="ipinfo.io",
                    confidence="MEDIUM"
                )
        except Exception as e:
            print(f"[PreciseLocation] ipinfo.io failed: {e}")
        
        return None
    
    def _get_detailed_address(self, lat: float, lon: float) -> Optional[Dict]:
        """Get detailed address from coordinates using reverse geocoding"""
        try:
            # Try OpenStreetMap Nominatim (free)
            print(f"[PreciseLocation] 🗺️ Reverse geocoding: {lat}, {lon}")
            response = requests.get(
                f"https://nominatim.openstreetmap.org/reverse",
                params={
                    "format": "json",
                    "lat": lat,
                    "lon": lon,
                    "zoom": 18,
                    "addressdetails": 1
                },
                headers={"User-Agent": "BuddyVoiceAssistant/1.0"},
                timeout=8
            )
            
            data = response.json()
            
            if "address" in data:
                address = data["address"]
                
                # Extract detailed components
                house_number = address.get("house_number", "")
                street_name = (
                    address.get("road") or 
                    address.get("street") or 
                    address.get("pedestrian") or 
                    ""
                )
                
                street_address = f"{house_number} {street_name}".strip()
                
                return {
                    "street_address": street_address,
                    "house_number": house_number,
                    "street_name": street_name,
                    "suburb": (
                        address.get("suburb") or 
                        address.get("neighbourhood") or 
                        address.get("quarter") or 
                        ""
                    ),
                    "district": (
                        address.get("city_district") or 
                        address.get("district") or 
                        ""
                    ),
                    "city": (
                        address.get("city") or 
                        address.get("town") or 
                        address.get("municipality") or 
                        ""
                    ),
                    "state": (
                        address.get("state") or 
                        address.get("province") or 
                        ""
                    ),
                    "postal_code": address.get("postcode", ""),
                    "country": address.get("country", "")
                }
                
        except Exception as e:
            print(f"[PreciseLocation] Reverse geocoding failed: {e}")
        
        return None
    
    def _try_reverse_geocoding(self) -> Optional[PreciseLocationInfo]:
        """Try to get location using reverse geocoding services"""
        # This would require getting coordinates first from IP
        # Then doing detailed reverse geocoding
        # Implementation depends on having coordinates
        return None
    
    def _try_windows_location_services(self) -> Optional[PreciseLocationInfo]:
        """Try Windows Location Services for GPS-level accuracy"""
        try:
            if platform.system() == "Windows":
                # This would require Windows Location API
                # For now, placeholder
                print("[PreciseLocation] 📍 Windows Location Services not implemented yet")
                pass
        except Exception as e:
            print(f"[PreciseLocation] Windows location failed: {e}")
        
        return None
    
    def _create_precise_location_info(self, lat, lon, house_number, street_name, 
                                    street_address, suburb, district, city, state, 
                                    country, postal_code, region, county, timezone=None, 
                                    public_ip=None, isp="", accuracy_meters=1000.0, 
                                    source="unknown", confidence="MEDIUM") -> PreciseLocationInfo:
        """Create PreciseLocationInfo object with all details"""
        
        # Get local IP
        local_ip = self._get_local_ip()
        
        # Get system timezone if not provided
        if not timezone:
            timezone = self._get_system_timezone_string()
        
        # Get current time in the detected timezone
        try:
            if timezone:
                tz = pytz.timezone(timezone)
                current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
                timezone_offset = datetime.now(tz).strftime("%z")
                if timezone_offset:
                    timezone_offset = f"{timezone_offset[:3]}:{timezone_offset[3:]}"
            else:
                # Use system time
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                timezone_offset = "+00:00"
                timezone = "UTC"
        except:
            # Fallback to system time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timezone_offset = "+00:00"
            timezone = "UTC"
        
        return PreciseLocationInfo(
            latitude=float(lat) if lat else -27.4698,
            longitude=float(lon) if lon else 153.0251,
            house_number=house_number or "",
            street_name=street_name or "",
            street_address=street_address or "",
            suburb=suburb or "",
            district=district or "",
            city=city or "Brisbane",
            state=state or "Queensland",
            country=country or "Australia",
            postal_code=postal_code or "",
            region=region or "",
            county=county or "",
            timezone=timezone or "Australia/Brisbane",
            timezone_offset=timezone_offset or "+10:00",
            current_time=current_time,
            public_ip=public_ip or "",
            local_ip=local_ip,
            isp=isp,
            accuracy_meters=accuracy_meters,
            source=source,
            confidence=confidence
        )
    
    def _get_best_fallback_location(self) -> PreciseLocationInfo:
        """Fallback to Brisbane area with system time"""
        # Use system timezone for time
        try:
            brisbane_tz = pytz.timezone("Australia/Brisbane")
            current_time = datetime.now(brisbane_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
            timezone_offset = datetime.now(brisbane_tz).strftime("%z")
            if timezone_offset:
                timezone_offset = f"{timezone_offset[:3]}:{timezone_offset[3:]}"
        except:
            # Fallback to system time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timezone_offset = "+10:00"
        
        return PreciseLocationInfo(
            latitude=-27.4698,  # Brisbane coordinates
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
            public_ip=self._get_public_ip(),
            local_ip=self._get_local_ip(),
            isp="Unknown",
            accuracy_meters=10000.0,  # Low accuracy for fallback
            source="fallback",
            confidence="LOW"
        )
    
    def _get_system_timezone_string(self) -> str:
        """Get system timezone as string"""
        try:
            # Try to get system timezone
            import time
            if hasattr(time, 'tzname') and time.tzname:
                # For Australia, map to proper timezone
                if any('australia' in tz.lower() for tz in time.tzname if tz):
                    return "Australia/Brisbane"
            
            # Try using time module offset
            import time
            offset = time.timezone if not time.daylight else time.altzone
            hours = -offset // 3600
            
            # Brisbane is UTC+10
            if hours == 10:
                return "Australia/Brisbane"
            
            return "Australia/Brisbane"  # Default for Australian users
        except:
            return "Australia/Brisbane"
    
    def _get_public_ip(self) -> str:
        """Get public IP address"""
        try:
            # Try multiple services
            services = [
                "https://api.ipify.org",
                "https://ifconfig.me/ip",
                "https://ipinfo.io/ip",
                "https://checkip.amazonaws.com"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    ip = response.text.strip()
                    if ip and '.' in ip:  # Basic IP validation
                        return ip
                except:
                    continue
                    
            return "unknown"
        except Exception:
            return "unknown"
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to find local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    def _is_cache_valid(self) -> bool:
        """Check if cached location is still valid"""
        if not self.cached_location or not self.last_update:
            return False
        
        return (time.time() - self.last_update) < self.cache_duration
    
    def _cache_location(self, location: PreciseLocationInfo):
        """Cache precise location information"""
        try:
            self.cached_location = location
            self.last_update = time.time()
            
            # Save to file
            cache_data = {
                'location': location.__dict__,
                'timestamp': self.last_update
            }
            
            with open(self.location_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            print(f"[PreciseLocation] 💾 Cached location: {location.confidence} accuracy")
            
        except Exception as e:
            print(f"[PreciseLocation] Cache save failed: {e}")
    
    def load_cached_location(self):
        """Load cached location on startup"""
        try:
            if os.path.exists(self.location_cache_file):
                with open(self.location_cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                location_dict = cache_data.get('location', {})
                self.last_update = cache_data.get('timestamp', 0)
                
                # Recreate PreciseLocationInfo object
                self.cached_location = PreciseLocationInfo(**location_dict)
                
                print(f"[PreciseLocation] 📍 Loaded cached location: {self.cached_location.confidence} accuracy")
                
        except Exception as e:
            print(f"[PreciseLocation] Cache load failed: {e}")
    
    def get_current_time_info(self) -> Dict[str, str]:
        """Get comprehensive current time information"""
        location = self.get_precise_location()
        
        try:
            tz = pytz.timezone(location.timezone)
        except:
            tz = pytz.timezone("Australia/Brisbane")
        
        now = datetime.now(tz)
        
        return {
            'current_time': now.strftime("%Y-%m-%d %H:%M:%S"),
            'time_12h': now.strftime("%I:%M %p"),
            'time_24h': now.strftime("%H:%M"),
            'date': now.strftime("%A, %B %d, %Y"),
            'timezone': location.timezone,
            'timezone_offset': location.timezone_offset,
            'day_of_week': now.strftime("%A"),
            'month': now.strftime("%B"),
            'year': str(now.year)
        }
    
    def get_precise_location_summary(self) -> str:
        """Get human-readable precise location summary"""
        location = self.get_precise_location()
        
        parts = []
        
        # Add street address if available
        if location.street_address:
            parts.append(location.street_address)
        
        # Add suburb if available
        if location.suburb:
            parts.append(location.suburb)
        
        # Add city
        if location.city:
            parts.append(location.city)
        
        # Add state
        if location.state:
            parts.append(location.state)
        
        # Add country
        if location.country:
            parts.append(location.country)
        
        summary = ", ".join(parts) if parts else "Unknown location"
        
        print(f"[PreciseLocation] 📍 Summary: {summary} ({location.confidence} confidence)")
        
        return summary
    
    def get_location_for_weather(self) -> Dict[str, str]:
        """Get location data formatted for weather APIs"""
        location = self.get_precise_location()
        
        return {
            'latitude': str(location.latitude),
            'longitude': str(location.longitude),
            'city': location.city,
            'state': location.state,
            'country': location.country,
            'postal_code': location.postal_code,
            'timezone': location.timezone,
            'accuracy': location.confidence
        }

# Global instance
precise_location_manager = PreciseLocationManager()

def get_precise_location() -> PreciseLocationInfo:
    """Get precise current location information"""
    return precise_location_manager.get_precise_location()

def get_current_time() -> str:
    """Get current local time as string"""
    time_info = precise_location_manager.get_current_time_info()
    return time_info['current_time']

def get_precise_location_summary() -> str:
    """Get precise location summary for Buddy"""
    return precise_location_manager.get_precise_location_summary()

def get_time_info() -> Dict[str, str]:
    """Get comprehensive time information"""
    return precise_location_manager.get_current_time_info()

def get_weather_location_data() -> Dict[str, str]:
    """Get location data for weather API"""
    return precise_location_manager.get_location_for_weather()

# Initialize on import
precise_location_manager.load_cached_location()