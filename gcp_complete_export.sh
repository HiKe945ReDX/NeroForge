#!/bin/bash
# Complete GCP Infrastructure Snapshot Script
# Saves output to file and prevents terminal exit
# Run: bash gcp_complete_export.sh

# IMPORTANT: Remove 'set -e' to prevent script from exiting on errors
set +e

# Output file with timestamp
OUTPUT_FILE="guidora_gcp_complete_$(date +%Y%m%d_%H%M%S).txt"

echo "Starting GCP export..."
echo "Output will be saved to: $OUTPUT_FILE"

# Function to safely execute commands
safe_exec() {
    local description="$1"
    shift
    echo "Running: $description" >&2
    "$@" 2>&1 || echo "⚠️  Warning: $description failed (continuing...)" >&2
}

# Start the export (redirect to file)
{
echo "=========================================="
echo "GUIDORA GCP COMPLETE INFRASTRUCTURE EXPORT"
echo "Date: $(date)"
echo "Project: guidora-main"
echo "=========================================="
echo ""

# Set project
gcloud config set project guidora-main 2>&1 || true

echo "=========================================="
echo "1. SECRET MANAGER - ALL SECRETS"
echo "=========================================="
gcloud secrets list --format="table(name,created,labels)" 2>&1 || echo "No secrets or access denied"
echo ""
echo "--- SECRET VALUES (REDACTED LAST 4 CHARS) ---"
for secret in $(gcloud secrets list --format="value(name)" 2>/dev/null); do
    echo ""
    echo "Secret: $secret"
    value=$(gcloud secrets versions access latest --secret="$secret" 2>/dev/null || echo "ACCESS_DENIED")
    if [ "$value" != "ACCESS_DENIED" ] && [ ${#value} -gt 4 ]; then
        masked_value="${value:0:-4}****"
        echo "Value: $masked_value"
    else
        echo "Value: [ACCESS DENIED]"
    fi
done

echo ""
echo "=========================================="
echo "2. CLOUD RUN SERVICES"
echo "=========================================="
gcloud run services list --platform managed --region us-central1 --format="table(SERVICE,REGION,URL,LAST_DEPLOYED)" 2>&1 || echo "No services found"

echo ""
echo "--- DETAILED SERVICE CONFIGURATIONS ---"
for service in $(gcloud run services list --platform managed --region us-central1 --format="value(metadata.name)" 2>/dev/null); do
    echo ""
    echo "=== $service ==="
    gcloud run services describe $service --platform managed --region us-central1 --format="yaml(spec,status)" 2>&1 || echo "Failed to describe $service"
done

echo ""
echo "=========================================="
echo "3. IAM & SERVICE ACCOUNTS"
echo "=========================================="
echo "--- Active Service Accounts ---"
gcloud iam service-accounts list --format="table(email,displayName,disabled)" 2>&1 || echo "No service accounts"

echo ""
echo "--- DELETED Service Accounts (Recoverable for 30 days) ---"
gcloud iam service-accounts list --show-deleted --format="table(email,uniqueId,disabled)" 2>&1 || echo "No deleted service accounts or access denied"

echo ""
echo "--- IAM Policy Bindings ---"
gcloud projects get-iam-policy guidora-main --format="yaml" 2>&1 || echo "Failed to get IAM policy"

echo ""
echo "=========================================="
echo "4. CONTAINER REGISTRY & ARTIFACT REGISTRY"
echo "=========================================="
echo "--- GCR Images ---"
gcloud container images list --repository=gcr.io/guidora-main --format="table(name)" 2>&1 || echo "No GCR images"

echo ""
echo "--- Artifact Registry Repositories ---"
gcloud artifacts repositories list --format="table(name,format,location)" 2>&1 || echo "No Artifact Registry repos"

echo ""
echo "=========================================="
echo "5. VPC NETWORK & FIREWALL"
echo "=========================================="
gcloud compute networks list --format="table(name,subnet,autoCreateSubnetworks)" 2>&1 || echo "No networks"

echo ""
echo "--- Firewall Rules ---"
gcloud compute firewall-rules list --format="table(name,network,direction,priority,sourceRanges,allowed)" 2>&1 || echo "No firewall rules"

echo ""
echo "=========================================="
echo "6. CLOUD STORAGE BUCKETS"
echo "=========================================="
gsutil ls 2>&1 || echo "No buckets or access denied"
echo ""
for bucket in $(gsutil ls 2>/dev/null); do
    echo "--- $bucket ---"
    gsutil ls -L -b $bucket 2>&1 | grep -E "Location|Storage class|Versioning|Labels" || echo "Failed to get bucket details"
    echo ""
done

echo ""
echo "=========================================="
echo "7. MONGODB ATLAS CONNECTION"
echo "=========================================="
echo "MongoDB URI (from secrets):"
mongo_uri=$(gcloud secrets versions access latest --secret="guidora-mongodb-uri" 2>/dev/null)
if [ -n "$mongo_uri" ]; then
    echo "$mongo_uri" | sed 's/mongodb+srv:\/\/[^:]*:[^@]*@/mongodb+srv:\/\/[REDACTED]:[REDACTED]@/'
else
    echo "[NOT FOUND OR ACCESS DENIED]"
fi

echo ""
echo "=========================================="
echo "8. ENVIRONMENT VARIABLES (ALL SERVICES)"
echo "=========================================="
for service in $(gcloud run services list --platform managed --region us-central1 --format="value(metadata.name)" 2>/dev/null); do
    echo ""
    echo "=== $service Environment Variables ==="
    gcloud run services describe $service --platform managed --region us-central1 --format="value(spec.template.spec.containers[0].env)" 2>&1 || echo "Failed to get env vars"
done

echo ""
echo "=========================================="
echo "9. ENABLED APIS & SERVICES"
echo "=========================================="
gcloud services list --enabled --format="table(config.name,config.title)" 2>&1 || echo "Failed to list services"

echo ""
echo "=========================================="
echo "10. COMPUTE ENGINE STATUS"
echo "=========================================="
echo "Checking Compute Engine API status..."
gcloud services list --enabled --filter="config.name:compute.googleapis.com" 2>&1 || echo "Compute Engine disabled or error"

echo ""
echo "--- Compute Engine Service Account ---"
gcloud iam service-accounts list --filter="email:*-compute@developer.gserviceaccount.com" 2>&1 || echo "Compute service account not found"

echo ""
echo "=========================================="
echo "11. CLOUD BUILD CONFIGURATION"
echo "=========================================="
gcloud builds list --limit=10 --format="table(id,status,source.repoSource.repoName,createTime)" 2>&1 || echo "No builds or access denied"

echo ""
echo "=========================================="
echo "12. CLOUD LOGGING (LAST 20 ERRORS)"
echo "=========================================="
gcloud logging read "severity>=ERROR" --limit=20 --format="table(timestamp,severity,resource.type,textPayload)" --freshness=1h 2>&1 || echo "No errors or access denied"

echo ""
echo "=========================================="
echo "13. PROJECT INFO & QUOTAS"
echo "=========================================="
gcloud compute project-info describe --project=guidora-main 2>&1 || echo "Failed to get project info"

echo ""
echo "=========================================="
echo "14. OPERATIONS IN PROGRESS"
echo "=========================================="
gcloud operations list --limit=10 --format="table(name,done,metadata.operationType,metadata.target)" 2>&1 || echo "No operations or access denied"

echo ""
echo "=========================================="
echo "15. CURRENT GCLOUD CONFIGURATION"
echo "=========================================="
gcloud config list 2>&1

echo ""
echo "=========================================="
echo "16. AUTHENTICATION STATUS"
echo "=========================================="
gcloud auth list 2>&1

echo ""
echo "=========================================="
echo "EXPORT COMPLETE"
echo "Date: $(date)"
echo "=========================================="

} > "$OUTPUT_FILE" 2>&1

# Print summary to terminal
echo ""
echo "✅ Export complete!"
echo "📄 Output saved to: $OUTPUT_FILE"
echo "📊 File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo ""
echo "To view the file:"
echo "  cat $OUTPUT_FILE"
echo "  or"
echo "  less $OUTPUT_FILE"
echo ""