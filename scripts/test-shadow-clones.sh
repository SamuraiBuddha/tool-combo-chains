#!/bin/bash

# Test script for Memory Gateway Shadow Clone workflow
# Prerequisites: 
# - VLLM running on port 8000
# - n8n running with imported workflow
# - Hybrid memory MCP running on port 3002

echo "🥷 Shadow Clone Memory Gateway Test Suite"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if services are running
echo -n "Checking VLLM... "
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Please start VLLM first${NC}"
    echo "Run: vllm serve mistralai/Mistral-7B-Instruct-v0.3 --port 8000"
    exit 1
fi

echo -n "Checking n8n... "
if curl -s http://localhost:5678 > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Please start n8n first${NC}"
    exit 1
fi

# Test 1: Create new entity
echo -e "\n📝 Test 1: Creating new entity with shadow clones..."
START_TIME=$(date +%s%N)

curl -X POST http://localhost:5678/webhook/memory-shadow-clone \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Shadow_Clone_Test_'$(date +%s)'",
    "entity_type": "Test_Entity",
    "content": "This entity was created by shadow clones working in parallel. Clone 1 checked existence, Clone 2 assigned priority, Clone 3 mapped relationships.",
    "metadata": {
      "test_run": true,
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'"
    }
  }' 2>/dev/null | jq .

END_TIME=$(date +%s%N)
ELAPSED=$((($END_TIME - $START_TIME) / 1000000))
echo -e "⏱️  Execution time: ${GREEN}${ELAPSED}ms${NC}"

# Test 2: Update existing entity
echo -e "\n📝 Test 2: Updating existing entity with shadow clones..."
START_TIME=$(date +%s%N)

curl -X POST http://localhost:5678/webhook/memory-shadow-clone \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Shadow_Clone_Complete_Architecture_2025",
    "entity_type": "Architecture_Complete",
    "content": "Testing shadow clone update operation. This should add an observation rather than creating a new entity.",
    "metadata": {
      "test_update": true
    }
  }' 2>/dev/null | jq .

END_TIME=$(date +%s%N)
ELAPSED=$((($END_TIME - $START_TIME) / 1000000))
echo -e "⏱️  Execution time: ${GREEN}${ELAPSED}ms${NC}"

# Test 3: Parallel performance test
echo -e "\n📝 Test 3: Stress test - 5 parallel requests..."
START_TIME=$(date +%s%N)

for i in {1..5}; do
  curl -X POST http://localhost:5678/webhook/memory-shadow-clone \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Parallel_Test_'$i'_'$(date +%s%N)'",
      "entity_type": "Performance_Test",
      "content": "Parallel request number '$i' to test shadow clone scalability",
      "metadata": {"request_number": '$i'}
    }' 2>/dev/null &
done

wait
END_TIME=$(date +%s%N)
ELAPSED=$((($END_TIME - $START_TIME) / 1000000))
echo -e "⏱️  Total time for 5 parallel requests: ${GREEN}${ELAPSED}ms${NC}"
echo -e "Average per request: ${GREEN}$((ELAPSED / 5))ms${NC}"

echo -e "\n✅ Shadow Clone tests complete!"
echo -e "\nExpected performance:"
echo -e "- Single operation: ~500ms (vs 3000ms sequential)"
echo -e "- Parallel operations: Should scale linearly"
echo -e "\n🎯 If times are significantly higher, check:"
echo -e "- VLLM model is loaded and warm"
echo -e "- n8n has sufficient resources"
echo -e "- Network latency between services"
