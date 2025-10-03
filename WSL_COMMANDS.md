# 🚀 WSL Commands Guide - Les 4 MousquetAIres

Complete guide for launching services and running tests in WSL (Windows Subsystem for Linux).

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Launch Services](#launch-services)
4. [Run Tests](#run-tests)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Check WSL Installation
```bash
wsl --version
```

### Check Python Installation
```bash
python3 --version  # Should be 3.9+
pip3 --version
```

### Navigate to Project Directory
```bash
cd /mnt/c/Users/sarah/Desktop/les_4_MousquetAIres
```

---

## Initial Setup

### 1. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv path)
which python3
```

### 2. Install Dependencies
```bash
# Install all required packages
pip3 install -r requirements.txt

# Verify installation
pip3 list
```

### 3. Set Up Environment Variables
```bash
# Create .env file if it doesn't exist
cat > .env << 'EOF'
# Mistral AI API Key (Required)
MISTRAL_API_KEY=your_mistral_api_key_here

# OpenWeatherMap API Key (Required for weather)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=versailles_knowledge

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
EOF

# Edit the file to add your actual API keys
nano .env
# Or use vim: vim .env
```

### 4. Install and Start Redis

#### Option A: Using Docker (Recommended)
```bash
# Install Docker if not already installed
# Follow: https://docs.docker.com/engine/install/ubuntu/

# Start Redis container
docker run -d --name redis-versailles -p 6379:6379 redis:7.0

# Verify Redis is running
docker ps | grep redis

# Test Redis connection
docker exec -it redis-versailles redis-cli ping
# Should return: PONG
```

#### Option B: Native Installation
```bash
# Install Redis
sudo apt-get update
sudo apt-get install redis-server -y

# Start Redis service
sudo service redis-server start

# Check Redis status
sudo service redis-server status

# Test connection
redis-cli ping
# Should return: PONG
```

### 5. Initialize Vector Store (First Time Only)
```bash
# This loads 300+ Versailles documents into ChromaDB
# Takes about 2-3 minutes
python3 rag/initialize_db.py

# Expected output:
# ✓ Loaded X documents
# ✓ Created embeddings
# ✓ Stored in ChromaDB
```

---

## Launch Services

### Option 1: FastAPI Application (Main Service)

#### Start the Server
```bash
# Method 1: Using Python directly
python3 app/app.py

# Method 2: Using uvicorn
uvicorn app.app:app --reload --host 0.0.0.0 --port 8000

# Method 3: With custom port
uvicorn app.app:app --reload --host 0.0.0.0 --port 8080
```

#### Access the API
```bash
# From WSL - Test health endpoint
curl http://localhost:8000/health

# From Windows browser, open:
# http://localhost:8000          - API root
# http://localhost:8000/docs     - Interactive API documentation
# http://localhost:8000/redoc    - Alternative API documentation
```

#### Test the Chat Endpoint
```bash
# Simple test
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bonjour, quels sont les horaires d'\''ouverture ?",
    "session_id": "test123"
  }'

# Complex reservation test
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Je veux réserver pour 2 personnes le 15 juin 2025",
    "session_id": "test123"
  }'

# Get reservation status
curl http://localhost:8000/reservation/test123

# Reset session
curl -X DELETE http://localhost:8000/session/test123
```

#### Stop the Server
```bash
# Press Ctrl+C in the terminal where server is running
```

---

### Option 2: MCP Server (Model Context Protocol)

#### Start MCP Server
```bash
# Run MCP server (uses stdio)
python3 mcp_server.py

# Note: MCP server runs on stdio and is meant to be used with
# MCP clients like Claude Desktop or Cline
```

#### Configure for Claude Desktop
```bash
# Edit Claude Desktop config (on Windows)
# File location: %APPDATA%\Claude\claude_desktop_config.json

# Add this configuration:
{
  "mcpServers": {
    "versailles-agent": {
      "command": "wsl",
      "args": [
        "python3",
        "/mnt/c/Users/sarah/Desktop/les_4_MousquetAIres/mcp_server.py"
      ],
      "env": {
        "MISTRAL_API_KEY": "your_key_here",
        "OPENWEATHER_API_KEY": "your_key_here"
      }
    }
  }
}
```

---

### Option 3: Docker Compose (All Services)

#### Start All Services
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f fastapi-app
docker-compose logs -f redis
```

#### Check Service Status
```bash
# List running containers
docker-compose ps

# Check if services are healthy
curl http://localhost:8000/health
```

#### Stop All Services
```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Run Tests

### Automated Test Scripts

#### Run Bash Test Script
```bash
# Make script executable
chmod +x test_implementation.sh

# Run all tests
bash test_implementation.sh

# Expected output:
# ✓ Multiple test categories
# ✓ Pass/Fail summary
```

#### Run Python Test Script
```bash
# Run Python test implementation
python3 test_implementation.py

# Expected output:
# ✓ Test results for each component
```

---

### Manual Testing Commands

#### 1. Environment Tests
```bash
# Check Python version
python3 --version

# Check pip
pip3 --version

# Check installed packages
pip3 list | grep -E "langchain|fastapi|chromadb|redis"
```

#### 2. Import Tests
```bash
# Test all critical imports
python3 << 'EOF'
print("Testing imports...")
try:
    import agents.langgraph_flow
    print("✓ langgraph_flow")
    import agents.agent_multistep
    print("✓ agent_multistep")
    from llm.reservation_memory import ReservationPlan
    print("✓ reservation_memory")
    from rag.vector_store import VersaillesVectorStore
    print("✓ vector_store")
    import app.app
    print("✓ app")
    print("\n✅ All imports successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
EOF
```

#### 3. Model Tests
```bash
# Test ReservationPlan model
python3 << 'EOF'
from llm.reservation_memory import ReservationPlan

rp = ReservationPlan()
print(f"Missing slots: {rp.get_missing_slots()}")
print(f"Completion: {rp.get_completion_percentage()}%")
print(f"Is complete: {rp.is_complete()}")

# Fill some data
rp.date = "2025-06-15"
rp.participants = 2
rp.type_billet = "passeport"

print(f"\nAfter filling 3 fields:")
print(f"Completion: {rp.get_completion_percentage()}%")
print(f"Missing: {rp.get_missing_slots()}")
print("\n✓ ReservationPlan works correctly")
EOF
```

#### 4. Tool Tests
```bash
# Test Google Maps tool
python3 << 'EOF'
from tools.google_maps_tool import google_maps_route

result = google_maps_route.invoke({
    "origin": "Paris Gare de Lyon",
    "destination": "Château de Versailles",
    "mode": "transit"
})
print(result)
print("\n✓ Google Maps tool works")
EOF

# Test Weather tool
python3 << 'EOF'
from tools.get_weather import get_weather

result = get_weather.invoke({"city": "Versailles"})
print(result)
print("\n✓ Weather tool works")
EOF

# Test Parking Info
python3 << 'EOF'
from tools.parking_restaurants import get_parking_info

result = get_parking_info.invoke({"location": "Versailles"})
print(result)
print("\n✓ Parking info works")
EOF

# Test Restaurant Finder
python3 << 'EOF'
from tools.parking_restaurants import find_restaurants

result = find_restaurants.invoke({
    "location": "Versailles",
    "cuisine": "français",
    "budget": "moyen"
})
print(result)
print("\n✓ Restaurant finder works")
EOF
```

#### 5. Memory Tests
```bash
# Test session save/load
python3 << 'EOF'
from memory.memory import save_session, load_session

# Save test session
test_data = {
    "chat_history": "User: Hello\nAgent: Hi!",
    "reservation_plan": {"date": "2025-06-15", "participants": 2}
}
save_session("test_session", test_data)
print("✓ Session saved")

# Load session
loaded = load_session("test_session")
print(f"✓ Session loaded")
print(f"  Chat history: {loaded.get('chat_history')}")
print(f"  Reservation: {loaded.get('reservation_plan')}")
EOF
```

#### 6. LangGraph Routing Tests
```bash
# Test routing logic
python3 << 'EOF'
from agents.langgraph_flow import route_input, State

# Test agent routing (complex query)
agent_state = State(
    input_text="Je veux réserver un billet pour Versailles",
    response="",
    session_id="test"
)
route = route_input(agent_state)
print(f"Complex query routes to: {route}")
assert route == "Agent_Response", "Should route to Agent"

# Test LLM routing (simple query)
llm_state = State(
    input_text="Bonjour, comment allez-vous ?",
    response="",
    session_id="test"
)
route = route_input(llm_state)
print(f"Simple query routes to: {route}")
assert route == "LLM_Response", "Should route to LLM"

print("\n✓ Routing logic works correctly")
EOF
```

#### 7. Syntax Validation
```bash
# Check Python syntax for all main files
echo "Checking syntax..."
python3 -m py_compile agents/langgraph_flow.py && echo "✓ langgraph_flow.py"
python3 -m py_compile agents/agent_multistep.py && echo "✓ agent_multistep.py"
python3 -m py_compile app/app.py && echo "✓ app.py"
python3 -m py_compile mcp_server.py && echo "✓ mcp_server.py"
python3 -m py_compile llm/reservation_memory.py && echo "✓ reservation_memory.py"
echo "✅ All syntax checks passed"
```

#### 8. Redis Connection Test
```bash
# Test Redis connection
python3 << 'EOF'
import redis
import os

try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True
    )
    r.ping()
    print("✓ Redis is running and accessible")
    
    # Test set/get
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"✓ Redis read/write works: {value}")
except Exception as e:
    print(f"⚠ Redis not available: {e}")
    print("  (Agent will use fallback in-memory storage)")
EOF
```

---

### PyTest Tests

#### Run All Tests
```bash
# Run all pytest tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

#### Run Specific Test Files
```bash
# Test agent
pytest tests/test_agent_multistep.py -v

# Test app
pytest tests/test_app.py -v

# Test LangGraph flow
pytest tests/test_langgraph_flow.py -v

# Test memory
pytest tests/test_memory.py -v

# Test tools
pytest tests/test_tools.py -v
```

#### Run Specific Test Functions
```bash
# Run a specific test
pytest tests/test_app.py::test_set_get_redis -v

# Run tests matching a pattern
pytest -k "redis" -v
```

---

### Integration Tests

#### Full End-to-End Test
```bash
# Start services in background
python3 app/app.py &
APP_PID=$!

# Wait for server to start
sleep 5

# Run integration tests
echo "Testing chat endpoint..."
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Quels sont les horaires ?", "session_id": "integration_test"}'

echo -e "\n\nTesting reservation endpoint..."
curl http://localhost:8000/reservation/integration_test

echo -e "\n\nTesting session reset..."
curl -X DELETE http://localhost:8000/session/integration_test

# Stop server
kill $APP_PID

echo -e "\n✅ Integration tests completed"
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Redis Connection Failed
```bash
# Check if Redis is running
sudo service redis-server status

# Or for Docker
docker ps | grep redis

# Restart Redis
sudo service redis-server restart

# Or for Docker
docker restart redis-versailles
```

#### 2. Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or use a different port
uvicorn app.app:app --port 8080
```

#### 3. Import Errors
```bash
# Ensure you're in the project root
pwd
# Should show: /mnt/c/Users/sarah/Desktop/les_4_MousquetAIres

# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"
```

#### 4. Missing API Keys
```bash
# Check if .env file exists
ls -la .env

# View environment variables (without showing values)
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

keys = ['MISTRAL_API_KEY', 'OPENWEATHER_API_KEY']
for key in keys:
    value = os.getenv(key)
    if value:
        print(f"✓ {key} is set")
    else:
        print(f"✗ {key} is missing")
EOF
```

#### 5. ChromaDB Errors
```bash
# Reinstall ChromaDB
pip3 install chromadb sentence-transformers --force-reinstall

# Clear and reinitialize
rm -rf chroma_db/
python3 rag/initialize_db.py
```

#### 6. Permission Errors
```bash
# Fix file permissions
chmod +x test_implementation.sh
chmod -R 755 .

# Fix ownership (if needed)
sudo chown -R $USER:$USER .
```

---

## Quick Reference Commands

### Start Everything
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Start Redis (if not running)
docker start redis-versailles
# OR
sudo service redis-server start

# 3. Start FastAPI server
python3 app/app.py
```

### Run All Tests
```bash
# Quick test
bash test_implementation.sh

# Full pytest suite
pytest -v

# With coverage
pytest --cov=. --cov-report=html
```

### Stop Everything
```bash
# Stop FastAPI (Ctrl+C in terminal)

# Stop Redis
docker stop redis-versailles
# OR
sudo service redis-server stop

# Deactivate virtual environment
deactivate
```

---

## Performance Monitoring

### Monitor Server Logs
```bash
# Watch logs in real-time
tail -f app.log

# Monitor with timestamps
python3 app/app.py 2>&1 | ts '[%Y-%m-%d %H:%M:%S]'
```

### Monitor Redis
```bash
# Monitor Redis commands
redis-cli monitor

# Check Redis stats
redis-cli info stats

# Check memory usage
redis-cli info memory
```

### Monitor System Resources
```bash
# CPU and memory usage
htop

# Or use top
top

# Disk usage
df -h

# Check specific process
ps aux | grep python3
```

---

## Additional Resources

- **README.md**: Complete project documentation
- **QUICKSTART.md**: 5-minute quick start guide
- **TESTING_GUIDE.md**: Detailed testing instructions
- **TODO.md**: Implementation status and roadmap

---

**Happy Testing! 🏰**
