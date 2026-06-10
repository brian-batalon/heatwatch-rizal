/* HeatWatch Rizal - Map Utilities */

// Initialize map with default Rizal view
function initializeHeatWatchMap(elementId, options = {}) {
    const defaultOptions = {
        center: [14.5764, 121.0851], // Antipolo, Rizal
        zoom: 11,
        minZoom: 8,
        maxZoom: 18
    };
    
    const mapOptions = { ...defaultOptions, ...options };
    
    const map = L.map(elementId).setView(mapOptions.center, mapOptions.zoom);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: mapOptions.maxZoom
    }).addTo(map);
    
    // Add scale control
    L.control.scale({
        metric: true,
        imperial: false,
        position: 'bottomleft'
    }).addTo(map);
    
    return map;
}

// Create custom marker based on risk level
function createRiskMarker(lat, lon, riskLevel, riskColor, locationName, temperature, humidity, heatIndex) {
    const markerIcon = L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: ${riskColor}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"></div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15],
        popupAnchor: [0, -15]
    });
    
    const marker = L.marker([lat, lon], { icon: markerIcon });
    
    const popupContent = `
        <div style="min-width: 220px;">
            <h6 style="margin-bottom: 10px; font-weight: bold;">${locationName}</h6>
            <table style="width: 100%; font-size: 14px;">
                <tr><td>Temperature:</td><td><strong>${temperature}°C</strong></td></tr>
                <tr><td>Humidity:</td><td><strong>${humidity}%</strong></td></tr>
                <tr><td>Heat Index:</td><td><strong>${heatIndex}°C</strong></td></tr>
                <tr><td>Risk Level:</td><td><span style="background-color: ${riskColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">${riskLevel}</span></td></tr>
            </table>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    
    return marker;
}

// Create circle marker for heatmap-style visualization
function createHeatCircle(lat, lon, riskLevel, riskColor, radius = 500) {
    const opacityMap = {
        'LOW': 0.3,
        'MODERATE': 0.4,
        'HIGH': 0.5,
        'EXTREME': 0.6,
        'UNKNOWN': 0.2
    };
    
    const circle = L.circle([lat, lon], {
        color: riskColor,
        fillColor: riskColor,
        fillOpacity: opacityMap[riskLevel] || 0.3,
        radius: radius,
        weight: 1
    });
    
    return circle;
}

// Add legend to map
function addMapLegend(map, position = 'bottomright') {
    const legend = L.control({ position: position });
    
    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-legend bg-white p-3 rounded shadow');
        div.innerHTML = `
            <h6 style="margin-bottom: 10px; font-weight: bold;">Heat Risk Legend</h6>
            <div style="margin-bottom: 5px;">
                <span style="display: inline-block; width: 16px; height: 16px; background-color: #388e3c; border-radius: 50%; margin-right: 8px;"></span>
                <span>Low Risk</span>
            </div>
            <div style="margin-bottom: 5px;">
                <span style="display: inline-block; width: 16px; height: 16px; background-color: #fbc02d; border-radius: 50%; margin-right: 8px;"></span>
                <span>Moderate Risk</span>
            </div>
            <div style="margin-bottom: 5px;">
                <span style="display: inline-block; width: 16px; height: 16px; background-color: #f57c00; border-radius: 50%; margin-right: 8px;"></span>
                <span>High Risk</span>
            </div>
            <div>
                <span style="display: inline-block; width: 16px; height: 16px; background-color: #d32f2f; border-radius: 50%; margin-right: 8px;"></span>
                <span>Extreme Risk</span>
            </div>
            <hr style="margin: 10px 0;">
            <small style="color: #666;">
                <i class="bi bi-info-circle"></i> Click markers for details
            </small>
        `;
        return div;
    };
    
    legend.addTo(map);
    return legend;
}

// Fit map bounds to show all markers
function fitMapToMarkers(map, markers) {
    if (markers.length === 0) return;
    
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds(), { 
        padding: [50, 50],
        maxZoom: 13
    });
}

// Add location search control
function addLocationSearch(map) {
    const searchControl = L.control({ position: 'topleft' });
    
    searchControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'leaflet-control bg-white p-2 rounded shadow');
        div.innerHTML = `
            <select id="location-search" class="form-select form-select-sm" style="width: 200px;">
                <option value="">📍 Jump to location...</option>
            </select>
        `;
        
        // Prevent map click propagation
        L.DomEvent.disableClickPropagation(div);
        
        return div;
    };
    
    searchControl.addTo(map);
    return searchControl;
}

// Update location search dropdown
function updateLocationSearch(map, locations) {
    const select = document.getElementById('location-search');
    if (!select) return;
    
    // Clear existing options except first
    while (select.options.length > 1) {
        select.remove(1);
    }
    
    // Add location options
    locations.sort((a, b) => a.name.localeCompare(b.name));
    locations.forEach(loc => {
        const option = document.createElement('option');
        option.value = `${loc.lat},${loc.lon}`;
        option.textContent = loc.name;
        select.appendChild(option);
    });
    
    // Add change event
    select.addEventListener('change', function(e) {
        const value = e.target.value;
        if (value) {
            const [lat, lon] = value.split(',').map(Number);
            map.setView([lat, lon], 14);
        }
    });
}

// Create heat gradient based on temperature
function getTemperatureColor(temp) {
    if (!temp) return '#9e9e9e';
    
    const colors = [
        { temp: 20, color: '#0066cc' },
        { temp: 25, color: '#00cc44' },
        { temp: 30, color: '#ffcc00' },
        { temp: 35, color: '#ff6600' },
        { temp: 40, color: '#cc0000' }
    ];
    
    let color = colors[0].color;
    for (let i = 0; i < colors.length; i++) {
        if (temp >= colors[i].temp) {
            color = colors[i].color;
        }
    }
    
    return color;
}

// Get risk level description
function getRiskDescription(riskLevel) {
    const descriptions = {
        'LOW': 'Low risk - Normal conditions. No special precautions needed.',
        'MODERATE': 'Moderate risk - Stay hydrated. Take breaks if working outdoors.',
        'HIGH': 'High risk - Limit outdoor activities. Drink plenty of water.',
        'EXTREME': 'Extreme danger - Avoid outdoor activities. Seek air-conditioned spaces.',
        'UNKNOWN': 'Data unavailable - Unable to determine risk level.'
    };
    
    return descriptions[riskLevel] || 'Unknown risk level';
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-PH', {
        timeZone: 'Asia/Manila',
        hour12: true,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Calculate distance between two points in kilometers
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Group locations by area (Rizal municipalities)
function groupLocationsByArea(locations) {
    const areas = {
        'Antipolo': [],
        'Taytay': [],
        'Cainta': [],
        'Angono': [],
        'Binangonan': [],
        'Tanay': [],
        'Other': []
    };
    
    locations.forEach(loc => {
        let grouped = false;
        for (const area in areas) {
            if (loc.name.includes(area)) {
                areas[area].push(loc);
                grouped = true;
                break;
            }
        }
        if (!grouped) {
            areas['Other'].push(loc);
        }
    });
    
    return areas;
}