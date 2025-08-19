// Fraud Detection Dashboard JavaScript

class FraudDashboard {
    constructor() {
        this.fraudData = [];
        this.charts = {};
        this.refreshInterval = null;
        this.selectedTransaction = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadFraudData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Refresh button
        window.refreshData = () => this.loadFraudData();
        
        // Export button
        window.exportData = () => this.exportToCSV();
        
        // Modal actions
        window.markAsConfirmedFraud = () => this.markTransaction('confirmed_fraud');
        window.markAsLegitimate = () => this.markTransaction('legitimate');
        
        // Transaction row click
        window.showTransactionDetails = (transactionId) => this.showTransactionModal(transactionId);
    }

    async loadFraudData() {
        try {
            this.showLoading();
            
            // Try to load from Flask API first
            const apiData = await this.loadFromAPI();
            if (apiData) {
                this.processAPIData(apiData);
            } else {
                // Try to load from fraud_report.json
                const reportData = await this.loadFraudReport();
                if (reportData) {
                    this.processFraudReport(reportData);
                } else {
                    // Fallback to sample data for demonstration
                    this.loadSampleData();
                }
            }
            
            this.updateDashboard();
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading fraud data:', error);
            this.showAlert('Error loading fraud data. Using sample data.', 'warning');
            this.loadSampleData();
            this.updateDashboard();
            this.hideLoading();
        }
    }

    async loadFromAPI() {
        try {
            const response = await fetch('/api/fraud-data');
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    return result.data;
                }
            }
        } catch (error) {
            console.log('Could not load from API, trying fraud_report.json');
        }
        return null;
    }

    async loadFraudReport() {
        try {
            const response = await fetch('../fraud_report.json');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.log('Could not load fraud_report.json, using sample data');
        }
        return null;
    }

    processAPIData(apiData) {
        // Use data directly from API
        this.fraudData = apiData.transactions || [];
        
        // Update statistics from API
        if (apiData.statistics) {
            this.updateStatistics({
                totalTransactions: apiData.statistics.totalTransactions,
                fraudDetected: apiData.statistics.fraudDetected,
                fraudRate: apiData.statistics.fraudRate,
                lastUpdated: apiData.statistics.lastUpdated
            });
        }
    }

    processFraudReport(reportData) {
        // Generate sample transactions based on the report data
        const totalTransactions = reportData.total_transactions || 0;
        const fraudCount = reportData.fraud_detected || 0;
        const highRisk = reportData.high_risk_transactions || 0;
        const mediumRisk = reportData.medium_risk_transactions || 0;
        const lowRisk = reportData.low_risk_transactions || 0;
        
        this.fraudData = [];
        
        // Generate fraudulent transactions
        for (let i = 0; i < fraudCount; i++) {
            this.fraudData.push(this.generateTransaction(true, i));
        }
        
        // Update statistics
        this.updateStatistics({
            totalTransactions,
            fraudDetected: fraudCount,
            fraudRate: totalTransactions > 0 ? ((fraudCount / totalTransactions) * 100).toFixed(1) : 0,
            lastUpdated: reportData.timestamp || new Date().toISOString()
        });
    }

    loadSampleData() {
        // Sample fraudulent transactions for demonstration
        this.fraudData = [
            {
                id: 'TXN001',
                amount: 15000.00,
                merchant: 'Unknown Online Store',
                location: 'Lagos, Nigeria',
                riskScore: 95,
                riskLevel: 'high',
                timestamp: new Date(Date.now() - 3600000).toISOString(),
                cardNumber: '**** **** **** 1234',
                customerName: 'John Doe',
                transactionType: 'Online Purchase',
                ipAddress: '192.168.1.100',
                deviceFingerprint: 'Unknown Device'
            },
            {
                id: 'TXN002',
                amount: 8500.50,
                merchant: 'ATM Withdrawal',
                location: 'Moscow, Russia',
                riskScore: 88,
                riskLevel: 'high',
                timestamp: new Date(Date.now() - 7200000).toISOString(),
                cardNumber: '**** **** **** 5678',
                customerName: 'Jane Smith',
                transactionType: 'ATM Withdrawal',
                ipAddress: '10.0.0.50',
                deviceFingerprint: 'ATM Terminal'
            },
            {
                id: 'TXN003',
                amount: 2500.00,
                merchant: 'Gas Station XYZ',
                location: 'Detroit, MI',
                riskScore: 72,
                riskLevel: 'medium',
                timestamp: new Date(Date.now() - 10800000).toISOString(),
                cardNumber: '**** **** **** 9012',
                customerName: 'Bob Johnson',
                transactionType: 'Point of Sale',
                ipAddress: 'N/A',
                deviceFingerprint: 'POS Terminal'
            }
        ];
        
        this.updateStatistics({
            totalTransactions: 150,
            fraudDetected: this.fraudData.length,
            fraudRate: ((this.fraudData.length / 150) * 100).toFixed(1),
            lastUpdated: new Date().toISOString()
        });
    }

    generateTransaction(isFraud, index) {
        const merchants = ['Unknown Store', 'Suspicious Vendor', 'Fake Shop', 'Fraudulent Site'];
        const locations = ['Lagos, Nigeria', 'Moscow, Russia', 'Unknown Location', 'Suspicious Area'];
        const amounts = [5000, 8500, 12000, 15000, 20000];
        
        return {
            id: `TXN${String(index + 1).padStart(3, '0')}`,
            amount: amounts[index % amounts.length] + (Math.random() * 1000),
            merchant: merchants[index % merchants.length],
            location: locations[index % locations.length],
            riskScore: 70 + Math.random() * 30,
            riskLevel: Math.random() > 0.5 ? 'high' : 'medium',
            timestamp: new Date(Date.now() - (index * 3600000)).toISOString(),
            cardNumber: `**** **** **** ${Math.floor(1000 + Math.random() * 9000)}`,
            customerName: `Customer ${index + 1}`,
            transactionType: 'Online Purchase',
            ipAddress: `192.168.1.${Math.floor(100 + Math.random() * 155)}`,
            deviceFingerprint: 'Unknown Device'
        };
    }

    updateStatistics(stats) {
        // Use banking dataset statistics if available
        const totalTransactions = stats.totalTransactions || stats.total_transactions || 0;
        const fraudDetected = stats.fraudDetected || stats.fraud_detected || 0;
        const fraudRate = stats.fraudRate || stats.fraud_rate || 0;
        const lastUpdated = stats.lastUpdated || stats.last_updated || new Date().toISOString();
        
        document.getElementById('totalTransactions').textContent = totalTransactions.toLocaleString();
        document.getElementById('fraudDetected').textContent = fraudDetected.toLocaleString();
        document.getElementById('fraudRate').textContent = fraudRate + '%';
        document.getElementById('lastUpdated').textContent = new Date(lastUpdated).toLocaleString();
    }

    updateDashboard() {
        this.renderFraudTable();
        this.updateCharts();
        
        if (this.fraudData.length > 0) {
            this.showAlert(`${this.fraudData.length} fraudulent transactions detected!`, 'danger');
        }
    }

    renderFraudTable() {
        const tbody = document.getElementById('fraudTableBody');
        
        if (this.fraudData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        <i class="fas fa-search me-2"></i>
                        No fraudulent transactions detected
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.fraudData.map(transaction => `
            <tr class="fade-in" onclick="showTransactionDetails('${transaction.id}')" style="cursor: pointer;">
                <td><strong>${transaction.id}</strong></td>
                <td class="amount ${this.getAmountClass(transaction.amount)}">
                    $${transaction.amount.toLocaleString('en-US', {minimumFractionDigits: 2})}
                </td>
                <td>${transaction.merchant}</td>
                <td>
                    <i class="fas fa-map-marker-alt me-1"></i>
                    ${transaction.location}
                </td>
                <td>
                    <div class="risk-score">
                        <div class="risk-score-bar">
                            <div class="risk-score-fill bg-${this.getRiskColor(transaction.riskScore)}" 
                                 style="width: ${transaction.riskScore}%"></div>
                        </div>
                        <div class="risk-score-text">${Math.round(transaction.riskScore)}%</div>
                    </div>
                </td>
                <td>
                    <span class="risk-badge risk-${transaction.riskLevel}">
                        ${transaction.riskLevel}
                    </span>
                </td>
                <td>${this.formatTimestamp(transaction.timestamp)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-info action-btn" 
                            onclick="event.stopPropagation(); showTransactionDetails('${transaction.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger action-btn" 
                            onclick="event.stopPropagation(); blockTransaction('${transaction.id}')">
                        <i class="fas fa-ban"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    initializeCharts() {
        // Transaction Distribution Chart
        const transactionCtx = document.getElementById('transactionChart').getContext('2d');
        this.charts.transaction = new Chart(transactionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Legitimate', 'Fraudulent'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: ['#28a745', '#dc3545'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Risk Level Chart
        const riskCtx = document.getElementById('riskChart').getContext('2d');
        this.charts.risk = new Chart(riskCtx, {
            type: 'bar',
            data: {
                labels: ['High Risk', 'Medium Risk', 'Low Risk'],
                datasets: [{
                    label: 'Transactions',
                    data: [0, 0, 0],
                    backgroundColor: ['#dc3545', '#ffc107', '#28a745'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    updateCharts() {
        // Update transaction distribution
        const totalTransactions = parseInt(document.getElementById('totalTransactions').textContent) || 0;
        const fraudCount = this.fraudData.length;
        const legitimateCount = totalTransactions - fraudCount;
        
        this.charts.transaction.data.datasets[0].data = [legitimateCount, fraudCount];
        this.charts.transaction.update();

        // Update risk level distribution
        const riskCounts = {
            high: this.fraudData.filter(t => t.riskLevel === 'high').length,
            medium: this.fraudData.filter(t => t.riskLevel === 'medium').length,
            low: this.fraudData.filter(t => t.riskLevel === 'low').length
        };
        
        this.charts.risk.data.datasets[0].data = [riskCounts.high, riskCounts.medium, riskCounts.low];
        this.charts.risk.update();
    }

    showTransactionModal(transactionId) {
        const transaction = this.fraudData.find(t => t.id === transactionId);
        if (!transaction) return;
        
        this.selectedTransaction = transaction;
        
        const detailsHtml = `
            <div class="detail-row">
                <span class="detail-label">Transaction ID:</span>
                <span class="detail-value"><strong>${transaction.id}</strong></span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Amount:</span>
                <span class="detail-value amount ${this.getAmountClass(transaction.amount)}">
                    $${transaction.amount.toLocaleString('en-US', {minimumFractionDigits: 2})}
                </span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Customer:</span>
                <span class="detail-value">${transaction.customerName}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Card Number:</span>
                <span class="detail-value">${transaction.cardNumber}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Merchant:</span>
                <span class="detail-value">${transaction.merchant}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Location:</span>
                <span class="detail-value">
                    <i class="fas fa-map-marker-alt me-1"></i>
                    ${transaction.location}
                </span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Transaction Type:</span>
                <span class="detail-value">${transaction.transactionType}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">IP Address:</span>
                <span class="detail-value">${transaction.ipAddress}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Device:</span>
                <span class="detail-value">${transaction.deviceFingerprint}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Risk Score:</span>
                <span class="detail-value">
                    <span class="risk-badge risk-${transaction.riskLevel}">
                        ${Math.round(transaction.riskScore)}% - ${transaction.riskLevel.toUpperCase()}
                    </span>
                </span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Timestamp:</span>
                <span class="detail-value">${this.formatTimestamp(transaction.timestamp)}</span>
            </div>
        `;
        
        document.getElementById('transactionDetails').innerHTML = detailsHtml;
        
        const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
        modal.show();
    }

    markTransaction(status) {
        if (!this.selectedTransaction) return;
        
        const action = status === 'confirmed_fraud' ? 'confirmed as fraud' : 'marked as legitimate';
        this.showAlert(`Transaction ${this.selectedTransaction.id} has been ${action}.`, 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
        modal.hide();
    }

    exportToCSV() {
        if (this.fraudData.length === 0) {
            this.showAlert('No data to export.', 'warning');
            return;
        }
        
        const headers = ['Transaction ID', 'Amount', 'Merchant', 'Location', 'Risk Score', 'Risk Level', 'Timestamp'];
        const csvContent = [
            headers.join(','),
            ...this.fraudData.map(t => [
                t.id,
                t.amount,
                `"${t.merchant}"`,
                `"${t.location}"`,
                t.riskScore,
                t.riskLevel,
                t.timestamp
            ].join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fraud_report_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        this.showAlert('Fraud report exported successfully.', 'success');
    }

    startAutoRefresh() {
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadFraudData();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showAlert(message, type = 'info') {
        const alertBanner = document.getElementById('alertBanner');
        const alertMessage = document.getElementById('alertMessage');
        
        alertBanner.className = `alert alert-${type} alert-dismissible fade show`;
        alertMessage.textContent = message;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            alertBanner.classList.add('d-none');
        }, 5000);
    }

    showEmailModal() {
        const modal = new bootstrap.Modal(document.getElementById('emailModal'));
        modal.show();
        
        // Clear previous results
        document.getElementById('emailResult').innerHTML = '';
        document.getElementById('emailAddress').value = '';
    }

    async sendEmail() {
        const emailAddress = document.getElementById('emailAddress').value;
        const resultDiv = document.getElementById('emailResult');
        
        if (!emailAddress) {
            resultDiv.innerHTML = '<div class="alert alert-danger">Please enter an email address.</div>';
            return;
        }
        
        // Show loading state
        resultDiv.innerHTML = '<div class="alert alert-info"><i class="fas fa-spinner fa-spin"></i> Preparing email...</div>';
        
        try {
            const response = await fetch('/api/send-dashboard-link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: emailAddress })
            });
            
            const result = await response.json();
            
            if (result.success) {
                resultDiv.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> <strong>Email prepared successfully!</strong><br>
                        <small>${result.message}</small>
                    </div>
                    <div class="alert alert-info">
                        <strong>Dashboard URLs:</strong><br>
                        <small>Local: <a href="${result.local_url}" target="_blank">${result.local_url}</a></small><br>
                        <small>Network: <a href="${result.dashboard_url}" target="_blank">${result.dashboard_url}</a></small>
                    </div>
                    <div class="alert alert-warning">
                        <i class="fas fa-info-circle"></i> <strong>Note:</strong> ${result.note}
                    </div>
                `;
                
                // Update network URL in the form
                document.getElementById('networkUrl').textContent = `Network: ${result.dashboard_url}`;
                
                this.showAlert(`Dashboard link prepared for ${emailAddress}`, 'success');
            } else {
                resultDiv.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> Error: ${result.error}</div>`;
            }
        } catch (error) {
            console.error('Error sending email:', error);
            resultDiv.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> Error: ${error.message}</div>`;
        }
    }

    showLoading() {
        // Could add loading spinner here
    }

    hideLoading() {
        // Could hide loading spinner here
    }

    formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    getAmountClass(amount) {
        if (amount > 10000) return 'high';
        if (amount > 5000) return 'medium';
        return 'low';
    }

    getRiskColor(riskScore) {
        if (riskScore >= 80) return 'danger';
        if (riskScore >= 60) return 'warning';
        return 'success';
    }
}

// Global functions for button clicks
window.blockTransaction = function(transactionId) {
    dashboard.showAlert(`Transaction ${transactionId} has been blocked.`, 'warning');
};

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', function() {
    dashboard = new FraudDashboard();
});