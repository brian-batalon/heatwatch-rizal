/* HeatWatch Rizal - Chart Utilities */

// Default chart colors
const CHART_COLORS = {
    low: '#388e3c',
    moderate: '#fbc02d',
    high: '#f57c00',
    extreme: '#d32f2f',
    unknown: '#9e9e9e',
    temperature: '#ff5722',
    humidity: '#2196f3',
    heatIndex: '#e91e63'
};

// Create risk distribution pie chart
function createRiskPieChart(ctx, data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 15,
                    font: {
                        size: 12
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Low', 'Moderate', 'High', 'Extreme'],
            datasets: [{
                data: [
                    data.LOW || 0,
                    data.MODERATE || 0,
                    data.HIGH || 0,
                    data.EXTREME || 0
                ],
                backgroundColor: [
                    CHART_COLORS.low,
                    CHART_COLORS.moderate,
                    CHART_COLORS.high,
                    CHART_COLORS.extreme
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: chartOptions
    });
}

// Create temperature bar chart
function createTemperatureBarChart(ctx, labels, temperatures, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `Temperature: ${context.parsed.y}°C`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                min: 20,
                title: {
                    display: true,
                    text: 'Temperature (°C)'
                },
                grid: {
                    color: '#e0e0e0'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperature (°C)',
                data: temperatures,
                backgroundColor: function(context) {
                    const value = context.raw;
                    if (value >= 35) return CHART_COLORS.extreme;
                    if (value >= 30) return CHART_COLORS.high;
                    if (value >= 25) return CHART_COLORS.moderate;
                    return CHART_COLORS.low;
                },
                borderRadius: 5,
                barPercentage: 0.7
            }]
        },
        options: chartOptions
    });
}

// Create humidity line chart
function createHumidityLineChart(ctx, labels, humidity, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `Humidity: ${context.parsed.y}%`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                title: {
                    display: true,
                    text: 'Humidity (%)'
                },
                grid: {
                    color: '#e0e0e0'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        elements: {
            line: {
                tension: 0.3,
                borderWidth: 3
            },
            point: {
                radius: 4,
                hoverRadius: 6
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Humidity (%)',
                data: humidity,
                borderColor: CHART_COLORS.humidity,
                backgroundColor: 'rgba(33, 150, 243, 0.1)',
                fill: true
            }]
        },
        options: chartOptions
    });
}

// Create heat index gauge chart
function createHeatIndexGauge(ctx, heatIndex, riskLevel, options = {}) {
    const riskColors = {
        'LOW': CHART_COLORS.low,
        'MODERATE': CHART_COLORS.moderate,
        'HIGH': CHART_COLORS.high,
        'EXTREME': CHART_COLORS.extreme,
        'UNKNOWN': CHART_COLORS.unknown
    };
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                enabled: false
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    const maxValue = 50;
    const value = Math.min(heatIndex || 25, maxValue);
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Heat Index', 'Remaining'],
            datasets: [{
                data: [value, maxValue - value],
                backgroundColor: [
                    riskColors[riskLevel] || CHART_COLORS.unknown,
                    '#e0e0e0'
                ],
                borderWidth: 0,
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            ...chartOptions,
            cutout: '75%',
        }
    });
}

// Create time series chart for temperature and humidity
function createTimeSeriesChart(ctx, timestamps, temperatures, humidity, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 15
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        let value = context.parsed.y;
                        let unit = context.dataset.label.includes('Temperature') ? '°C' : '%';
                        return `${label}: ${value}${unit}`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                grid: {
                    color: '#e0e0e0'
                }
            },
            y1: {
                position: 'right',
                beginAtZero: true,
                max: 100,
                grid: {
                    drawOnChartArea: false
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        elements: {
            line: {
                tension: 0.3
            },
            point: {
                radius: 2,
                hoverRadius: 5
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temperatures,
                    borderColor: CHART_COLORS.temperature,
                    backgroundColor: 'transparent',
                    yAxisID: 'y',
                    borderWidth: 2
                },
                {
                    label: 'Humidity (%)',
                    data: humidity,
                    borderColor: CHART_COLORS.humidity,
                    backgroundColor: 'transparent',
                    yAxisID: 'y1',
                    borderWidth: 2,
                    borderDash: [5, 5]
                }
            ]
        },
        options: chartOptions
    });
}

// Create stacked bar chart for risk levels by location
function createRiskStackedBarChart(ctx, locations, riskData, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 15,
                    usePointStyle: true
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        },
        scales: {
            x: {
                stacked: true,
                grid: {
                    display: false
                }
            },
            y: {
                stacked: true,
                title: {
                    display: true,
                    text: 'Number of Readings'
                },
                grid: {
                    color: '#e0e0e0'
                }
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: locations,
            datasets: [
                {
                    label: 'Low',
                    data: riskData.map(d => d.LOW || 0),
                    backgroundColor: CHART_COLORS.low
                },
                {
                    label: 'Moderate',
                    data: riskData.map(d => d.MODERATE || 0),
                    backgroundColor: CHART_COLORS.moderate
                },
                {
                    label: 'High',
                    data: riskData.map(d => d.HIGH || 0),
                    backgroundColor: CHART_COLORS.high
                },
                {
                    label: 'Extreme',
                    data: riskData.map(d => d.EXTREME || 0),
                    backgroundColor: CHART_COLORS.extreme
                }
            ]
        },
        options: chartOptions
    });
}

// Create scatter plot for temperature vs humidity
function createTempHumidityScatterChart(ctx, data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 15
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const point = context.raw;
                        return `Temp: ${point.x}°C, Humidity: ${point.y}%`;
                    }
                }
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Temperature (°C)'
                },
                grid: {
                    color: '#e0e0e0'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Humidity (%)'
                },
                max: 100,
                grid: {
                    color: '#e0e0e0'
                }
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'scatter',
        data: data,
        options: chartOptions
    });
}

// Update chart data dynamically
function updateChartData(chart, newLabels, newData) {
    if (chart && chart.data) {
        chart.data.labels = newLabels;
        chart.data.datasets.forEach((dataset, index) => {
            if (newData[index] !== undefined) {
                dataset.data = newData[index];
            }
        });
        chart.update();
    }
}

// Destroy chart if it exists
function destroyChart(chart) {
    if (chart && typeof chart.destroy === 'function') {
        chart.destroy();
    }
}

// Create chart container with loading state
function showChartLoading(ctx, message = 'Loading data...') {
    const { width, height } = ctx.canvas;
    
    ctx.save();
    ctx.font = '14px Arial';
    ctx.fillStyle = '#999';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(message, width / 2, height / 2);
    ctx.restore();
}

// Format chart label for timestamps
function formatTimeLabels(timestamps, format = 'time') {
    return timestamps.map(ts => {
        const date = new Date(ts);
        if (format === 'time') {
            return date.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });
        } else if (format === 'datetime') {
            return date.toLocaleString('en-PH', { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit'
            });
        }
        return date.toLocaleString('en-PH');
    });
}