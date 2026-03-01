/**
 * HR Module - Custom JavaScript
 * Handles interactive elements for HR module
 */

(function() {
    'use strict';

    // ============================================
    // DOM Ready
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        initTooltips();
        initDropdowns();
        initMobileMenu();
        initTableResponsive();
        initDatepickers();
        initFormValidation();
        initDeleteModals();
        initCharts();
        initSearchDebounce();
        initSelectAllCheckbox();
        initImportProgress();
    });

    // ============================================
    // Tooltips
    // ============================================
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        if (tooltipElements.length === 0) return;
        
        tooltipElements.forEach(el => {
            el.addEventListener('mouseenter', function(e) {
                const tooltip = this.getAttribute('data-tooltip');
                if (!tooltip) return;
                
                // Create tooltip element
                const tooltipEl = document.createElement('div');
                tooltipEl.className = 'hr-tooltip';
                tooltipEl.textContent = tooltip;
                tooltipEl.style.cssText = `
                    position: absolute;
                    background: #1f2937;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    z-index: 9999;
                    pointer-events: none;
                    white-space: nowrap;
                `;
                
                document.body.appendChild(tooltipEl);
                
                // Position tooltip
                const rect = this.getBoundingClientRect();
                tooltipEl.style.top = rect.top - tooltipEl.offsetHeight - 5 + window.scrollY + 'px';
                tooltipEl.style.left = rect.left + (rect.width / 2) - (tooltipEl.offsetWidth / 2) + 'px';
                
                this.addEventListener('mouseleave', function() {
                    tooltipEl.remove();
                }, { once: true });
            });
        });
    }

    // ============================================
    // Custom Dropdowns
    // ============================================
    function initDropdowns() {
        // Export dropdown
        const exportBtn = document.getElementById('exportDropdownButton');
        const exportDropdown = document.getElementById('exportDropdown');
        
        if (exportBtn && exportDropdown) {
            exportBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                exportDropdown.classList.toggle('hidden');
            });
            
            document.addEventListener('click', function() {
                exportDropdown.classList.add('hidden');
            });
            
            exportDropdown.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
        
        // Filter dropdowns
        const filterToggles = document.querySelectorAll('[data-filter-toggle]');
        filterToggles.forEach(toggle => {
            const targetId = toggle.getAttribute('data-filter-toggle');
            const target = document.getElementById(targetId);
            
            if (target) {
                toggle.addEventListener('click', function(e) {
                    e.stopPropagation();
                    target.classList.toggle('hidden');
                });
            }
        });
    }

    // ============================================
    // Mobile Menu
    // ============================================
    function initMobileMenu() {
        const menuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (menuButton && mobileMenu) {
            menuButton.addEventListener('click', function() {
                mobileMenu.classList.toggle('hidden');
                
                // Animate menu icon
                const icon = this.querySelector('i');
                if (icon) {
                    icon.classList.toggle('fa-bars');
                    icon.classList.toggle('fa-xmark');
                }
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!menuButton.contains(e.target) && !mobileMenu.contains(e.target)) {
                    mobileMenu.classList.add('hidden');
                    const icon = menuButton.querySelector('i');
                    if (icon) {
                        icon.classList.add('fa-bars');
                        icon.classList.remove('fa-xmark');
                    }
                }
            });
        }
    }

    // ============================================
    // Responsive Tables
    // ============================================
    function initTableResponsive() {
        const tables = document.querySelectorAll('.table-responsive');
        
        tables.forEach(table => {
            const headers = [];
            const headerRow = table.querySelector('thead tr');
            
            if (headerRow) {
                headerRow.querySelectorAll('th').forEach(th => {
                    headers.push(th.textContent.trim());
                });
                
                // Add data-label attributes to cells
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    row.querySelectorAll('td').forEach((td, index) => {
                        if (headers[index]) {
                            td.setAttribute('data-label', headers[index]);
                        }
                    });
                });
            }
        });
    }

    // ============================================
    // Datepickers (fallback for browser native)
    // ============================================
    function initDatepickers() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        
        dateInputs.forEach(input => {
            // Add placeholder for browsers that don't support date input
            if (input.type !== 'date') {
                input.placeholder = 'YYYY-MM-DD';
            }
            
            // Add min/max validation
            input.addEventListener('change', function() {
                validateDateRange(this);
            });
        });
    }
    
    function validateDateRange(input) {
        const min = input.getAttribute('min');
        const max = input.getAttribute('max');
        const value = input.value;
        
        if (min && value < min) {
            input.setCustomValidity(`Date must be after ${min}`);
        } else if (max && value > max) {
            input.setCustomValidity(`Date must be before ${max}`);
        } else {
            input.setCustomValidity('');
        }
    }

    // ============================================
    // Form Validation
    // ============================================
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Scroll to first error
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        firstInvalid.focus();
                    }
                }
                
                form.classList.add('was-validated');
            });
        });
        
        // Real-time validation
        const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    }
    
    function validateField(field) {
        if (field.checkValidity()) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            
            // Remove error message if exists
            const errorDiv = field.parentNode.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
        } else {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            
            // Add or update error message
            let errorDiv = field.parentNode.querySelector('.invalid-feedback');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                field.parentNode.appendChild(errorDiv);
            }
            errorDiv.textContent = field.validationMessage;
        }
    }

    // ============================================
    // Delete Modals
    // ============================================
    function initDeleteModals() {
        window.confirmDelete = function(nik, nama) {
            const modal = document.getElementById('deleteModal');
            const nameSpan = document.getElementById('deleteEmployeeName');
            const confirmBtn = document.getElementById('deleteConfirmBtn');
            
            if (modal && nameSpan && confirmBtn) {
                nameSpan.textContent = nama;
                confirmBtn.href = `/hr/employees/${nik}/delete/`;
                modal.style.display = 'flex';
                
                // Focus on cancel button for accessibility
                setTimeout(() => {
                    modal.querySelector('button:first-child')?.focus();
                }, 100);
            }
        };
        
        window.closeDeleteModal = function() {
            const modal = document.getElementById('deleteModal');
            if (modal) {
                modal.style.display = 'none';
            }
        };
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeDeleteModal();
            }
        });
        
        // Close modal when clicking outside
        const deleteModal = document.getElementById('deleteModal');
        if (deleteModal) {
            deleteModal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeDeleteModal();
                }
            });
        }
    }

    // ============================================
    // Charts (if Chart.js is available)
    // ============================================
    function initCharts() {
        if (typeof Chart === 'undefined') return;
        
        // Department Chart
        const deptCtx = document.getElementById('deptChart')?.getContext('2d');
        if (deptCtx && window.deptChartData) {
            new Chart(deptCtx, {
                type: 'doughnut',
                data: window.deptChartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: document.documentElement.classList.contains('dark') ? '#fff' : '#374151'
                            }
                        }
                    }
                }
            });
        }
        
        // Status Chart
        const statusCtx = document.getElementById('statusChart')?.getContext('2d');
        if (statusCtx && window.statusChartData) {
            new Chart(statusCtx, {
                type: 'bar',
                data: window.statusChartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: document.documentElement.classList.contains('dark') ? '#374151' : '#e5e7eb'
                            },
                            ticks: {
                                color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280'
                            }
                        }
                    }
                }
            });
        }
    }

    // ============================================
    // Search Debounce (for AJAX search)
    // ============================================
    function initSearchDebounce() {
        const searchInput = document.querySelector('input[name="search"]');
        
        if (searchInput && searchInput.hasAttribute('data-ajax-search')) {
            let debounceTimer;
            
            searchInput.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                
                const query = this.value;
                debounceTimer = setTimeout(() => {
                    performSearch(query);
                }, 500);
            });
        }
    }
    
    function performSearch(query) {
        // This will be implemented when adding HTMX
        console.log('Searching for:', query);
    }

    // ============================================
    // Select All Checkbox
    // ============================================
    function initSelectAllCheckbox() {
        const selectAllCheckbox = document.getElementById('selectAll');
        const itemCheckboxes = document.querySelectorAll('.select-item');
        
        if (selectAllCheckbox && itemCheckboxes.length) {
            selectAllCheckbox.addEventListener('change', function() {
                itemCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
            });
            
            itemCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const allChecked = Array.from(itemCheckboxes).every(cb => cb.checked);
                    selectAllCheckbox.checked = allChecked;
                    selectAllCheckbox.indeterminate = !allChecked && Array.from(itemCheckboxes).some(cb => cb.checked);
                });
            });
        }
    }

    // ============================================
    // Import Progress
    // ============================================
    function initImportProgress() {
        const importForm = document.getElementById('importForm');
        
        if (importForm) {
            importForm.addEventListener('submit', function(e) {
                // Check if we're not already showing progress
                if (document.getElementById('importLoadingModal')?.style.display === 'flex') {
                    return;
                }
                
                e.preventDefault();
                
                const modal = document.getElementById('importLoadingModal');
                const progressBar = document.getElementById('importProgress');
                const statusText = document.getElementById('importStatus');
                
                if (modal && progressBar && statusText) {
                    modal.style.display = 'flex';
                    
                    let progress = 0;
                    const interval = setInterval(function() {
                        progress += 5;
                        progressBar.style.width = progress + '%';
                        
                        if (progress < 30) {
                            statusText.textContent = 'Reading dataset...';
                        } else if (progress < 60) {
                            statusText.textContent = 'Processing records...';
                        } else if (progress < 90) {
                            statusText.textContent = 'Saving to database...';
                        } else {
                            statusText.textContent = 'Finalizing import...';
                        }
                        
                        if (progress >= 100) {
                            clearInterval(interval);
                            statusText.textContent = 'Import complete! Redirecting...';
                            setTimeout(() => {
                                importForm.submit();
                            }, 500);
                        }
                    }, 200);
                }
            });
        }
    }

    // ============================================
    // Toast Notifications
    // ============================================
    window.showToast = function(message, type = 'info', duration = 5000) {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} animate-slide-in`;
        toast.style.cssText = `
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 300px;
            max-width: 400px;
        `;
        
        // Add icon
        const icon = document.createElement('i');
        icon.className = `fa-solid ${
            type === 'success' ? 'fa-circle-check' : 
            type === 'error' ? 'fa-circle-exclamation' : 
            type === 'warning' ? 'fa-triangle-exclamation' : 
            'fa-circle-info'
        }`;
        toast.appendChild(icon);
        
        // Add message
        const text = document.createElement('span');
        text.style.flex = '1';
        text.textContent = message;
        toast.appendChild(text);
        
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            opacity: 0.7;
            padding: 0 5px;
        `;
        closeBtn.onclick = () => toast.remove();
        toast.appendChild(closeBtn);
        
        toastContainer.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    };
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        `;
        document.body.appendChild(container);
        return container;
    }

    // ============================================
    // Keyboard Shortcuts
    // ============================================
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // ? for help
        if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            showKeyboardShortcuts();
        }
    });
    
    function showKeyboardShortcuts() {
        const shortcuts = [
            { key: 'Ctrl/Cmd + K', description: 'Focus search' },
            { key: '?', description: 'Show keyboard shortcuts' },
            { key: 'Esc', description: 'Close modal' },
            { key: 'Ctrl/Cmd + N', description: 'New employee' },
            { key: 'Ctrl/Cmd + I', description: 'Go to import' }
        ];
        
        let message = 'Keyboard Shortcuts:\n\n';
        shortcuts.forEach(s => {
            message += `${s.key.padEnd(15)} - ${s.description}\n`;
        });
        
        alert(message);
    }
})();