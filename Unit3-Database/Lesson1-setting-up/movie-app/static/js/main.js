/**
 * CineMatch - Main JavaScript
 * Unit 3 - Lesson 3.1 Starter
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎬 CineMatch loaded successfully!');
    
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Log to console (helps students debug)
    console.log('✅ Flash message auto-dismiss enabled');
    console.log('✅ Smooth scrolling enabled');
});

/**
 * TODO (Later in Unit 3): Add JavaScript for:
 * - Search functionality
 * - Filter interactions
 * - Dynamic form validation
 * - Loading states
 */
