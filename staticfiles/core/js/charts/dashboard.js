// dashboard.js - Charts untuk dashboard

function initRecruitmentChart(months, counts) {
    const ctx = document.getElementById('recruitmentChart');
    
    if (!ctx) return;
    
    // Destroy chart instance if it exists
    if (window.recruitmentChart instanceof Chart) {
        window.recruitmentChart.destroy();
    }
    
    // Get theme colors
    const isDark = document.documentElement.classList.contains('dark');
    const textColor = isDark ? '#e5e7eb' : '#374151';
    const gridColor = isDark ? '#374151' : '#e5e7eb';
    
    // Create new chart
    window.recruitmentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Jumlah Karyawan Baru',
                data: counts,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: isDark ? '#1f2937' : '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: textColor,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: isDark ? '#1f2937' : '#ffffff',
                    titleColor: isDark ? '#e5e7eb' : '#111827',
                    bodyColor: isDark ? '#d1d5db' : '#4b5563',
                    borderColor: isDark ? '#374151' : '#e5e7eb',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: textColor,
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Re-initialize chart when theme changes
document.addEventListener('themeChanged', function(e) {
    const chartCanvas = document.getElementById('recruitmentChart');
    if (chartCanvas && window.recruitmentChart) {
        // Get data from data attributes
        const months = JSON.parse(chartCanvas.dataset.months || '[]');
        const counts = JSON.parse(chartCanvas.dataset.counts || '[]');
        initRecruitmentChart(months, counts);
    }
});
// dashboard.js - Charts untuk dashboard

function initRecruitmentChart(months, counts) {
    const ctx = document.getElementById('recruitmentChart');
    
    if (!ctx) return;
    
    // Destroy chart instance if it exists
    if (window.recruitmentChart instanceof Chart) {
        window.recruitmentChart.destroy();
    }
    
    // Get theme colors
    const isDark = document.documentElement.classList.contains('dark');
    const textColor = isDark ? '#e5e7eb' : '#374151';
    const gridColor = isDark ? '#374151' : '#e5e7eb';
    
    // Create new chart
    window.recruitmentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Jumlah Karyawan Baru',
                data: counts,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: isDark ? '#1f2937' : '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: textColor,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: isDark ? '#1f2937' : '#ffffff',
                    titleColor: isDark ? '#e5e7eb' : '#111827',
                    bodyColor: isDark ? '#d1d5db' : '#4b5563',
                    borderColor: isDark ? '#374151' : '#e5e7eb',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: textColor,
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Initialize chart when page loads
document.addEventListener('DOMContentLoaded', function() {
    const chartCanvas = document.getElementById('recruitmentChart');
    if (chartCanvas) {
        const months = JSON.parse(chartCanvas.dataset.months || '[]');
        const counts = JSON.parse(chartCanvas.dataset.counts || '[]');
        if (months.length && counts.length) {
            initRecruitmentChart(months, counts);
        }
    }
});

// Re-initialize chart when theme changes
document.addEventListener('themeChanged', function(e) {
    const chartCanvas = document.getElementById('recruitmentChart');
    if (chartCanvas && window.recruitmentChart) {
        const months = JSON.parse(chartCanvas.dataset.months || '[]');
        const counts = JSON.parse(chartCanvas.dataset.counts || '[]');
        initRecruitmentChart(months, counts);
    }
});

// Filter functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterSelect = document.getElementById('dept-filter');
    if (!filterSelect) return;
    
    filterSelect.addEventListener('change', function(e) {
        const selectedDept = e.target.value;
        
        if (selectedDept === 'all') {
            // Reset ke semua department dengan reload
            location.reload();
        } else {
            // Fetch data untuk department tertentu
            fetch(`/dashboard/api/dept-data/?dept=${encodeURIComponent(selectedDept)}`)
                .then(response => response.json())
                .then(data => {
                    updateDepartmentDisplay(data);
                })
                .catch(error => console.error('Error:', error));
        }
    });
});

function updateDepartmentDisplay(data) {
    const container = document.querySelector('.department-breakdown');
    if (!container) return;
    
    if (Array.isArray(data)) {
        // Data multiple departments (top 10)
        let html = '';
        const maxCount = data[0]?.count || 1;
        
        data.forEach(dept => {
            const width = (dept.count / maxCount) * 100;
            html += `
                <div class="mb-4 last:mb-0">
                    <div class="flex justify-between text-sm text-gray-600 dark:text-gray-300 mb-1">
                        <span>${dept.name}</span>
                        <span class="font-medium">${dept.count} karyawan</span>
                    </div>
                    <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                        <div class="bg-blue-600 dark:bg-blue-500 h-2.5 rounded-full" style="width: ${width}%"></div>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    } else {
        // Single department
        container.innerHTML = `
            <div class="mb-4">
                <div class="flex justify-between text-sm text-gray-600 dark:text-gray-300 mb-1">
                    <span>${data.name}</span>
                    <span class="font-medium">${data.count} karyawan</span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                    <div class="bg-blue-600 dark:bg-blue-500 h-2.5 rounded-full" style="width: 100%"></div>
                </div>
            </div>
        `;
    }
}