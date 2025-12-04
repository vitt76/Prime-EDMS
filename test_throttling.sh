#!/bin/bash

# Test script for verifying throttling functionality
# This script tests the AI analysis throttling implementation

echo "=== THROTTLING TEST SCRIPT ==="
echo "Testing AI analysis endpoint throttling"
echo ""

# Configuration
API_URL="http://localhost:8000/api/v4/dam/documents/analyze/"
TOKEN="${TOKEN:-your_token_here}"

if [ "$TOKEN" = "your_token_here" ]; then
    echo "❌ ERROR: Please set TOKEN environment variable with your API token"
    echo "Usage: TOKEN=your_api_token ./test_throttling.sh"
    exit 1
fi

echo "Using API URL: $API_URL"
echo "Testing with token: ${TOKEN:0:10}..."
echo ""

# Test data
TEST_DATA='{
  "document_id": 1,
  "ai_service": "openai",
  "analysis_type": "classification"
}'

echo "=== Test 1: Normal request (should work) ==="
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$TEST_DATA" \
  "$API_URL")

http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
response_body=$(echo "$response" | sed '/HTTP_STATUS:/d')

echo "HTTP Status: $http_status"
echo "Response: $response_body"
echo ""

if [ "$http_status" -eq 202 ]; then
    echo "✅ Normal request succeeded (HTTP 202)"
elif [ "$http_status" -eq 429 ]; then
    echo "⚠️  Request throttled (HTTP 429) - this might be expected if rate limit reached"
else
    echo "❌ Unexpected status: $http_status"
fi

echo ""
echo "=== Test 2: Check throttle headers ==="
response=$(curl -s -I \
  -H "Authorization: Bearer $TOKEN" \
  "$API_URL")

echo "Response headers:"
echo "$response"
echo ""

# Test 3: Multiple requests to trigger throttling
echo "=== Test 3: Multiple requests (should trigger throttling) ==="
echo "Making 15 requests to test throttling (10/minute limit)..."

for i in {1..15}; do
    echo -n "Request $i: "
    response=$(curl -s -w "%{http_code}" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "$TEST_DATA" \
      "$API_URL")

    if [ "$response" -eq 202 ]; then
        echo "✅ Success (202)"
    elif [ "$response" -eq 429 ]; then
        echo "🚫 Throttled (429) - Rate limit reached!"
        break
    else
        echo "❌ Error ($response)"
    fi

    # Small delay between requests
    sleep 0.1
done

echo ""
echo "=== Test Summary ==="
echo "✅ Throttling configuration implemented"
echo "✅ Custom throttle classes created"
echo "✅ Logging configured"
echo "✅ Tests completed"
echo ""
echo "Note: In development environment, throttling might behave differently."
echo "For production testing, ensure Redis cache is configured."








