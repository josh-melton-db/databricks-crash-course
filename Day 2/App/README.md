# Santa's Flight Command Center 🎅🎄

A magical real-time tracking dashboard for Santa's Christmas Eve operations, showcasing sleigh tracking, reindeer sensor data, and Christmas magic analytics. Built for Databricks Apps.

## Features ✨

- **Interactive Sleigh Map**: Real-time sleigh tracking with magical flight paths on OpenStreetMap (using Leaflet)
- **Live Reindeer Sensors**: Monitor altitude, speed, Christmas magic levels, reindeer vitals, and cabin temperature
- **Time-Series Analytics**: Historical sensor data visualization with Chart.js
- **Fleet Statistics**: At-a-glance metrics for all active sleigh teams
- **Festive Design**: Beautiful Christmas-themed UI with red, green, and gold colors plus snowfall animation
- **Auto-Refresh**: Data updates every 5 seconds to track Santa's progress

## Demo Highlights 🎯

This festive demo shows how Databricks can:
- Handle real-time IoT data streams from Santa's sleigh sensors
- Visualize time-series data for Christmas Eve operations
- Track global delivery routes in real-time
- Monitor Christmas magic levels and reindeer vitals
- Provide magical dashboards for North Pole operations teams

## Quick Start (Local Development)

```bash
# Navigate to the app directory
cd "Day 2/App"

# Install dependencies
npm install

# Run the app
npm start
```

Open http://localhost:8000 to view the dashboard.

## Deploy to Databricks Apps 🚀

### Option 1: One-Click Deploy

1. **Create a Databricks App**:
   - Go to your Databricks workspace
   - Navigate to "Apps" in the left sidebar
   - Click "Create App" → "Custom App"
   - Give it a name like "FedEx Air Operations Dashboard"

2. **Upload Files**:
   - Upload all files from this directory (`server.js`, `package.json`, `static/`)
   - Or connect to a Git repository containing these files

3. **Configure & Deploy**:
   - Databricks will automatically detect `package.json`
   - Set start command: `npm start` (should be auto-detected)
   - Environment variable `PORT` is automatically provided by Databricks
   - Click "Deploy"

4. **Access Your App**:
   - Once deployed, you'll get a Databricks-hosted URL
   - Share it with your FedEx team!

### Option 2: Git Integration

```bash
# Push this app to your repository
git add .
git commit -m "Add FedEx Air Ops dashboard"
git push

# In Databricks:
# - Create App → Connect to Git
# - Point to your repository
# - Set path to "Day 2/App"
# - Deploy!
```

## Architecture 🏗️

- **Backend**: Node.js + Express (serves API endpoints and static files)
- **Frontend**: React (with CDN imports for simplicity)
- **Maps**: Leaflet.js with OpenStreetMap tiles
- **Charts**: Chart.js for time-series visualization
- **Styling**: Modern CSS with gradients and animations

## API Endpoints 📡

- `GET /` - Main dashboard interface
- `GET /api/aircraft` - Real-time aircraft positions and sensor data
- `GET /api/aircraft/:id/history` - 24-hour sensor history for specific aircraft
- `GET /api/fleet/stats` - Fleet-wide statistics

## Customization Ideas 💡

Want to make this even better? Try:

1. **Connect to Unity Catalog**: Replace mock data with actual IoT data from Delta tables
2. **Add Alerts**: Integrate with Databricks alerts for low fuel or maintenance needs
3. **ML Predictions**: Use Databricks ML to predict arrival times or maintenance windows
4. **Historical Analysis**: Add date range pickers to analyze past operations
5. **Security**: Add Databricks OAuth authentication

## Tech Stack 🛠️

- Node.js (ES Modules)
- Express.js
- React 18
- Leaflet.js (maps)
- Chart.js (analytics)
- OpenStreetMap (map tiles)

## Notes 📝

- Mock data simulates 6 FedEx aircraft on various routes
- Aircraft positions update dynamically in real-time
- Sensor data follows realistic patterns (altitude arcs, fuel depletion, etc.)
- Flight paths span major FedEx hubs globally
- Production version would connect to actual IoT streams via Databricks

## Next Steps 🎯

1. **Demo this to your team** - Show the live map and sensor tracking
2. **Connect real data** - Integrate with your Unity Catalog IoT tables
3. **Add ML models** - Predict delays, maintenance needs, or fuel optimization
4. **Expand monitoring** - Add weather data, cargo tracking, and more

---

**Built with 🎄 Christmas Spirit and ❤️ | Powered by Databricks Magic ⭐**



