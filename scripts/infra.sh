#!/bin/bash

# Infrastructure Readiness Check Script

echo "🔍 Starting Infrastructure Readiness Check..."

# 1. Verify service directories and package.json
SERVICES=("deafauth" "pinksync" "fibonrose")
for service in "${SERVICES[@]}"; do
    if [ -f "services/$service/package.json" ]; then
        echo "✅ $service service configured"
    else
        echo "❌ $service service NOT configured (missing services/$service/package.json)"
        exit 1
    fi
done

# 2. Verify Terraform files
TF_FILES=("main.tf" "variables.tf" "outputs.tf" "networking.tf" "deafauth.tf" "pinksync.tf" "fibonrose.tf" "monitoring.tf" "cicd.tf" "billing.tf")
for tf_file in "${TF_FILES[@]}"; do
    if [ -f "terraform/$tf_file" ]; then
        echo "✅ Terraform file $tf_file present"
    else
        echo "❌ Terraform file $tf_file MISSING"
        exit 1
    fi
done

# 3. Verify environment files
ENV_FILES=("dev.tfvars" "staging.tfvars" "production.tfvars")
for env_file in "${ENV_FILES[@]}"; do
    if [ -f "environments/$env_file" ]; then
        echo "✅ Environment file $env_file present"
    else
        echo "❌ Environment file $env_file MISSING"
        exit 1
    fi
done

echo "✅ ALL INFRASTRUCTURE CHECKS PASSED"
exit 0
