// GetLate Social Media Automation - Main JavaScript Application

class SocialMediaApp {
    constructor() {
        this.currentWorkflowId = null;
        this.isRecording = false;
        this.recognition = null;
        
        this.initializeEventListeners();
        this.initializeVoiceRecognition();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('contentForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createContent();
        });

        // Voice input button
        document.getElementById('voiceInputBtn').addEventListener('click', () => {
            this.toggleVoiceInput();
        });

        // Publish button
        document.getElementById('publishBtn').addEventListener('click', () => {
            this.publishContent();
        });

        // Navigation buttons
        document.getElementById('analyticsBtn').addEventListener('click', () => {
            this.showAnalytics();
        });

        document.getElementById('accountsBtn').addEventListener('click', () => {
            this.showAccounts();
        });
    }

    initializeVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('topic').value = transcript;
                document.getElementById('voiceInput').value = transcript;
                this.stopRecording();
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopRecording();
                this.showAlert('Voice input error: ' + event.error, 'danger');
            };

            this.recognition.onend = () => {
                this.stopRecording();
            };
        }
    }

    toggleVoiceInput() {
        if (!this.recognition) {
            this.showAlert('Voice input is not supported in your browser.', 'warning');
            return;
        }

        if (this.isRecording) {
            this.recognition.stop();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        this.isRecording = true;
        const btn = document.getElementById('voiceInputBtn');
        btn.classList.add('recording');
        btn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting speech recognition:', error);
            this.stopRecording();
        }
    }

    stopRecording() {
        this.isRecording = false;
        const btn = document.getElementById('voiceInputBtn');
        btn.classList.remove('recording');
        btn.innerHTML = '<i class="fas fa-microphone"></i> Use Voice Input';
    }

    async createContent() {
        const form = document.getElementById('contentForm');
        const formData = new FormData(form);
        
        // Show loading state
        this.showLoading(true);
        this.hideResults();
        
        try {
            const response = await fetch('/create-content', {
                method: 'POST',
                body: formData
            });
            
            // Check if response is HTML (redirect to review page)
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/html')) {
                // Replace current page with the HTML response (review page)
                const html = await response.text();
                document.open();
                document.write(html);
                document.close();
                return;
            }
            
            // Handle JSON response (for backward compatibility)
            const result = await response.json();
            
            if (result.success) {
                this.currentWorkflowId = result.workflow_id;
                this.displayContentResults(result);
                this.showAlert('Content created successfully!', 'success');
            } else {
                throw new Error(result.message || 'Failed to create content');
            }
            
        } catch (error) {
            console.error('Error creating content:', error);
            this.showAlert('Error creating content: ' + error.message, 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    displayContentResults(result) {
        const contentPreview = document.getElementById('contentPreview');
        const imagePreview = document.getElementById('imagePreview');
        const analyticsPreview = document.getElementById('analyticsPreview');
        
        // Display generated content
        let contentHtml = '<h5><i class="fas fa-file-alt"></i> Generated Content</h5>';
        const content = result.content;
        
        for (const [platform, variants] of Object.entries(content)) {
            contentHtml += `
                <div class="content-platform">
                    <div class="platform-header">
                        <i class="fab fa-${this.getPlatformIcon(platform)} platform-icon"></i>
                        <span class="platform-name">${this.capitalizeFirst(platform)}</span>
                    </div>
                    <div class="content-text">${this.escapeHtml(variants[0])}</div>
                    <div class="variant-selector">
                        <small class="text-muted">Variant 1 of ${variants.length}</small>
                    </div>
                </div>
            `;
        }
        
        contentPreview.innerHTML = contentHtml;
        
        // Display generated image if available
        if (result.image_url) {
            document.getElementById('generatedImage').src = result.image_url;
            imagePreview.style.display = 'block';
        }
        
        // Display analytics if available
        if (result.analytics && Object.keys(result.analytics).length > 0) {
            let analyticsHtml = '';
            for (const [key, value] of Object.entries(result.analytics)) {
                analyticsHtml += `
                    <div class="analytics-metric">
                        <span class="metric-label">${this.capitalizeFirst(key.replace('_', ' '))}:</span>
                        <span class="metric-value">${value}</span>
                    </div>
                `;
            }
            document.getElementById('analyticsContent').innerHTML = analyticsHtml;
            analyticsPreview.style.display = 'block';
        }
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
    }

    async publishContent() {
        if (!this.currentWorkflowId) {
            this.showAlert('No content to publish. Please create content first.', 'warning');
            return;
        }
        
        // Show publishing status
        const publishingStatus = document.getElementById('publishingStatus');
        const publishBtn = document.getElementById('publishBtn');
        if (publishingStatus) {
            publishingStatus.style.display = 'block';
        }
        if (publishBtn) {
            publishBtn.disabled = true;
        }
        
        try {
            const formData = new FormData();
            formData.append('workflow_id', this.currentWorkflowId);
            
            const response = await fetch('/publish-content', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayPublishResults(result);
                this.showAlert('Content published successfully!', 'success');
            } else {
                throw new Error(result.message || 'Failed to publish content');
            }
            
        } catch (error) {
            console.error('Error publishing content:', error);
            this.showAlert('Error publishing content: ' + error.message, 'danger');
        } finally {
            const publishingStatus = document.getElementById('publishingStatus');
            const publishBtn = document.getElementById('publishBtn');
            if (publishingStatus) {
                publishingStatus.style.display = 'none';
            }
            if (publishBtn) {
                publishBtn.disabled = false;
            }
        }
    }

    displayPublishResults(result) {
        const publishResults = document.getElementById('publishResults');
        const publishDetails = document.getElementById('publishDetails');
        
        let detailsHtml = '<h6>Publication Results:</h6>';
        const results = result.results;
        
        for (const [platform, data] of Object.entries(results)) {
            const status = data.success ? 'success' : 'danger';
            const icon = data.success ? 'check-circle' : 'times-circle';
            
            detailsHtml += `
                <div class="alert alert-${status} alert-sm">
                    <i class="fas fa-${icon}"></i>
                    <strong>${this.capitalizeFirst(platform)}:</strong> 
                    ${data.success ? 'Published successfully' : 'Failed - ' + data.error}
                </div>
            `;
        }
        
        publishDetails.innerHTML = detailsHtml;
        if (publishResults) {
            publishResults.style.display = 'block';
        }
    }

    async showAnalytics() {
        try {
            const response = await fetch('/analytics');
            const result = await response.json();
            
            if (result.success) {
                this.displayAnalytics(result.analytics);
                const modal = new bootstrap.Modal(document.getElementById('analyticsModal'));
                modal.show();
            } else {
                throw new Error('Failed to load analytics');
            }
            
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showAlert('Error loading analytics: ' + error.message, 'danger');
        }
    }

    displayAnalytics(analytics) {
        const modalBody = document.getElementById('analyticsModalBody');
        
        let html = '<div class="row">';
        
        // System stats
        if (analytics.system_stats) {
            html += `
                <div class="col-md-6">
                    <div class="analytics-card">
                        <h6><i class="fas fa-cogs"></i> System Statistics</h6>
            `;
            
            for (const [key, value] of Object.entries(analytics.system_stats)) {
                html += `
                    <div class="analytics-metric">
                        <span class="metric-label">${this.capitalizeFirst(key.replace('_', ' '))}:</span>
                        <span class="metric-value">${value}</span>
                    </div>
                `;
            }
            
            html += '</div></div>';
        }
        
        // Platform stats
        if (analytics.platform_stats) {
            html += `
                <div class="col-md-6">
                    <div class="analytics-card">
                        <h6><i class="fas fa-share-alt"></i> Platform Statistics</h6>
            `;
            
            for (const [platform, stats] of Object.entries(analytics.platform_stats)) {
                html += `
                    <div class="analytics-metric">
                        <span class="metric-label">${this.capitalizeFirst(platform)}:</span>
                        <span class="metric-value">${stats.posts} posts</span>
                    </div>
                `;
            }
            
            html += '</div></div>';
        }
        
        html += '</div>';
        modalBody.innerHTML = html;
    }

    async showAccounts() {
        try {
            const response = await fetch('/accounts');
            const result = await response.json();
            
            if (result.success) {
                this.displayAccounts(result.accounts);
                const modal = new bootstrap.Modal(document.getElementById('accountsModal'));
                modal.show();
            } else {
                throw new Error('Failed to load accounts');
            }
            
        } catch (error) {
            console.error('Error loading accounts:', error);
            this.showAlert('Error loading accounts: ' + error.message, 'danger');
        }
    }

    displayAccounts(accounts) {
        const modalBody = document.getElementById('accountsModalBody');
        
        if (!accounts || accounts.length === 0) {
            modalBody.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-users-slash fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No connected accounts found.</p>
                    <p class="small text-muted">Connect your social media accounts in the GetLate dashboard.</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="list-group">';
        
        accounts.forEach(account => {
            const statusClass = account.connected ? 'success' : 'warning';
            const statusIcon = account.connected ? 'check-circle' : 'exclamation-triangle';
            
            html += `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">
                            <i class="fab fa-${this.getPlatformIcon(account.platform)}"></i>
                            ${this.capitalizeFirst(account.platform)}
                        </h6>
                        <small class="text-${statusClass}">
                            <i class="fas fa-${statusIcon}"></i>
                            ${account.connected ? 'Connected' : 'Not Connected'}
                        </small>
                    </div>
                    <p class="mb-1 small text-muted">${account.username || 'No username'}</p>
                </div>
            `;
        });
        
        html += '</div>';
        modalBody.innerHTML = html;
    }

    // Utility functions
    showLoading(show) {
        const loadingSpinner = document.getElementById('loadingSpinner');
        if (loadingSpinner) {
            loadingSpinner.style.display = show ? 'block' : 'none';
        }
    }

    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        const publishResults = document.getElementById('publishResults');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        if (publishResults) {
            publishResults.style.display = 'none';
        }
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    getPlatformIcon(platform) {
        const iconMap = {
            'twitter': 'twitter',
            'linkedin': 'linkedin',
            'facebook': 'facebook',
            'instagram': 'instagram',
            'reddit': 'reddit'
        };
        return iconMap[platform] || 'share-alt';
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SocialMediaApp();
});