"""Script to initialize the ChromaDB vector store with Versailles data."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rag.vector_store import get_vector_store
from dotenv import load_dotenv


def initialize_vector_store():
    """Initialize the vector store with Versailles data."""
    # Load environment variables
    load_dotenv()

    print("Initializing Versailles knowledge base...")
    print("-" * 50)

    # Get vector store instance
    vector_store = get_vector_store()

    # Check if already populated
    count = vector_store.get_collection_count()
    if count > 0:
        print(f"Vector store already contains {count} documents.")
        response = input("Do you want to reset and reload? (y/n): ")
        if response.lower() == "y":
            print("Resetting vector store...")
            vector_store.reset()
        else:
            print("Keeping existing data.")
            return

    # Load data
    data_path = "data/versailles_semantic_complete_20250813_204248.jsonl"

    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    print(f"Loading data from {data_path}...")
    vector_store.load_versailles_data(data_path)

    # Verify
    final_count = vector_store.get_collection_count()
    print("-" * 50)
    print(f"✓ Vector store initialized successfully!")
    print(f"✓ Total documents: {final_count}")
    print("-" * 50)

    # Test search
    print("\nTesting search functionality...")
    test_query = "horaires d'ouverture du château"
    results = vector_store.search(test_query, k=3)

    print(f"\nTest query: '{test_query}'")
    print(f"Found {len(results)} results:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.metadata.get('title', 'No title')}")
        print(f"   Content preview: {doc.page_content[:150]}...")


if __name__ == "__main__":
    initialize_vector_store()
