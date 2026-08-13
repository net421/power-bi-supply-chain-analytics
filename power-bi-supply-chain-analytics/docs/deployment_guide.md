# Deployment Guide

## Overview

This guide provides instructions for deploying the Supply Chain Analytics dashboard to various environments.

---

## Local Development

### Prerequisites

1. Python 3.9 or higher
2. pip package manager
3. Git (optional, for version control)

### Installation Steps

```bash
# Navigate to project directory
cd power-bi-supply-chain-analytics

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python data/generate_data.py

# Validate data quality
python validation/data_quality_checks.py

# Run KPI verification tests
python validation/kpi_verification.py

# Launch dashboard
streamlit run dashboards/app.py
```

The dashboard will be available at `http://localhost:8501`

---

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate data on container start
CMD ["streamlit", "run", "dashboards/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build Docker image
docker build -t supply-chain-analytics .

# Run container
docker run -p 8501:8501 supply-chain-analytics
```

Access at `http://localhost:8501`

---

## Cloud Deployment Options

### Streamlit Cloud (Free)

1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Configure:
   - Main file path: `dashboards/app.py`
   - Python version: 3.9
5. Deploy!

**Note**: Data files must be generated during deployment or stored in repo.

### AWS Deployment

#### Option A: EC2 Instance

```bash
# Launch Ubuntu EC2 instance
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Install Python and dependencies
sudo apt update
sudo apt install python3-pip -y
pip3 install streamlit pandas plotly numpy

# Clone repository
git clone <your-repo-url>
cd power-bi-supply-chain-analytics

# Install requirements
pip3 install -r requirements.txt

# Generate data
python3 data/generate_data.py

# Run Streamlit (background)
nohup streamlit run dashboards/app.py --server.port=8501 --server.address=0.0.0.0 &
```

Configure Security Group to allow inbound traffic on port 8501.

#### Option B: AWS Elastic Beanstalk

1. Create `application.py`:
```python
from dashboards.app import main
```

2. Create `.ebextensions/streamlit.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: application.py
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current"
```

3. Deploy using EB CLI:
```bash
pip install awsebcli
eb init
eb create supply-chain-env
eb deploy
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/supply-chain-analytics

# Deploy to Cloud Run
gcloud run deploy supply-chain-analytics \
  --image gcr.io/PROJECT_ID/supply-chain-analytics \
  --platform managed \
  --port 8501 \
  --allow-unauthenticated
```

### Azure

#### App Service

1. Containerize the application (see Docker section)
2. Push to Azure Container Registry
3. Deploy to App Service:
```bash
az webapp create --resource-group <RG> --plan <PLAN> \
  --name <APP-NAME> --deployment-container-image-name <IMAGE>
```

---

## Production Considerations

### Data Management

For production use, replace the synthetic data generator with:

1. **Database Connection**: Connect to actual ERP/WMS systems
2. **ETL Pipeline**: Schedule regular data updates
3. **Data Refresh**: Implement incremental refresh logic

Example database connection:
```python
import sqlalchemy

def load_from_database():
    engine = sqlalchemy.create_engine('postgresql://user:pass@host:5432/db')
    orders = pd.read_sql('SELECT * FROM orders', engine)
    return orders
```

### Security

1. **Authentication**: Add login requirement
```python
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(...)
name, auth_status, key = authenticator.login('Login', 'main')
```

2. **Environment Variables**: Store secrets securely
```python
import os
db_password = os.environ.get('DB_PASSWORD')
```

3. **HTTPS**: Enable SSL/TLS for production

### Performance Optimization

1. **Caching**: Use Streamlit caching
```python
@st.cache_data
def load_data():
    return pd.read_csv('large_file.csv')
```

2. **Pagination**: Limit table row display
```python
st.dataframe(df.head(100))
```

3. **Sampling**: Use data samples for large datasets
```python
sample_df = df.sample(n=10000, random_state=42)
```

### Monitoring

1. **Logging**: Add application logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

2. **Health Checks**: Implement status endpoint
3. **Metrics**: Track usage and performance

---

## Scheduled Updates

### Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add daily data refresh at 2 AM
0 2 * * * cd /path/to/project && /path/to/venv/bin/python data/generate_data.py
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/hourly)
4. Action: Start program
   - Program: `python.exe`
   - Arguments: `data/generate_data.py`
   - Start in: project directory

### Airflow DAG

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {'retries': 3}

with DAG('supply_chain_data_refresh', 
         default_args=default_args,
         schedule_interval='@daily') as dag:
    
    generate_data = BashOperator(
        task_id='generate_data',
        bash_command='cd /app && python data/generate_data.py'
    )
    
    validate_data = BashOperator(
        task_id='validate_data',
        bash_command='cd /app && python validation/data_quality_checks.py'
    )
    
    generate_data >> validate_data
```

---

## Troubleshooting

### Common Issues

**Issue**: Dashboard loads slowly
- **Solution**: Enable caching, reduce data size, optimize queries

**Issue**: Out of memory errors
- **Solution**: Use data sampling, implement pagination, increase container memory

**Issue**: Data not refreshing
- **Solution**: Check file permissions, verify cron/task scheduler configuration

**Issue**: Port conflicts
- **Solution**: Use different port: `streamlit run app.py --server.port 8502`

---

## Support

For issues or questions:
1. Check README.md for general information
2. Review validation scripts for data issues
3. Examine logs for error messages
