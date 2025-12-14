"""Setup script for Versailles Visit Planning Agent."""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_python_version():
    """Check if Python version is 3.9+."""
    print_header("Checking Python Version")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False

    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_redis():
    """Check if Redis is running."""
    print_header("Checking Redis")

    try:
        import redis

        r = redis.Redis(host="localhost", port=6379)
        r.ping()
        print("✓ Redis is running")
        return True
    except Exception as e:
        print("❌ Redis is not running or not accessible")
        print(f"   Error: {e}")
        print("\n   Please start Redis:")
        print("   - Windows: redis-server.exe")
        print("   - Linux/Mac: redis-server")
        print("   - Docker: docker run -d -p 6379:6379 redis:7.0")
        return False


def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")

    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_env_file():
    """Check if .env file exists."""
    print_header("Checking Environment Configuration")

    env_path = Path(".env")

    if not env_path.exists():
        print("⚠️  .env file not found")
        print("\n   Please create a .env file with your API keys:")
        print("   - MISTRAL_API_KEY=your_key")
        print("   - OPENWEATHER_API_KEY=your_key")
        print("   - REDIS_HOST=localhost")
        print("   - REDIS_PORT=6379")
        return False

    # Check for required keys
    with open(env_path, "r") as f:
        content = f.read()

    required_keys = ["MISTRAL_API_KEY", "OPENWEATHER_API_KEY"]
    missing_keys = [key for key in required_keys if key not in content]

    if missing_keys:
        print(f"⚠️  Missing required keys in .env: {', '.join(missing_keys)}")
        return False

    print("✓ .env file configured")
    return True


def initialize_vector_store():
    """Initialize ChromaDB vector store."""
    print_header("Initializing Vector Store")

    data_file = Path("data/versailles_semantic_complete_20250813_204248.jsonl")

    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return False

    print("Initializing ChromaDB with Versailles data...")
    print("This may take a few minutes...")

    try:
        # Import here to avoid issues if dependencies not installed
        from rag.vector_store import get_vector_store

        vector_store = get_vector_store()
        count = vector_store.get_collection_count()

        if count > 0:
            print(f"✓ Vector store already initialized ({count} documents)")
            response = input("\n   Reinitialize? (y/n): ")
            if response.lower() != "y":
                return True
            vector_store.reset()

        vector_store.load_versailles_data(str(data_file))
        final_count = vector_store.get_collection_count()
        print(f"✓ Vector store initialized with {final_count} documents")
        return True

    except Exception as e:
        print(f"❌ Failed to initialize vector store: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print_header("Creating Directories")

    directories = ["chroma_db", "logs"]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created {directory}/")

    return True


def run_tests():
    """Run basic tests."""
    print_header("Running Tests")

    try:
        print("Running pytest...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("⚠️  Some tests failed")
            print(result.stdout)
            return False

    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        return False


def main():
    """Main setup function."""
    print("\n" + "=" * 70)
    print("  🏰 Versailles Visit Planning Agent - Setup")
    print("=" * 70)

    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Environment Config", check_env_file),
        ("Redis", check_redis),
        ("Directories", create_directories),
        ("Vector Store", initialize_vector_store),
        ("Tests", run_tests),
    ]

    results = {}

    for step_name, step_func in steps:
        try:
            results[step_name] = step_func()
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            results[step_name] = False

    # Summary
    print_header("Setup Summary")

    for step_name, success in results.items():
        status = "✓" if success else "❌"
        print(f"{status} {step_name}")

    all_success = all(results.values())

    if all_success:
        print("\n" + "=" * 70)
        print("  ✅ Setup completed successfully!")
        print("=" * 70)
        print("\n  Next steps:")
        print("  1. Start the FastAPI server:")
        print("     python app/app.py")
        print("\n  2. Or start the MCP server:")
        print("     python mcp_server.py")
        print("\n  3. Access the API docs:")
        print("     http://localhost:8000/docs")
        print("=" * 70 + "\n")
    else:
        print("\n" + "=" * 70)
        print("  ⚠️  Setup completed with warnings")
        print("=" * 70)
        print("\n  Please fix the issues above and run setup again.")
        print("=" * 70 + "\n")

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
