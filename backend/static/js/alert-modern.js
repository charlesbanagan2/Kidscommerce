// Modern Alert System
console.log('Loading modern alert system...');

class ModernAlert {
    constructor() {
        this.container = null;
        this.init();
        console.log('ModernAlert initialized');
    }

    init() {
        // Create alert container if it doesn't exist
        if (!document.getElementById('alert-container')) {
            this.container = document.createElement('div');
            this.container.id = 'alert-container';
            this.container.style.cssText = `
                position: fixed;
                top: 0;
                right: 0;
                z-index: 9999;
                pointer-events: none;
            `;
            document.body.appendChild(this.container);
            console.log('Alert container created');
        } else {
            this.container = document.getElementById('alert-container');
            console.log('Alert container found');
        }
    }

    show(message, type = 'info', title = null, duration = 5000) {
        console.log('Showing alert:', { message, type, title, duration });
        const alertId = 'alert-' + Date.now();
        
        // Determine icon based on type
        const icons = {
            success: '✓',
            error: '✕',
            warning: '!',
            info: 'i'
        };

        // Determine title based on type if not provided
        const titles = {
            success: title || 'Success',
            error: title || 'Error',
            warning: title || 'Warning',
            info: title || 'Information'
        };

        const alertHTML = `
            <div id="${alertId}" class="alert-modern ${type}">
                <div class="alert-icon">
                    <span style="font-weight: bold; font-size: 14px;">${icons[type]}</span>
                </div>
                <div class="alert-content">
                    <div class="alert-title">${titles[type]}</div>
                    <div class="alert-message">${message}</div>
                </div>
                <button class="alert-close" onclick="modernAlert.close('${alertId}')">
                    <span style="font-size: 12px;">✕</span>
                </button>
            </div>
        `;

        // Add to container
        this.container.insertAdjacentHTML('beforeend', alertHTML);
        
        // Make container interactive
        this.container.style.pointerEvents = 'auto';

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.close(alertId);
            }, duration);
        }

        return alertId;
    }

    close(alertId) {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.classList.add('removing');
            setTimeout(() => {
                alert.remove();
                // Remove container if no alerts left
                if (this.container.children.length === 0) {
                    this.container.style.pointerEvents = 'none';
                }
            }, 300);
        }
    }

    // Convenience methods
    success(message, title = null, duration = 5000) {
        return this.show(message, 'success', title, duration);
    }

    error(message, title = null, duration = 7000) {
        return this.show(message, 'error', title, duration);
    }

    warning(message, title = null, duration = 6000) {
        return this.show(message, 'warning', title, duration);
    }

    info(message, title = null, duration = 5000) {
        return this.show(message, 'info', title, duration);
    }
}

// Global instance
const modernAlert = new ModernAlert();
console.log('ModernAlert global instance created');

// Helper functions for backward compatibility
function showModernAlert(message, type = 'info', title = null, duration = 5000) {
    console.log('showModernAlert called');
    return modernAlert.show(message, type, title, duration);
}

function showSuccessAlert(message, title = null, duration = 5000) {
    console.log('showSuccessAlert called');
    return modernAlert.success(message, title, duration);
}

function showErrorAlert(message, title = null, duration = 7000) {
    return modernAlert.error(message, title, duration);
}

function showWarningAlert(message, title = null, duration = 6000) {
    return modernAlert.warning(message, title, duration);
}

function showInfoAlert(message, title = null, duration = 5000) {
    return modernAlert.info(message, title, duration);
}
