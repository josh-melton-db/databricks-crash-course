// FedEx Air Operations Dashboard - Vanilla JS (no Babel needed)

class AirOpsApp {
  constructor() {
    this.aircraftData = [];
    this.fleetStats = null;
    this.selectedAircraft = null;
    this.leafletMap = null;
    this.markers = {};
    this.charts = {};
    this.mapReady = false;
    
    this.init();
  }
  
  init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.start());
    } else {
      this.start();
    }
  }
  
  start() {
    this.initMap();
    this.fetchData();
    setInterval(() => this.fetchData(), 5000); // Update every 5 seconds
  }
  
  initMap() {
    // Wait for Leaflet to be loaded
    if (typeof L === 'undefined') {
      setTimeout(() => this.initMap(), 100);
      return;
    }
    
    const mapElement = document.getElementById('map');
    if (!mapElement) {
      console.error('Map element not found');
      return;
    }
    
    try {
      this.leafletMap = L.map('map').setView([30, 0], 2);
      
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
      }).addTo(this.leafletMap);
      
      this.mapReady = true;
      console.log('Map initialized successfully');
      
      // Update loading indicator
      const loadingText = document.getElementById('map-loading');
      if (loadingText) loadingText.style.display = 'none';
    } catch (error) {
      console.error('Error initializing map:', error);
    }
  }
  
  async fetchData() {
    try {
      const [aircraftRes, statsRes] = await Promise.all([
        fetch('/api/aircraft'),
        fetch('/api/fleet/stats')
      ]);
      
      this.aircraftData = await aircraftRes.json();
      this.fleetStats = await statsRes.json();
      
      this.render();
      
      if (this.mapReady) {
        this.updateMap(this.aircraftData);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }
  
  render() {
    this.renderStats();
    this.renderAircraftList();
  }
  
  renderStats() {
    if (!this.fleetStats) return;
    
    const statsHTML = `
      <div class="stat-card">
        <div class="stat-label">Aircraft in Flight</div>
        <div class="stat-value">${this.fleetStats.inFlight}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Cargo</div>
        <div class="stat-value">${this.fleetStats.totalCargo}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Altitude</div>
        <div class="stat-value">${this.fleetStats.avgAltitude}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Speed</div>
        <div class="stat-value">${this.fleetStats.avgSpeed}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Active Alerts</div>
        <div class="stat-value" style="color: ${this.fleetStats.alerts > 0 ? '#ff6b00' : '#4ade80'}">
          ${this.fleetStats.alerts}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">On-Time Performance</div>
        <div class="stat-value">${this.fleetStats.onTimePerformance}</div>
      </div>
    `;
    
    const statsBar = document.getElementById('stats-bar');
    if (statsBar) statsBar.innerHTML = statsHTML;
  }
  
  renderAircraftList() {
    const listHTML = this.aircraftData.map(aircraft => {
      const isSelected = this.selectedAircraft?.id === aircraft.id;
      return `
        <div class="aircraft-card ${isSelected ? 'selected' : ''}" 
             onclick="app.selectAircraft('${aircraft.id}')">
          <div class="aircraft-id">${aircraft.id}</div>
          <div class="aircraft-route">${aircraft.origin} → ${aircraft.destination}</div>
          <div style="font-size: 13px; color: #666; margin-bottom: 5px;">
            ${aircraft.model} | ${aircraft.cargo}
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${aircraft.progress}%"></div>
          </div>
          <div class="sensor-grid">
            <div class="sensor-item">
              <span class="sensor-label">Alt: </span>
              <span class="sensor-value">${aircraft.sensors.altitude.toLocaleString()} ft</span>
            </div>
            <div class="sensor-item">
              <span class="sensor-label">Speed: </span>
              <span class="sensor-value">${aircraft.sensors.speed} mph</span>
            </div>
            <div class="sensor-item">
              <span class="sensor-label">Fuel: </span>
              <span class="sensor-value">${aircraft.sensors.fuel}%</span>
            </div>
            <div class="sensor-item">
              <span class="sensor-label">Engine: </span>
              <span class="sensor-value">${aircraft.sensors.engineTemp}°F</span>
            </div>
          </div>
          <span class="status-badge status-${aircraft.status.toLowerCase().replace(' ', '')}">
            ${aircraft.status}
          </span>
        </div>
      `;
    }).join('');
    
    const aircraftList = document.getElementById('aircraft-list');
    if (aircraftList) aircraftList.innerHTML = listHTML;
  }
  
  selectAircraft(aircraftId) {
    const aircraft = this.aircraftData.find(a => a.id === aircraftId);
    if (!aircraft) return;
    
    this.selectedAircraft = aircraft;
    this.renderAircraftList();
    
    // Fetch and display historical data
    fetch(`/api/aircraft/${aircraftId}/history`)
      .then(res => res.json())
      .then(data => this.renderCharts(data))
      .catch(err => console.error('Error fetching history:', err));
    
    // Pan map to aircraft
    if (this.leafletMap && aircraft.position) {
      this.leafletMap.setView([aircraft.position.lat, aircraft.position.lng], 5);
      
      // Open popup if marker exists
      if (this.markers[aircraftId]) {
        this.markers[aircraftId].openPopup();
      }
    }
  }
  
  updateMap(aircraft) {
    if (!this.leafletMap || !this.mapReady) {
      console.log('Map not ready for update');
      return;
    }
    
    try {
      // Clear old markers
      Object.values(this.markers).forEach(marker => {
        try {
          marker.remove();
        } catch (e) {
          console.warn('Error removing marker:', e);
        }
      });
      this.markers = {};
      
      // Add aircraft markers and flight paths
      aircraft.forEach(plane => {
        // Draw flight path (sparkly Christmas trail!)
        L.polyline(plane.flightPath, {
          color: '#c41e3a',
          weight: 3,
          opacity: 0.6,
          dashArray: '10, 5'
        }).addTo(this.leafletMap);
        
        // Custom sleigh icon
        const planeIcon = L.divIcon({
          className: 'custom-plane-icon',
          html: `<div style="font-size: 28px; text-shadow: 0 0 10px gold;">🛷</div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        });
        
        // Add aircraft marker
        const marker = L.marker([plane.position.lat, plane.position.lng], {
          icon: planeIcon
        }).addTo(this.leafletMap);
        
        marker.bindPopup(`
          <strong>${plane.id}</strong><br/>
          ${plane.model}<br/>
          ${plane.origin} → ${plane.destination}<br/>
          Altitude: ${plane.sensors.altitude.toLocaleString()} ft<br/>
          Speed: ${plane.sensors.speed} mph<br/>
          Fuel: ${plane.sensors.fuel}%
        `);
        
        this.markers[plane.id] = marker;
      });
      
      console.log(`Updated ${aircraft.length} aircraft on map`);
    } catch (error) {
      console.error('Error updating map:', error);
    }
  }
  
  renderCharts(data) {
    const chartsContainer = document.getElementById('charts-container');
    if (!chartsContainer) return;
    
    // Show charts container
    chartsContainer.style.display = 'grid';
    
    // Destroy old charts
    if (this.charts.altitude) this.charts.altitude.destroy();
    if (this.charts.fuel) this.charts.fuel.destroy();
    
    // Altitude Chart
    const altCtx = document.getElementById('altitudeChart');
    if (altCtx) {
      this.charts.altitude = new Chart(altCtx, {
        type: 'line',
        data: {
          labels: data.map(d => new Date(d.timestamp).toLocaleTimeString()),
          datasets: [{
            label: 'Altitude (ft)',
            data: data.map(d => d.altitude),
            borderColor: '#c41e3a',
            backgroundColor: 'rgba(196, 30, 58, 0.1)',
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: false }
          }
        }
      });
    }
    
    // Fuel Chart
    const fuelCtx = document.getElementById('fuelChart');
    if (fuelCtx) {
      this.charts.fuel = new Chart(fuelCtx, {
        type: 'line',
        data: {
          labels: data.map(d => new Date(d.timestamp).toLocaleTimeString()),
          datasets: [{
            label: 'Christmas Magic (%)',
            data: data.map(d => d.fuel),
            borderColor: '#165b33',
            backgroundColor: 'rgba(22, 91, 51, 0.1)',
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: false }
          }
        }
      });
    }
  }
}

// Initialize app when script loads
let app;
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    app = new AirOpsApp();
  });
} else {
  app = new AirOpsApp();
}


