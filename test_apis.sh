#!/bin/bash
# TEST SCRIPT - Run after applying SQL fixes

echo "================================"
echo "TESTING PROFILE & PSGC APIs"
echo "================================"

BASE_URL="http://localhost:8000"

echo ""
echo "1. Testing PSGC Regions (NO AUTH)..."
curl -s "$BASE_URL/api/regions" | jq '.success, .result | length'

echo ""
echo "2. Testing PSGC Provinces for NCR..."
curl -s "$BASE_URL/api/provinces?region_code=130000000" | jq '.success, .result | length'

echo ""
echo "3. Testing PSGC Cities for Metro Manila..."
curl -s "$BASE_URL/api/cities?province_code=133900000" | jq '.success, .result | length'

echo ""
echo "4. Testing PSGC Barangays for Manila..."
curl -s "$BASE_URL/api/barangays?city_code=133901000" | jq '.success, .result | length'

echo ""
echo "5. Testing Buyer Profile (REQUIRES AUTH TOKEN)..."
echo "   Replace YOUR_TOKEN with actual token:"
echo "   curl -H 'Authorization: Bearer YOUR_TOKEN' $BASE_URL/api/v1/buyer/profile"

echo ""
echo "================================"
echo "EXPECTED RESULTS:"
echo "- All should return: true"
echo "- Regions: 17"
echo "- Provinces: 1"
echo "- Cities: 17"
echo "- Barangays: 16"
echo "================================"
