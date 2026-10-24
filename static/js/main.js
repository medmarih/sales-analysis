// JavaScript moderne pour l'application de prédiction des ventes

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des composants Bootstrap
    initializeBootstrapComponents();
    
    // Animations et effets visuels
    initializeAnimations();
    
    // Gestion des formulaires
    initializeFormHandling();
    
    // Gestion des fichiers
    initializeFileHandling();
    
    // Fonctionnalités utilitaires
    initializeUtilities();
    
    // Gestion des rôles utilisateur
    updateUIByRole();
    
    // Initialisation des graphiques
    initializeCharts();
    
    // Effets de particules
    initializeParticles();
});

// Initialisation des composants Bootstrap
function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            animation: true,
            delay: { show: 100, hide: 100 }
        });
    });

    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            animation: true,
            trigger: 'hover'
        });
    });

    // Modals avec animations
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            this.querySelector('.modal-dialog').style.transform = 'scale(0.7)';
            setTimeout(() => {
                this.querySelector('.modal-dialog').style.transform = 'scale(1)';
            }, 50);
        });
    });
}

// Animations et effets visuels
function initializeAnimations() {
    // Animation des messages flash avec effet de slide
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message, index) {
        message.style.opacity = '0';
        message.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            message.style.transition = 'all 0.5s ease';
            message.style.opacity = '1';
            message.style.transform = 'translateY(0)';
        }, index * 100);
        
        // Auto-fermeture avec animation
        setTimeout(function() {
            message.style.transform = 'translateY(-20px)';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Animation des cartes au scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observer les éléments avec animation
    document.querySelectorAll('.card, .workflow-step, .feature-card').forEach(el => {
        observer.observe(el);
    });

    // Effet de parallaxe pour les éléments de fond
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
}

// Gestion des formulaires
function initializeFormHandling() {
    // Validation côté client avec feedback visuel
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Animation d'erreur
                const invalidFields = form.querySelectorAll('.is-invalid');
                invalidFields.forEach(field => {
                    field.style.animation = 'shake 0.5s ease-in-out';
                    setTimeout(() => {
                        field.style.animation = '';
                    }, 500);
                });
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Amélioration des champs de saisie
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        // Effet de focus avec animation
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Validation en temps réel
        input.addEventListener('input', function() {
            validateField(this);
        });
    });
}

// Validation des champs en temps réel
function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    const fieldName = field.name;
    
    // Supprimer les classes d'erreur précédentes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Validation selon le type de champ
    let isValid = true;
    
    if (fieldType === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        isValid = emailRegex.test(value);
    } else if (fieldType === 'password') {
        isValid = value.length >= 6;
    } else if (fieldName === 'username') {
        isValid = value.length >= 3;
    }
    
    // Appliquer les classes de validation
    if (value && isValid) {
        field.classList.add('is-valid');
    } else if (value && !isValid) {
        field.classList.add('is-invalid');
    }
}

// Gestion des fichiers
function initializeFileHandling() {
    const fileInput = document.getElementById('csv_file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Animation de sélection de fichier
                const fileName = file.name;
                const fileSize = (file.size / 1024).toFixed(2);
                
                // Créer un élément de feedback visuel
                const feedback = document.createElement('div');
                feedback.className = 'file-feedback';
                feedback.innerHTML = `
                    <div class="file-info">
                        <i class="fas fa-file-csv text-success"></i>
                        <span class="file-name">${fileName}</span>
                        <span class="file-size">(${fileSize} KB)</span>
                    </div>
                `;
                
                // Remplacer ou ajouter le feedback
                const existingFeedback = document.querySelector('.file-feedback');
                if (existingFeedback) {
                    existingFeedback.remove();
                }
                fileInput.parentElement.appendChild(feedback);
                
                // Animation d'apparition
                feedback.style.opacity = '0';
                feedback.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    feedback.style.transition = 'all 0.3s ease';
                    feedback.style.opacity = '1';
                    feedback.style.transform = 'translateY(0)';
                }, 100);
            }
        });
    }
}

// Fonctionnalités utilitaires
function initializeUtilities() {
    // Fonction d'export CSV améliorée
    window.exportTableToCSV = function(tableId, filename) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const rows = table.querySelectorAll('tr');
        let csv = [];
        
        for (let i = 0; i < rows.length; i++) {
            const row = [], cols = rows[i].querySelectorAll('td, th');
            
            for (let j = 0; j < cols.length; j++) {
                let data = cols[j].innerText.replace(/"/g, '""');
                row.push('"' + data + '"');
            }
            
            csv.push(row.join(','));
        }
        
        // Créer et télécharger le fichier
        const csvFile = new Blob([csv.join('\n')], {type: 'text/csv;charset=utf-8;'});
        const downloadLink = document.createElement('a');
        
        downloadLink.download = filename;
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = 'none';
        
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        
        // Feedback utilisateur
        showNotification('Fichier exporté avec succès !', 'success');
    };

    // Fonction d'impression améliorée
    window.printElement = function(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Impression - Prédiction des Ventes</title>
                    <link rel="stylesheet" href="/static/css/style.css">
                    <style>
                        body { font-family: 'Inter', sans-serif; }
                        .no-print { display: none !important; }
                        @media print {
                            .card { box-shadow: none !important; border: 1px solid #ddd !important; }
                        }
                    </style>
                </head>
                <body>
                    ${element.outerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.focus();
        
        setTimeout(function() {
            printWindow.print();
            printWindow.close();
        }, 500);
    };

    // Système de notifications
    window.showNotification = function(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animation d'entrée
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Auto-fermeture
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    };
}

// Icône pour les notifications
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Gestion des rôles utilisateur
function updateUIByRole() {
    const isAdmin = document.body.dataset.isAdmin === 'true';
    const adminElements = document.querySelectorAll('.admin-only');
    
    adminElements.forEach(function(element) {
        if (isAdmin) {
            element.classList.remove('d-none');
            element.style.animation = 'fadeInUp 0.5s ease-out';
        } else {
            element.classList.add('d-none');
        }
    });
}

// Initialisation des graphiques
function initializeCharts() {
    // Configuration globale pour Plotly
    if (typeof Plotly !== 'undefined') {
        Plotly.setPlotConfig({
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false,
            responsive: true
        });
    }
}

// Effets de particules
function initializeParticles() {
    const particlesContainer = document.getElementById('particles-bg');
    if (!particlesContainer) return;
    
    // Créer des particules animées
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 10 + 's';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        particlesContainer.appendChild(particle);
    }
}

// Gestion du thème sombre/clair
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            // Animation de transition
            document.body.style.transition = 'all 0.3s ease';
        });
    }
    
    // Restaurer le thème sauvegardé
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Gestion du mode plein écran
window.toggleFullscreen = function(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (!document.fullscreenElement) {
        element.requestFullscreen().catch(err => {
            console.log('Erreur lors du passage en plein écran:', err);
        });
    } else {
        document.exitFullscreen();
    }
};

// Gestion du copier-coller
document.addEventListener('copy', function(e) {
    const selection = window.getSelection();
    if (selection.toString().length > 0) {
        // Ajouter des informations de source
        e.clipboardData.setData('text/plain', 
            selection.toString() + '\n\nSource: Application de Prédiction des Ventes'
        );
        e.preventDefault();
    }
});

// Gestion des raccourcis clavier
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S pour sauvegarder
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        // Logique de sauvegarde
        showNotification('Sauvegarde automatique...', 'info');
    }
    
    // Échap pour fermer les modales
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});

// Styles CSS pour les nouvelles fonctionnalités
const additionalStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: var(--border-radius-md);
        box-shadow: var(--shadow-lg);
        padding: 1rem;
        z-index: 9999;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        padding: 0.25rem;
        margin-left: auto;
    }
    
    .notification-success { border-left: 4px solid var(--success-color); }
    .notification-error { border-left: 4px solid var(--danger-color); }
    .notification-warning { border-left: 4px solid var(--warning-color); }
    .notification-info { border-left: 4px solid var(--info-color); }
    
    .file-feedback {
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: rgba(79, 172, 254, 0.1);
        border-radius: var(--border-radius-sm);
        border-left: 3px solid var(--success-color);
    }
    
    .file-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }
    
    .file-size {
        color: #666;
        font-size: 0.8rem;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .focused .form-control {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .dark-theme {
        --bg-primary: #1a202c;
        --bg-secondary: #2d3748;
        --dark-color: #f7fafc;
        --light-color: #2d3748;
    }
`;

// Injecter les styles supplémentaires
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);