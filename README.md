# 🛡️ Fraud Detection System

A comprehensive end-to-end machine learning system for real-time fraud detection in banking transactions.

## 🚀 Features

- **Real-time Fraud Detection**: Processes transactions in real-time with sub-second response times
- **Multiple ML Models**: Logistic Regression, Random Forest, Gradient Boosting, and SVM
- **High Performance**: Achieves 99.74% ROC AUC with Gradient Boosting model
- **Automated Pipeline**: Complete data processing and model training automation
- **Alert System**: Intelligent fraud alerts with priority levels (HIGH/CRITICAL)
- **Scalable Architecture**: Supports both batch and streaming data processing
- **Cloud Ready**: AWS deployment with Docker containerization
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## 📊 Model Performance

| Model | ROC AUC | F1 Score | Best Parameters |
|-------|---------|----------|----------------|
| Logistic Regression | 0.9092 | 0.6688 | C=1, penalty=l1 |
| Random Forest | 0.9954 | 0.9022 | n_estimators=300, max_depth=20 |
| Gradient Boosting | 0.9974 | 0.9243 | learning_rate=0.05, max_depth=5 |
| SVM | Training | - | - |

## 🏗️ Project Structure

```
Fraud_detection_sys/
├── config/                    # Configuration files
├── data/                      # Data storage
│   ├── raw/                  # Raw transaction data
│   └── processed/            # Processed datasets
├── deploy/                    # Deployment scripts
│   └── notifications/        # Notification services
├── logs/                      # Application logs
├── models/                    # Trained models and artifacts
├── outputs/                   # Output files
├── reports/                   # Generated reports
├── src/                       # Source code
│   ├── alerts/               # Fraud alerts
│   ├── api/                  # REST API
│   ├── data_processing/      # Data pipeline
│   ├── models/               # ML models
│   └── utils/                # Helper functions
├── tests/                     # Test suites
│   └── unit/                 # Unit tests
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Multi-container setup
├── requirements.txt           # Python dependencies
└── setup.py                   # Package setup
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip
- Git
- AWS CLI (for cloud deployment)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/DiponkarSinha/Fraud_detection_sys.git
   cd Fraud_detection_sys
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv fraud_env
   source fraud_env/bin/activate  # On Windows: fraud_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your actual credentials
   ```

## 🚀 Quick Start

### 1. Generate Synthetic Data
```bash
python -m src.data_processing.synthetic_data_generator
```

### 2. Process Data
```bash
python -m src.data_processing.data_pipeline
```

### 3. Train Models
```bash
python -m src.models.model_training
```

### 4. Start API Server
```bash
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access API Documentation
Open http://localhost:8000/docs in your browser

### 6. Run Fraud Detection
```bash
python -m src.data_processing.incremental_processor
```

## 🐳 Docker Deployment

### Build and Run
```bash
docker build -t fraud-detection .
docker run -p 8000:8000 fraud-detection
```

### Docker Compose
```bash
docker-compose up -d
```

## ☁️ AWS Deployment

### Prerequisites
- AWS CLI configured
- Appropriate IAM permissions
- S3 bucket for data storage
- SES configured for email alerts

### Deploy to AWS
```bash
# Set up AWS resources
python scripts/setup/deploy_complete_pipeline.py

# Verify setup
python scripts/verification/check_aws_setup_status.py
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `.env.template`:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your_account_id

# Database Configuration
DATABASE_URL=your_database_url

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email
EMAIL_PASSWORD=your_password
```

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/unit/ -v
```

### Run Integration Tests
```bash
python -m pytest tests/integration/ -v
```

## 📈 API Endpoints

- `POST /predict` - Predict fraud for a single transaction
- `POST /batch_predict` - Predict fraud for multiple transactions
- `GET /model_info` - Get current model information
- `GET /health` - Health check endpoint
- `GET /metrics` - System metrics

## 🔍 Monitoring

The system includes comprehensive monitoring:

- **Performance Metrics**: Response time, throughput, accuracy
- **System Health**: CPU, memory, disk usage
- **Alert Management**: Real-time fraud alerts with email notifications
- **Model Drift Detection**: Automatic model performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@frauddetection.com
- Documentation: [Wiki](https://github.com/DiponkarSinha/Fraud_detection_sys/wiki)

## 🙏 Acknowledgments

- Thanks to the open-source community for the amazing libraries
- Special thanks to contributors and testers
- Inspired by real-world fraud detection challenges

---

**Built with ❤️ for secure financial transactions**