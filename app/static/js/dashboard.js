/* HeatWatch Rizal - Dashboard JavaScript */

// Dashboard specific functions
document.addEventListener('DOMContentLoaded', function() {
    console.log('HeatWatch Rizal Dashboard loaded');
});

// Refresh dashboard data
function refreshDashboard() {
    if (typeof loadDashboardData === 'function') {
        loadDashboardData();
    }
}

// Format number with unit
function formatTemperature(temp) {
    return temp ? `${temp.toFixed(1)}°C` : 'N/A';
}

function formatHumidity(humidity) {
    return humidity ? `${humidity.toFixed(0)}%` : 'N/A';
}

// Get risk badge HTML
function getRiskBadge(riskLevel, riskColor) {
    return `<span class="badge" style="background-color: ${riskColor};">${riskLevel}</span>`;
}

// Show error message
function showError(message) {
    console.error(message);
    // Could add toast notification here
}

// Show success message
function showSuccess(message) {
    console.log(message);
    // Could add toast notification here
}