#!/bin/bash

set -e

echo "Running terraform fmt..."
terraform fmt -check

echo "Running terraform validate..."
terraform validate

echo "Running terraform plan..."
terraform plan -out=tfplan

echo "Terraform validation successful"