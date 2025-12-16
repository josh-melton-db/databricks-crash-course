import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import cors from 'cors';

const app = express();
const port = process.env.PORT || 8000;

const __dirname = path.dirname(fileURLToPath(import.meta.url));

app.use(cors());
app.use(express.json());
app.use('/static', express.static(path.join(__dirname, 'static')));

// Mock aircraft fleet data
const aircraftFleet = [
  { id: 'FDX001', model: 'Boeing 777F', origin: 'Memphis', destination: 'Paris', cargo: 'Priority' },
  { id: 'FDX002', model: 'Boeing 767F', origin: 'Indianapolis', destination: 'Tokyo', cargo: 'Standard' },
  { id: 'FDX003', model: 'Airbus A300', origin: 'Oakland', destination: 'Anchorage', cargo: 'Express' },
  { id: 'FDX004', model: 'Boeing 757F', origin: 'Newark', destination: 'London', cargo: 'Priority' },
  { id: 'FDX005', model: 'Boeing 777F', origin: 'Miami', destination: 'São Paulo', cargo: 'Express' },
  { id: 'FDX006', model: 'MD-11F', origin: 'Los Angeles', destination: 'Shanghai', cargo: 'Standard' }
];

// Generate realistic flight paths
function generateFlightPath(start, end, progress) {
  const steps = 20;
  const path = [];
  
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const lat = start.lat + (end.lat - start.lat) * t;
    const lng = start.lng + (end.lng - start.lng) * t;
    path.push([lat, lng]);
  }
  
  return path;
}

// Airport coordinates
const airports = {
  'Memphis': { lat: 35.0424, lng: -89.9767 },
  'Paris': { lat: 49.0097, lng: 2.5479 },
  'Indianapolis': { lat: 39.7173, lng: -86.2944 },
  'Tokyo': { lat: 35.5494, lng: 139.7798 },
  'Oakland': { lat: 37.7213, lng: -122.2208 },
  'Anchorage': { lat: 61.1744, lng: -149.9961 },
  'Newark': { lat: 40.6895, lng: -74.1745 },
  'London': { lat: 51.4700, lng: -0.4543 },
  'Miami': { lat: 25.7959, lng: -80.2870 },
  'São Paulo': { lat: -23.4356, lng: -46.4731 },
  'Los Angeles': { lat: 33.9416, lng: -118.4085 },
  'Shanghai': { lat: 31.1434, lng: 121.8052 }
};

// Serve main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'static/index.html'));
});

// Get all aircraft positions and sensor data
app.get('/api/aircraft', (req, res) => {
  const now = Date.now();
  
  const aircraft = aircraftFleet.map((plane, idx) => {
    const progress = ((now / 60000) % 120 + idx * 20) / 120; // Simulate flight progress
    const origin = airports[plane.origin];
    const dest = airports[plane.destination];
    
    // Calculate current position along the route
    const lat = origin.lat + (dest.lat - origin.lat) * progress;
    const lng = origin.lng + (dest.lng - origin.lng) * progress;
    
    // Generate realistic IoT sensor data
    const altitude = 35000 + Math.sin(progress * Math.PI) * 3000;
    const speed = 450 + Math.random() * 50;
    const fuel = 85 - (progress * 70);
    const engineTemp = 600 + Math.random() * 50;
    const cabinTemp = 21 + Math.random() * 3;
    
    return {
      id: plane.id,
      model: plane.model,
      origin: plane.origin,
      destination: plane.destination,
      cargo: plane.cargo,
      position: { lat, lng },
      flightPath: generateFlightPath(origin, dest, progress),
      progress: Math.round(progress * 100),
      sensors: {
        altitude: Math.round(altitude),
        speed: Math.round(speed),
        fuel: Math.round(fuel),
        engineTemp: Math.round(engineTemp),
        cabinTemp: Math.round(cabinTemp * 10) / 10,
        timestamp: new Date().toISOString()
      },
      status: fuel < 20 ? 'Warning' : progress > 0.95 ? 'Landing' : 'In Flight'
    };
  });
  
  res.json(aircraft);
});

// Get historical sensor data for a specific aircraft
app.get('/api/aircraft/:id/history', (req, res) => {
  const { id } = req.params;
  const now = Date.now();
  
  // Generate 24 hours of historical data (1 point per hour)
  const history = Array.from({ length: 24 }, (_, i) => {
    const timestamp = new Date(now - (23 - i) * 3600000);
    const timeProgress = i / 24;
    
    return {
      timestamp: timestamp.toISOString(),
      altitude: Math.round(35000 + Math.sin(timeProgress * Math.PI * 4) * 5000),
      speed: Math.round(450 + Math.random() * 50),
      fuel: Math.round(95 - timeProgress * 70),
      engineTemp: Math.round(600 + Math.random() * 50),
      cabinTemp: Math.round((21 + Math.random() * 3) * 10) / 10
    };
  });
  
  res.json(history);
});

// Get fleet statistics
app.get('/api/fleet/stats', (req, res) => {
  const stats = {
    totalAircraft: aircraftFleet.length,
    inFlight: aircraftFleet.length,
    totalCargo: '847 tons',
    avgAltitude: '35,400 ft',
    avgSpeed: '475 mph',
    alerts: 1,
    onTimePerformance: '98.2%'
  };
  
  res.json(stats);
});

app.listen(port, () => {
  console.log(`🚀 FedEx Air Operations Dashboard running at http://localhost:${port}`);
  console.log(`📊 API endpoints available at /api/*`);
});


