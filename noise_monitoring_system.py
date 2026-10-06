"""
IoT-Based Urban Noise Pollution Monitoring System
Main Module: Real-Time Environmental Noise Data Collection and Analysis

This module implements a comprehensive noise monitoring system that simulates
real-time environmental sound level monitoring across urban locations.

Author: Internship Project Team
Date: 2024
"""

import json
import random
import datetime
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NoiseLevel(Enum):
    """Noise level classification"""
    QUIET = "Quiet"
    NORMAL = "Normal"
    ELEVATED = "Elevated"
    LOUD = "Loud"
    VERY_LOUD = "Very Loud"
    EXTREME = "Extreme"


class LocationType(Enum):
    """Types of urban locations"""
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    INDUSTRIAL = "Industrial"
    SCHOOL = "School"
    HOSPITAL = "Hospital"
    PARK = "Park"
    HIGHWAY = "Highway"
    AIRPORT = "Airport"


@dataclass
class GPSCoordinate:
    """GPS coordinate data"""
    latitude: float
    longitude: float
    altitude: float = 0.0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'latitude': round(self.latitude, 6),
            'longitude': round(self.longitude, 6),
            'altitude': round(self.altitude, 2)
        }


@dataclass
class NoiseReading:
    """Data class representing a noise reading"""
    reading_id: str
    timestamp: datetime.datetime
    location_id: str
    location_type: LocationType
    location_name: str
    gps_coordinate: GPSCoordinate
    sound_level_db: float  # Decibels
    frequency_range: str  # Hz range
    noise_source: str  # e.g., 'Traffic', 'Construction', 'People'
    noise_level: NoiseLevel
    sensor_status: str
    battery_level: float
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'reading_id': self.reading_id,
            'timestamp': self.timestamp.isoformat(),
            'location_id': self.location_id,
            'location_type': self.location_type.value,
            'location_name': self.location_name,
            'gps_coordinate': self.gps_coordinate.to_dict(),
            'sound_level_db': round(self.sound_level_db, 2),
            'frequency_range': self.frequency_range,
            'noise_source': self.noise_source,
            'noise_level': self.noise_level.value,
            'sensor_status': self.sensor_status,
            'battery_level': round(self.battery_level, 2)
        }


@dataclass
class NoiseAlert:
    """Data class representing a noise pollution alert"""
    alert_id: str
    location_id: str
    location_name: str
    alert_type: str  # 'THRESHOLD_EXCEEDED', 'SUSTAINED_HIGH_NOISE', 'ANOMALY_DETECTED'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    sound_level_db: float
    threshold_db: float
    message: str
    timestamp: datetime.datetime
    duration_minutes: int = 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'location_id': self.location_id,
            'location_name': self.location_name,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'sound_level_db': round(self.sound_level_db, 2),
            'threshold_db': round(self.threshold_db, 2),
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'duration_minutes': self.duration_minutes
        }


class NoiseSensor:
    """Class representing a noise monitoring sensor"""
    
    def __init__(self, sensor_id: str, location_id: str, location_type: LocationType, 
                 location_name: str, gps_coordinate: GPSCoordinate):
        """
        Initialize a noise sensor
        
        Args:
            sensor_id: Unique sensor identifier
            location_id: Location identifier
            location_type: Type of location
            location_name: Human-readable location name
            gps_coordinate: GPS coordinates of sensor location
        """
        self.sensor_id = sensor_id
        self.location_id = location_id
        self.location_type = location_type
        self.location_name = location_name
        self.gps_coordinate = gps_coordinate
        self.readings: List[NoiseReading] = []
        self.battery_level = 100.0
        self.is_functional = True
        self.reading_count = 0
        
        # Set location-specific baseline and thresholds
        self._set_location_parameters()
    
    def _set_location_parameters(self):
        """Set baseline noise and thresholds based on location type"""
        if self.location_type == LocationType.RESIDENTIAL:
            self.baseline_db = 50
            self.warning_threshold = 65
            self.alert_threshold = 75
            self.critical_threshold = 85
        elif self.location_type == LocationType.COMMERCIAL:
            self.baseline_db = 65
            self.warning_threshold = 75
            self.alert_threshold = 85
            self.critical_threshold = 95
        elif self.location_type == LocationType.INDUSTRIAL:
            self.baseline_db = 75
            self.warning_threshold = 85
            self.alert_threshold = 95
            self.critical_threshold = 105
        elif self.location_type == LocationType.SCHOOL:
            self.baseline_db = 55
            self.warning_threshold = 70
            self.alert_threshold = 80
            self.critical_threshold = 90
        elif self.location_type == LocationType.HOSPITAL:
            self.baseline_db = 45
            self.warning_threshold = 60
            self.alert_threshold = 70
            self.critical_threshold = 80
        elif self.location_type == LocationType.PARK:
            self.baseline_db = 40
            self.warning_threshold = 55
            self.alert_threshold = 65
            self.critical_threshold = 75
        elif self.location_type == LocationType.HIGHWAY:
            self.baseline_db = 80
            self.warning_threshold = 90
            self.alert_threshold = 100
            self.critical_threshold = 110
        else:  # AIRPORT
            self.baseline_db = 85
            self.warning_threshold = 95
            self.alert_threshold = 105
            self.critical_threshold = 115
    
    def take_reading(self, time_of_day: int = 12, activity_factor: float = 0.5) -> NoiseReading:
        """
        Take a noise reading
        
        Args:
            time_of_day: Hour of day (0-23)
            activity_factor: Factor representing activity level (0.0 = quiet, 1.0 = peak activity)
            
        Returns:
            NoiseReading object
        """
        timestamp = datetime.datetime.now()
        reading_id = f"NOISE_{self.location_id}_{self.reading_count + 1}"
        
        # Generate noise level based on time and activity
        base_noise = self.baseline_db
        
        # Time-based variation (higher during day, lower at night)
        if 6 <= time_of_day <= 22:  # Day hours
            time_factor = 1.0 + (activity_factor * 0.3)
        else:  # Night hours
            time_factor = 0.8 + (activity_factor * 0.2)
        
        # Generate sound level
        sound_level = base_noise * time_factor + random.uniform(-5, 10)
        
        # Add occasional spikes (traffic, construction, etc.)
        if random.random() < 0.15:  # 15% chance of spike
            sound_level += random.uniform(5, 20)
        
        # Ensure realistic bounds
        sound_level = max(30, min(130, sound_level))
        
        # Determine noise level classification
        if sound_level < self.baseline_db - 10:
            noise_level = NoiseLevel.QUIET
        elif sound_level < self.baseline_db:
            noise_level = NoiseLevel.NORMAL
        elif sound_level < self.warning_threshold:
            noise_level = NoiseLevel.ELEVATED
        elif sound_level < self.alert_threshold:
            noise_level = NoiseLevel.LOUD
        elif sound_level < self.critical_threshold:
            noise_level = NoiseLevel.VERY_LOUD
        else:
            noise_level = NoiseLevel.EXTREME
        
        # Determine noise source
        if sound_level > self.baseline_db + 15:
            noise_source = random.choice(['Traffic', 'Construction', 'People', 'Machinery'])
        else:
            noise_source = 'Background'
        
        # Create reading
        reading = NoiseReading(
            reading_id=reading_id,
            timestamp=timestamp,
            location_id=self.location_id,
            location_type=self.location_type,
            location_name=self.location_name,
            gps_coordinate=self.gps_coordinate,
            sound_level_db=sound_level,
            frequency_range="20-20000 Hz",
            noise_source=noise_source,
            noise_level=noise_level,
            sensor_status="Operational",
            battery_level=self.battery_level
        )
        
        self.readings.append(reading)
        self.reading_count += 1
        
        # Update battery
        self.battery_level -= random.uniform(0.05, 0.15)
        if self.battery_level < 10:
            reading.sensor_status = "Low Battery"
        
        return reading
    
    def get_sensor_status(self) -> Dict:
        """Get current sensor status"""
        return {
            'sensor_id': self.sensor_id,
            'location_id': self.location_id,
            'location_type': self.location_type.value,
            'location_name': self.location_name,
            'is_functional': self.is_functional,
            'battery_level': round(self.battery_level, 2),
            'total_readings': self.reading_count,
            'last_reading': self.readings[-1].to_dict() if self.readings else None
        }


class NoiseMonitoringZone:
    """Class representing a monitored urban zone"""
    
    def __init__(self, zone_id: str, zone_name: str):
        """
        Initialize a monitoring zone
        
        Args:
            zone_id: Zone identifier
            zone_name: Zone name
        """
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.sensors: Dict[str, NoiseSensor] = {}
        self.alerts: List[NoiseAlert] = []
        self.high_noise_events: List[Dict] = []
        
        self._initialize_sensors()
    
    def _initialize_sensors(self):
        """Initialize sensors for the zone"""
        location_configs = [
            ('RES_001', LocationType.RESIDENTIAL, 'Downtown Residential', GPSCoordinate(40.7128, -74.0060, 10)),
            ('COM_001', LocationType.COMMERCIAL, 'Business District', GPSCoordinate(40.7150, -74.0070, 15)),
            ('IND_001', LocationType.INDUSTRIAL, 'Industrial Area', GPSCoordinate(40.7100, -74.0050, 5)),
            ('SCH_001', LocationType.SCHOOL, 'Central School', GPSCoordinate(40.7160, -74.0080, 8)),
            ('HOS_001', LocationType.HOSPITAL, 'City Hospital', GPSCoordinate(40.7140, -74.0040, 12)),
            ('PAR_001', LocationType.PARK, 'Central Park', GPSCoordinate(40.7829, -73.9654, 20)),
            ('HWY_001', LocationType.HIGHWAY, 'Main Highway', GPSCoordinate(40.7200, -74.0100, 3)),
            ('APT_001', LocationType.AIRPORT, 'City Airport', GPSCoordinate(40.6895, -74.1745, 50))
        ]
        
        for location_id, location_type, location_name, gps in location_configs:
            sensor_id = f"SENSOR_{location_id}"
            sensor = NoiseSensor(sensor_id, location_id, location_type, location_name, gps)
            self.sensors[sensor_id] = sensor
    
    def monitor_zone(self, hour: int = 12):
        """
        Monitor the zone by reading all sensors
        
        Args:
            hour: Current hour of day (0-23)
        """
        activity_factor = 0.5
        
        # Adjust activity based on time of day
        if 7 <= hour <= 9:  # Morning rush
            activity_factor = 0.9
        elif 12 <= hour <= 13:  # Lunch time
            activity_factor = 0.7
        elif 17 <= hour <= 19:  # Evening rush
            activity_factor = 0.95
        elif 22 <= hour or hour <= 6:  # Night time
            activity_factor = 0.2
        
        for sensor_id, sensor in self.sensors.items():
            reading = sensor.take_reading(hour, activity_factor)
            
            # Check for alerts
            if reading.sound_level_db > sensor.critical_threshold:
                self._generate_alert(sensor, reading, 'CRITICAL')
            elif reading.sound_level_db > sensor.alert_threshold:
                self._generate_alert(sensor, reading, 'HIGH')
            elif reading.sound_level_db > sensor.warning_threshold:
                self._generate_alert(sensor, reading, 'MEDIUM')
    
    def _generate_alert(self, sensor: NoiseSensor, reading: NoiseReading, severity: str):
        """Generate a noise pollution alert"""
        alert_id = f"ALERT_{len(self.alerts) + 1}"
        
        # Map severity to threshold
        if severity == 'CRITICAL':
            threshold = sensor.critical_threshold
            alert_type = 'THRESHOLD_EXCEEDED'
        elif severity == 'HIGH':
            threshold = sensor.alert_threshold
            alert_type = 'SUSTAINED_HIGH_NOISE'
        else:
            threshold = sensor.warning_threshold
            alert_type = 'ANOMALY_DETECTED'
        
        alert = NoiseAlert(
            alert_id=alert_id,
            location_id=sensor.location_id,
            location_name=sensor.location_name,
            alert_type=alert_type,
            severity=severity,
            sound_level_db=reading.sound_level_db,
            threshold_db=threshold,
            message=f"Noise level {reading.sound_level_db:.1f} dB exceeds threshold at {sensor.location_name}",
            timestamp=reading.timestamp
        )
        
        self.alerts.append(alert)
        logger.warning(f"Noise Alert: {alert.message}")
    
    def get_zone_status(self) -> Dict:
        """Get current zone status"""
        return {
            'zone_id': self.zone_id,
            'zone_name': self.zone_name,
            'total_sensors': len(self.sensors),
            'total_readings': sum(s.reading_count for s in self.sensors.values()),
            'total_alerts': len(self.alerts),
            'critical_alerts': len([a for a in self.alerts if a.severity == 'CRITICAL']),
            'high_alerts': len([a for a in self.alerts if a.severity == 'HIGH']),
            'avg_noise_level': self._calculate_average_noise()
        }
    
    def _calculate_average_noise(self) -> float:
        """Calculate average noise level across all sensors"""
        all_readings = []
        for sensor in self.sensors.values():
            all_readings.extend([r.sound_level_db for r in sensor.readings])
        
        return sum(all_readings) / len(all_readings) if all_readings else 0.0


class UrbanNoiseMonitoringSystem:
    """Central urban noise monitoring system"""
    
    def __init__(self):
        """Initialize the noise monitoring system"""
        self.zones: Dict[str, NoiseMonitoringZone] = {}
        self.all_readings: List[NoiseReading] = []
        self.all_alerts: List[NoiseAlert] = []
        self.operation_log: List[Dict] = []
        
        self._initialize_zones()
        logger.info("Urban Noise Monitoring System initialized")
    
    def _initialize_zones(self):
        """Initialize monitoring zones"""
        zone_configs = [
            ('ZONE_01', 'Downtown Area'),
            ('ZONE_02', 'Suburban Area'),
            ('ZONE_03', 'Industrial District')
        ]
        
        for zone_id, zone_name in zone_configs:
            zone = NoiseMonitoringZone(zone_id, zone_name)
            self.zones[zone_id] = zone
    
    def simulate_24_hour_cycle(self):
        """Simulate a 24-hour noise monitoring cycle"""
        logger.info("Starting 24-hour noise monitoring simulation")
        
        for hour in range(24):
            for zone_id, zone in self.zones.items():
                zone.monitor_zone(hour)
                
                # Collect readings and alerts
                for sensor in zone.sensors.values():
                    if sensor.readings:
                        self.all_readings.append(sensor.readings[-1])
                
                for alert in zone.alerts:
                    if alert not in self.all_alerts:
                        self.all_alerts.append(alert)
            
            # Log hourly status
            self.operation_log.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'hour': hour,
                'total_readings': len(self.all_readings),
                'total_alerts': len(self.all_alerts),
                'avg_noise_level': self._calculate_system_average()
            })
            
            logger.info(f"Hour {hour:02d}:00 - Readings: {len(self.all_readings)}, "
                       f"Alerts: {len(self.all_alerts)}")
        
        logger.info("24-hour simulation completed")
    
    def _calculate_system_average(self) -> float:
        """Calculate system-wide average noise level"""
        if not self.all_readings:
            return 0.0
        return sum(r.sound_level_db for r in self.all_readings) / len(self.all_readings)
    
    def get_system_statistics(self) -> Dict:
        """Get system-wide statistics"""
        total_zones = len(self.zones)
        total_sensors = sum(len(z.sensors) for z in self.zones.values())
        
        # Count alert types
        alert_distribution = {}
        for alert in self.all_alerts:
            alert_distribution[alert.alert_type] = alert_distribution.get(alert.alert_type, 0) + 1
        
        # Noise level distribution
        noise_levels = {}
        for reading in self.all_readings:
            level = reading.noise_level.value
            noise_levels[level] = noise_levels.get(level, 0) + 1
        
        return {
            'total_zones': total_zones,
            'total_sensors': total_sensors,
            'total_readings': len(self.all_readings),
            'total_alerts': len(self.all_alerts),
            'critical_alerts': len([a for a in self.all_alerts if a.severity == 'CRITICAL']),
            'high_alerts': len([a for a in self.all_alerts if a.severity == 'HIGH']),
            'avg_noise_level': round(self._calculate_system_average(), 2),
            'alert_distribution': alert_distribution,
            'noise_level_distribution': noise_levels
        }
    
    def export_to_json(self, filename: str):
        """Export system data to JSON"""
        data = {
            'system_name': 'Urban Noise Pollution Monitoring System',
            'total_zones': len(self.zones),
            'zones': {zone_id: zone.get_zone_status() for zone_id, zone in self.zones.items()},
            'statistics': self.get_system_statistics(),
            'alerts': [alert.to_dict() for alert in self.all_alerts[-50:]],
            'operation_log': self.operation_log
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data exported to {filename}")


if __name__ == "__main__":
    # Create noise monitoring system
    system = UrbanNoiseMonitoringSystem()
    
    # Run simulation
    system.simulate_24_hour_cycle()
    
    # Get statistics
    stats = system.get_system_statistics()
    
    # Print report
    print("\n" + "="*60)
    print("URBAN NOISE MONITORING SYSTEM - SIMULATION REPORT")
    print("="*60)
    print(json.dumps(stats, indent=2))
    
    # Export data
    system.export_to_json('/home/ubuntu/noise_monitoring_system_data.json')
