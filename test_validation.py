#!/usr/bin/env python
"""Test validation endpoints"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/drone"

# Test 1: update-tree with invalid part_name
print("=" * 60)
print("TEST 1: update-tree with INVALID part_name")
print("=" * 60)
response = requests.post(
    f"{BASE_URL}/sideview/update-tree",
    data={
        "farmer_id": "1",
        "survey_id": "1",
        "tree_number": "1",
        "part_name": "INVALID_PART",
        "status": "healthy",
        "confidence": "0.95"
    }
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 2: update-tree with invalid status
print("=" * 60)
print("TEST 2: update-tree with INVALID status")
print("=" * 60)
response = requests.post(
    f"{BASE_URL}/sideview/update-tree",
    data={
        "farmer_id": "1",
        "survey_id": "1",
        "tree_number": "1",
        "part_name": "stem",
        "status": "INVALID_STATUS",
        "confidence": "0.95"
    }
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 3: update-tree with invalid confidence (out of range)
print("=" * 60)
print("TEST 3: update-tree with INVALID confidence (>1.0)")
print("=" * 60)
response = requests.post(
    f"{BASE_URL}/sideview/update-tree",
    data={
        "farmer_id": "1",
        "survey_id": "1",
        "tree_number": "1",
        "part_name": "stem",
        "status": "healthy",
        "confidence": "1.5"
    }
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 4: update-tree with negative tree_number
print("=" * 60)
print("TEST 4: update-tree with NEGATIVE tree_number")
print("=" * 60)
response = requests.post(
    f"{BASE_URL}/sideview/update-tree",
    data={
        "farmer_id": "1",
        "survey_id": "1",
        "tree_number": "-1",
        "part_name": "stem",
        "status": "healthy",
        "confidence": "0.95"
    }
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 5: mock endpoint with invalid part_name
print("=" * 60)
print("TEST 5: mock endpoint with INVALID part_name")
print("=" * 60)
response = requests.post(
    f"{BASE_URL}/sideview/mock",
    data={
        "farmer_id": "1",
        "survey_id": "1",
        "tree_number": "1",
        "status": "healthy",
        "confidence": "0.95",
        "part_name": "ROOT"
    }
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 6: mock-batch with invalid part_name in batch
print("=" * 60)
print("TEST 6: mock-batch with INVALID part_name in batch")
print("=" * 60)
trees_data = [
    {"tree_number": 1, "part_name": "stem", "status": "healthy", "confidence": 0.95},
    {"tree_number": 2, "part_name": "INVALID", "status": "healthy", "confidence": 0.90},
]
response = requests.post(
    f"{BASE_URL}/sideview/mock-batch",
    data={
        "farmer_id": "1",
        "survey_id": "1",
        "trees_json": json.dumps(trees_data)
    }
)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(json.loads(response.text), indent=2)}\n")

# Test 7: mock-batch with invalid confidence in batch
print("=" * 60)
print("TEST 7: mock-batch with INVALID confidence in batch")
print("=" * 60)
trees_data = [
    {"tree_number": 1, "part_name": "stem", "status": "healthy", "confidence": 0.95},
    {"tree_number": 2, "part_name": "bud", "status": "healthy", "confidence": 2.0},
]
response = requests.post(
    f"{BASE_URL}/sideview/mock-batch",
    data={
        "farmer_id": "1",
        "survey_id": "1",
        "trees_json": json.dumps(trees_data)
    }
)
print(f"Status Code: {response.status_code}")
response_data = json.loads(response.text)
print(f"Results: {json.dumps(response_data.get('results', []), indent=2)}\n")

# Test 8: Valid mock endpoint
print("=" * 60)
print("TEST 8: mock endpoint with VALID inputs")
print("=" * 60)
response = requests.post(
    f"{BASE_URL}/sideview/mock",
    data={
        "farmer_id": "1",
        "survey_id": "1",
        "tree_number": "1",
        "status": "healthy",
        "confidence": "0.95",
        "part_name": "stem"
    }
)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✓ PASSED - Valid input accepted")
else:
    print(f"Response: {response.text}")
