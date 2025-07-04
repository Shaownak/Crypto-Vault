// Main JavaScript for Crypto App
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initializeAlerts();
    initializePostActions();
    initializeCharacterCounters();
    initializeFormValidation();
    initializeAnimations();
    
    // Auto-hide alerts after 5 seconds
    function initializeAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }, 5000);
        });
    }

    // Like and delete post functionality
    function initializePostActions() {
        // Like buttons
        document.querySelectorAll('.like-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const postId = this.dataset.postId;
                const likesSpan = this.querySelector('.likes-count');
                
                // Add loading state
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="loading"></span> Liking...';
                this.disabled = true;
                
                fetch(`/like/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        likesSpan.textContent = data.likes;
                        showToast('Post liked!', 'success');
                        
                        // Add animation
                        this.style.transform = 'scale(1.2)';
                        setTimeout(() => {
                            this.style.transform = 'scale(1)';
                        }, 150);
                    } else {
                        showToast(data.message || 'Error liking post', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error liking post', 'error');
                })
                .finally(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                });
            });
        });

        // Delete buttons
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                if (!confirm('Are you sure you want to delete this post?')) {
                    return;
                }
                
                const postId = this.dataset.postId;
                const postElement = this.closest('.post');
                
                // Add loading state
                this.innerHTML = '<span class="loading"></span> Deleting...';
                this.disabled = true;
                
                fetch(`/delete_post/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Animate removal
                        postElement.style.transform = 'translateX(-100%)';
                        postElement.style.opacity = '0';
                        setTimeout(() => {
                            postElement.remove();
                        }, 300);
                        showToast('Post deleted successfully!', 'success');
                    } else {
                        showToast(data.message || 'Error deleting post', 'error');
                        this.innerHTML = '🗑️ Delete';
                        this.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error deleting post', 'error');
                    this.innerHTML = '🗑️ Delete';
                    this.disabled = false;
                });
            });
        });
    }

    // Character counters for text inputs
    function initializeCharacterCounters() {
        document.querySelectorAll('textarea[data-max-length]').forEach(textarea => {
            const maxLength = parseInt(textarea.dataset.maxLength);
            
            // Create counter element
            const counter = document.createElement('div');
            counter.className = 'char-counter';
            textarea.parentNode.appendChild(counter);
            
            function updateCounter() {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${remaining} characters remaining`;
                
                // Update styling based on remaining characters
                counter.className = 'char-counter';
                if (remaining < 50) {
                    counter.classList.add('warning');
                }
                if (remaining < 10) {
                    counter.classList.remove('warning');
                    counter.classList.add('danger');
                }
            }
            
            // Initial count
            updateCounter();
            
            // Update on input
            textarea.addEventListener('input', updateCounter);
        });
    }

    // Form validation
    function initializeFormValidation() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const requiredFields = form.querySelectorAll('[required]');
                let isValid = true;
                
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        field.style.borderColor = '#dc3545';
                        isValid = false;
                        
                        // Remove error styling after user starts typing
                        field.addEventListener('input', function() {
                            this.style.borderColor = '';
                        }, { once: true });
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    showToast('Please fill in all required fields', 'error');
                }
            });
        });

        // Password confirmation validation
        const newPassword = document.getElementById('new_password');
        const confirmPassword = document.getElementById('confirm_password');
        
        if (newPassword && confirmPassword) {
            function validatePasswordMatch() {
                if (newPassword.value && confirmPassword.value) {
                    if (newPassword.value !== confirmPassword.value) {
                        confirmPassword.setCustomValidity("Passwords don't match");
                        confirmPassword.style.borderColor = '#dc3545';
                    } else {
                        confirmPassword.setCustomValidity('');
                        confirmPassword.style.borderColor = '#28a745';
                    }
                }
            }
            
            newPassword.addEventListener('input', validatePasswordMatch);
            confirmPassword.addEventListener('input', validatePasswordMatch);
        }
    }

    // Add animations to elements
    function initializeAnimations() {
        // Add fade-in animation to posts
        document.querySelectorAll('.post').forEach((post, index) => {
            post.style.animationDelay = `${index * 0.1}s`;
            post.classList.add('fade-in');
        });
        
        // Smooth scrolling for anchor links
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
    }

    // Toast notification system
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close">&times;</button>
            </div>
        `;
        
        // Add toast styles if not present
        if (!document.querySelector('#toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 12px;
                    padding: 15px 20px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    z-index: 1000;
                    transform: translateX(100%);
                    transition: transform 0.3s ease;
                    max-width: 300px;
                    border-left: 4px solid;
                }
                .toast-success { border-left-color: #28a745; }
                .toast-error { border-left-color: #dc3545; }
                .toast-info { border-left-color: #007bff; }
                .toast-content {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 10px;
                }
                .toast-close {
                    background: none;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    opacity: 0.7;
                }
                .toast-close:hover { opacity: 1; }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);
        
        // Add close functionality
        toast.querySelector('.toast-close').addEventListener('click', () => {
            removeToast(toast);
        });
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            removeToast(toast);
        }, 3000);
    }

    function removeToast(toast) {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    // Search functionality enhancements
    const searchInput = document.querySelector('input[name="search_query"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            // Add visual feedback
            if (this.value.length > 0) {
                this.style.borderColor = '#667eea';
            } else {
                this.style.borderColor = '';
            }
        });
    }

    // Auto-resize textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Add focus animations to form inputs
    document.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
            this.parentElement.style.transition = 'transform 0.2s ease';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });
});

// Utility function to debounce function calls
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

// Check for browser support of modern features
function checkBrowserSupport() {
    if (!window.fetch) {
        console.warn('Fetch API not supported, some features may not work');
    }
    if (!window.Promise) {
        console.warn('Promises not supported, some features may not work');
    }
}
