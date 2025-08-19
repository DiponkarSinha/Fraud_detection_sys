# Fraud Detection Dashboard

A modern, real-time web dashboard for fraud analysts to monitor and investigate fraudulent transactions.

## Features

### 🎯 **Real-Time Fraud Monitoring**
- Live detection of fraudulent transactions
- Automatic updates every 30 seconds
- Integration with the fraud detection pipeline

### 📊 **Interactive Analytics**
- Transaction distribution charts (legitimate vs fraudulent)
- Risk level visualization (high, medium, low)
- Real-time statistics and metrics

### 🔍 **Transaction Investigation**
- Detailed transaction information
- Risk scoring and assessment
- Customer and merchant details
- Device fingerprinting data

### 🚨 **Alert Management**
- Visual fraud alerts
- Risk-based color coding
- Transaction blocking capabilities
- Export functionality for reports

## Quick Start

### 1. Install Dependencies
```bash
cd dashboard
pip3 install -r requirements.txt
```

### 2. Start the Dashboard
```bash
python3 app.py
```

### 3. Access the Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```

## Dashboard Components

### Statistics Cards
- **Total Transactions**: Overall transaction count
- **Fraud Detected**: Number of fraudulent transactions
- **Fraud Rate**: Percentage of fraudulent transactions
- **Last Updated**: Timestamp of last data refresh

### Charts
- **Transaction Distribution**: Pie chart showing legitimate vs fraudulent transactions
- **Risk Level Distribution**: Bar chart showing high/medium/low risk transactions

### Fraud Transactions Table
- **Transaction ID**: Unique identifier
- **Amount**: Transaction amount with risk-based color coding
- **Merchant**: Merchant name
- **Location**: Transaction location
- **Risk Score**: Fraud probability percentage
- **Risk Level**: High/Medium/Low risk classification
- **Timestamp**: When the transaction occurred
- **Actions**: View details, block transaction

## API Endpoints

### GET `/api/fraud-data`
Returns complete fraud detection data including transactions and statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "transactions": [...],
    "statistics": {...},
    "lastUpdate": "2025-01-19T14:00:00Z"
  }
}
```

### GET `/api/statistics`
Returns fraud detection statistics only.

### GET `/api/transactions`
Returns fraud transactions only.

### GET `/api/transaction/<id>`
Returns detailed information for a specific transaction.

### GET `/api/health`
Health check endpoint.

## Data Integration

The dashboard automatically integrates with:

1. **fraud_report.json**: Real-time fraud detection results
2. **CSV Files**: Latest transaction data from `data/raw/` directory
3. **File Monitor**: Live detection of new transaction files

## Transaction Risk Assessment

### Risk Scoring
- **High Risk (80-100%)**: Red indicators, immediate attention required
- **Medium Risk (60-79%)**: Yellow indicators, review recommended
- **Low Risk (0-59%)**: Green indicators, likely legitimate

### Risk Factors
- Transaction amount
- Merchant reputation
- Geographic location
- Device fingerprinting
- Historical patterns

## Features in Detail

### 🔄 **Auto-Refresh**
- Dashboard updates every 30 seconds
- Real-time fraud detection integration
- Live statistics and charts

### 📱 **Responsive Design**
- Mobile-friendly interface
- Tablet and desktop optimized
- Touch-friendly controls

### 🎨 **Modern UI**
- Bootstrap 5 framework
- Font Awesome icons
- Chart.js visualizations
- Professional color scheme

### 🔒 **Security Features**
- Masked card numbers
- Secure data handling
- No sensitive data logging

## Usage Examples

### Investigating a Fraud Alert
1. Click on a high-risk transaction in the table
2. Review detailed transaction information
3. Analyze risk factors and customer data
4. Take action: confirm fraud or mark legitimate

### Monitoring Fraud Trends
1. Check the statistics cards for overall metrics
2. Review the distribution charts for patterns
3. Export data for further analysis
4. Set up alerts for specific thresholds

### Exporting Reports
1. Click the "Export" button
2. CSV file downloads with all fraud data
3. Use for compliance reporting
4. Share with stakeholders

## Troubleshooting

### Dashboard Not Loading
- Ensure Flask server is running on port 5000
- Check browser console for JavaScript errors
- Verify all dependencies are installed

### No Data Showing
- Confirm fraud_report.json exists
- Check CSV files in data/raw/ directory
- Verify file monitor is running

### Charts Not Rendering
- Ensure Chart.js library loads correctly
- Check browser compatibility
- Clear browser cache

## Development

### File Structure
```
dashboard/
├── app.py              # Flask backend
├── index.html          # Main dashboard page
├── dashboard.js        # Frontend JavaScript
├── styles.css          # Custom styling
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding New Features
1. Update the Flask backend in `app.py`
2. Modify the frontend in `dashboard.js`
3. Add styling in `styles.css`
4. Test with sample data

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Examine browser console logs
4. Verify system requirements

---

**🚨 Fraud Detection Dashboard - Protecting Your Business in Real-Time**