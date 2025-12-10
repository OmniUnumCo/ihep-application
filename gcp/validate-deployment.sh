#!/bin/bash

# Health Insight Ventures - Deployment Validation Script
set -e

PROJECT_ID="ihep-app"
REGION="us-central1"

echo "🔍 Validating Health Insight Ventures deployment..."

# Check if project exists and is accessible
echo "📋 Checking project access..."
if gcloud projects describe $PROJECT_ID &>/dev/null; then
    echo "✅ Project $PROJECT_ID is accessible"
else
    echo "❌ Cannot access project $PROJECT_ID"
    echo "Please ensure you have proper permissions and the project exists"
    exit 1
fi

# Check APIs
echo "🔧 Checking required APIs..."
REQUIRED_APIS=(
    "cloudfunctions.googleapis.com"
    "bigquery.googleapis.com"
    "storage.googleapis.com"
    "secretmanager.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo "✅ $api is enabled"
    else
        echo "❌ $api is not enabled"
        echo "Run: gcloud services enable $api"
    fi
done

# Check if Cloud Function exists
echo "☁️ Checking Cloud Function..."
if gcloud functions describe health-insight-api --region=$REGION &>/dev/null; then
    echo "✅ Cloud Function 'health-insight-api' exists"
    
    # Test the function
    FUNCTION_URL="https://$REGION-$PROJECT_ID.cloudfunctions.net/health-insight-api"
    echo "🌐 Testing function at: $FUNCTION_URL/health"
    
    if curl -s --max-time 10 "$FUNCTION_URL/health" | grep -q "healthy"; then
        echo "✅ Function is responding correctly"
    else
        echo "⚠️ Function exists but may not be responding correctly"
    fi
else
    echo "❌ Cloud Function 'health-insight-api' not found"
fi

# Check BigQuery dataset
echo "🗄️ Checking BigQuery dataset..."
if bq ls -d $PROJECT_ID:health_insight_platform &>/dev/null; then
    echo "✅ BigQuery dataset 'health_insight_platform' exists"
    
    # Check if tables exist
    TABLE_COUNT=$(bq ls $PROJECT_ID:health_insight_platform | grep -c "TABLE" || echo "0")
    echo "📊 Found $TABLE_COUNT tables in dataset"
else
    echo "❌ BigQuery dataset 'health_insight_platform' not found"
fi

# Check Cloud Storage bucket
echo "📦 Checking Cloud Storage bucket..."
BUCKET_NAME="$PROJECT_ID-health-insight-frontend"
if gsutil ls "gs://$BUCKET_NAME" &>/dev/null; then
    echo "✅ Storage bucket '$BUCKET_NAME' exists"
    
    # Check if frontend files exist
    if gsutil ls "gs://$BUCKET_NAME/index.html" &>/dev/null; then
        echo "✅ Frontend files deployed"
        echo "🌐 Production URL: https://ihep.app"
    else
        echo "⚠️ Bucket exists but frontend files not found"
    fi
else
    echo "❌ Storage bucket '$BUCKET_NAME' not found"
fi

# Check secrets
echo "🔐 Checking secrets..."
REQUIRED_SECRETS=(
    "OPENAI_API_KEY"
    "SENDGRID_API_KEY"
    "TWILIO_ACCOUNT_SID"
    "TWILIO_AUTH_TOKEN"
    "TWILIO_PHONE_NUMBER"
)

for secret in "${REQUIRED_SECRETS[@]}"; do
    if gcloud secrets describe $secret &>/dev/null; then
        echo "✅ Secret '$secret' exists"
    else
        echo "⚠️ Secret '$secret' not found - please create it"
    fi
done

echo ""
echo "🎯 Validation Summary:"
echo "=============================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Frontend: https://ihep.app"
echo "API: https://api.ihep.app"
echo "Backup: https://backup.ihep.app"
echo ""
echo "If all checks passed ✅, your deployment is ready!"
echo "If any checks failed ❌, please address them before proceeding."