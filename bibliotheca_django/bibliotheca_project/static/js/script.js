// Custom JavaScript for Bibliothèque

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Search form enhancements
    var searchForm = document.querySelector('form[method="get"]');
    if (searchForm) {
        var searchInput = searchForm.querySelector('input[name="query"]');
        if (searchInput) {
            // Add search suggestions (future enhancement)
            searchInput.addEventListener('input', debounce(function(e) {
                // Implementation for search suggestions
                console.log('Search query:', e.target.value);
            }, 300));
        }
    }

    // Book card hover effects
    var bookCards = document.querySelectorAll('.book-card');
    bookCards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Form validation enhancements
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner"></span> Chargement...';
                
                // Re-enable after 3 seconds if form hasn't submitted
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Soumettre';
                }, 3000);
            }
        });
    });

    // Smooth scroll for anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Dynamic table sorting (future enhancement)
    var sortableTables = document.querySelectorAll('.table-sortable');
    sortableTables.forEach(function(table) {
        var headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.addEventListener('click', function() {
                sortTable(table, this.getAttribute('data-sort'));
            });
        });
    });

    // Copy to clipboard functionality
    var copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(function() {
                showToast('Copié dans le presse-papiers!', 'success');
            }).catch(function() {
                showToast('Erreur lors de la copie', 'error');
            });
        });
    });

    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm-delete') || 'Êtes-vous sûr de vouloir supprimer cet élément?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Loading states for AJAX requests
    setupAjaxLoading();
});

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showToast(message, type = 'info') {
    var toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1050';
        document.body.appendChild(toastContainer);
    }

    var toastId = 'toast-' + Date.now();
    var toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    var toastElement = document.getElementById(toastId);
    var toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

function sortTable(table, column) {
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var isAscending = table.getAttribute('data-sort-direction') !== 'asc';
    
    rows.sort(function(a, b) {
        var aValue = a.children[column].textContent.trim();
        var bValue = b.children[column].textContent.trim();
        
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return isAscending ? aValue - bValue : bValue - aValue;
        }
        
        return isAscending ? 
            aValue.localeCompare(bValue) : 
            bValue.localeCompare(aValue);
    });
    
    tbody.innerHTML = '';
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    table.setAttribute('data-sort-direction', isAscending ? 'asc' : 'desc');
}

function setupAjaxLoading() {
    // Show loading indicator for AJAX requests
    var originalFetch = window.fetch;
    window.fetch = function() {
        showLoading();
        return originalFetch.apply(this, arguments).finally(function() {
            hideLoading();
        });
    };

    var originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        this.addEventListener('loadstart', showLoading);
        this.addEventListener('loadend', hideLoading);
        return originalXHROpen.apply(this, arguments);
    };
}

function showLoading() {
    var loadingIndicator = document.getElementById('loading-indicator');
    if (!loadingIndicator) {
        loadingIndicator = document.createElement('div');
        loadingIndicator.id = 'loading-indicator';
        loadingIndicator.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        loadingIndicator.style.backgroundColor = 'rgba(0,0,0,0.5)';
        loadingIndicator.style.zIndex = '9999';
        loadingIndicator.innerHTML = `
            <div class="spinner-border text-light" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
        `;
        document.body.appendChild(loadingIndicator);
    }
    loadingIndicator.style.display = 'flex';
}

function hideLoading() {
    var loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

// Form validation helpers
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return false;
    
    var isValid = true;
    var inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Date formatting helpers
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Currency formatting
function formatCurrency(amount, currency = 'EUR') {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Export functions for global use
window.Bibliotheque = {
    showToast: showToast,
    validateForm: validateForm,
    formatDate: formatDate,
    formatDateTime: formatDateTime,
    formatCurrency: formatCurrency
};
