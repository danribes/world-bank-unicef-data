// Main JavaScript for World Bank + UNICEF Data Visualization

// Chart color palette
const colors = {
    primary: '#1a73e8',
    secondary: '#34a853',
    accent: '#ea4335',
    unicefBlue: '#1cabe2',
    worldBankBlue: '#002244',
    warning: '#fbbc04',
    purple: '#9334e6'
};

// Chart defaults
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#5f6368';

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initMortalityChart();
    initNutritionChart();
    initPovertyChart();
    loadDataFromJSON();
});

// Load data from JSON file (will be populated by data export script)
async function loadDataFromJSON() {
    try {
        const response = await fetch('data/summary.json');
        if (response.ok) {
            const data = await response.json();
            updateChartsWithData(data);
        }
    } catch (error) {
        console.log('Using placeholder data. Run export script to generate real data.');
    }
}

// Update charts with actual data
function updateChartsWithData(data) {
    if (data.mortality) {
        updateMortalityChart(data.mortality);
    }
    if (data.nutrition) {
        updateNutritionChart(data.nutrition);
    }
    if (data.poverty) {
        updatePovertyChart(data.poverty);
    }
}

// Mortality Chart
let mortalityChart;

function initMortalityChart() {
    const ctx = document.getElementById('mortalityChart');
    if (!ctx) return;

    // Placeholder data - will be replaced with actual data
    const placeholderData = {
        labels: ['1990', '1995', '2000', '2005', '2010', '2015', '2020'],
        datasets: [
            {
                label: 'Under-5 Mortality Rate',
                data: [93, 87, 77, 63, 52, 43, 37],
                borderColor: colors.accent,
                backgroundColor: colors.accent + '20',
                fill: true,
                tension: 0.4
            },
            {
                label: 'Infant Mortality Rate',
                data: [64, 60, 54, 46, 39, 32, 28],
                borderColor: colors.primary,
                backgroundColor: colors.primary + '20',
                fill: true,
                tension: 0.4
            },
            {
                label: 'Neonatal Mortality Rate',
                data: [36, 34, 31, 27, 23, 19, 17],
                borderColor: colors.secondary,
                backgroundColor: colors.secondary + '20',
                fill: true,
                tension: 0.4
            }
        ]
    };

    mortalityChart = new Chart(ctx, {
        type: 'line',
        data: placeholderData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Global Child Mortality Rates Over Time (per 1,000 live births)',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Deaths per 1,000 live births'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                }
            }
        }
    });
}

function updateMortalityChart(data) {
    if (mortalityChart && data) {
        mortalityChart.data.labels = data.labels;
        mortalityChart.data.datasets = data.datasets;
        mortalityChart.update();
    }
}

// Nutrition Chart
let nutritionChart;

function initNutritionChart() {
    const ctx = document.getElementById('nutritionChart');
    if (!ctx) return;

    // Placeholder data showing regional nutrition indicators
    const placeholderData = {
        labels: ['Sub-Saharan Africa', 'South Asia', 'East Asia', 'Latin America', 'Middle East', 'Europe'],
        datasets: [
            {
                label: 'Stunting (%)',
                data: [33, 31, 8, 11, 15, 5],
                backgroundColor: colors.accent + 'cc'
            },
            {
                label: 'Wasting (%)',
                data: [6, 14, 2, 1, 7, 1],
                backgroundColor: colors.warning + 'cc'
            },
            {
                label: 'Underweight (%)',
                data: [18, 27, 4, 4, 9, 2],
                backgroundColor: colors.purple + 'cc'
            }
        ]
    };

    nutritionChart = new Chart(ctx, {
        type: 'bar',
        data: placeholderData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Child Malnutrition by Region (Latest Available Data)',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Prevalence (%)'
                    }
                }
            }
        }
    });
}

function updateNutritionChart(data) {
    if (nutritionChart && data) {
        nutritionChart.data.labels = data.labels;
        nutritionChart.data.datasets = data.datasets;
        nutritionChart.update();
    }
}

// Poverty Chart
let povertyChart;

function initPovertyChart() {
    const ctx = document.getElementById('povertyChart');
    if (!ctx) return;

    // Placeholder scatter plot showing GDP vs child mortality
    const placeholderData = {
        datasets: [{
            label: 'GDP per Capita vs Under-5 Mortality',
            data: [
                { x: 500, y: 120 },
                { x: 1000, y: 90 },
                { x: 2000, y: 60 },
                { x: 5000, y: 35 },
                { x: 10000, y: 20 },
                { x: 20000, y: 10 },
                { x: 40000, y: 5 },
                { x: 60000, y: 4 }
            ],
            backgroundColor: colors.unicefBlue + '80',
            borderColor: colors.unicefBlue,
            pointRadius: 8
        }]
    };

    povertyChart = new Chart(ctx, {
        type: 'scatter',
        data: placeholderData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'GDP per Capita vs Under-5 Mortality Rate',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    type: 'logarithmic',
                    title: {
                        display: true,
                        text: 'GDP per Capita (USD, log scale)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Under-5 Mortality Rate (per 1,000)'
                    }
                }
            }
        }
    });
}

function updatePovertyChart(data) {
    if (povertyChart && data) {
        povertyChart.data.datasets = data.datasets;
        povertyChart.update();
    }
}

// Utility function to format numbers
function formatNumber(num) {
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1) + 'B';
    }
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
