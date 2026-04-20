#!/bin/bash

echo "Checking pipeline structure..."

if ! grep -q "security" "$1"; then
  echo "Missing security stage"
  exit 1
fi

echo "Pipeline validation passed"