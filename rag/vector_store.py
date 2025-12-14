"""Vector store implementation using ChromaDB for Versailles knowledge base."""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document


class VersaillesVectorStore:
    """Manages the vector store for Versailles knowledge base."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "versailles_knowledge",
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Create persist directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Initialize or get collection
        self.vector_store = None
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initialize the vector store with LangChain Chroma."""
        try:
            self.vector_store = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise

    def load_versailles_data(
        self,
        jsonl_path: str = "data/versailles_semantic_complete_20250813_204248.jsonl",
    ):
        """
        Load Versailles data from JSONL file into vector store.

        Args:
            jsonl_path: Path to the JSONL file
        """
        if not os.path.exists(jsonl_path):
            raise FileNotFoundError(f"Data file not found: {jsonl_path}")

        documents = []

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())

                    # Extract content
                    url = data.get("url", "")
                    title = data.get("title", "")
                    content_blocks = data.get("content", [])

                    # Process content blocks
                    text_content = self._extract_text_from_content(content_blocks)

                    if text_content:
                        # Create document
                        doc = Document(
                            page_content=text_content,
                            metadata={
                                "url": url,
                                "title": title,
                                "source": "versailles_official",
                                "line_number": line_num,
                            },
                        )
                        documents.append(doc)

                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    continue

        if documents:
            print(f"Loading {len(documents)} documents into vector store...")
            self.vector_store.add_documents(documents)
            print("Documents loaded successfully!")
        else:
            print("No documents to load.")

    def _extract_text_from_content(self, content_blocks: List[Dict]) -> str:
        """
        Extract text from content blocks.

        Args:
            content_blocks: List of content block dictionaries

        Returns:
            Extracted text as string
        """
        texts = []

        for block in content_blocks:
            block_type = block.get("type", "")

            if block_type == "text":
                text = block.get("text", "")
                if text:
                    texts.append(text)

            elif block_type == "heading":
                heading_text = block.get("text", "")
                if heading_text:
                    texts.append(f"\n## {heading_text}\n")

            elif block_type == "section":
                heading = block.get("heading", {})
                if heading:
                    heading_text = heading.get("text", "")
                    if heading_text:
                        texts.append(f"\n## {heading_text}\n")

                section_content = block.get("content", [])
                if section_content:
                    section_text = self._extract_text_from_content(section_content)
                    texts.append(section_text)

            elif block_type == "list":
                items = block.get("items", [])
                for item in items:
                    texts.append(f"- {item}")

            elif block_type == "content_block":
                items = block.get("items", [])
                if items:
                    block_text = self._extract_text_from_content(items)
                    texts.append(block_text)

        return "\n".join(texts)

    def search(
        self, query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search the vector store.

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of relevant documents
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        try:
            results = self.vector_store.similarity_search(
                query=query, k=k, filter=filter_dict
            )
            return results
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []

    def search_with_score(
        self, query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Search the vector store with relevance scores.

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of tuples (document, score)
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        try:
            results = self.vector_store.similarity_search_with_score(
                query=query, k=k, filter=filter_dict
            )
            return results
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []

    def reset(self):
        """Reset the vector store (delete all data)."""
        try:
            self.client.reset()
            self._initialize_vector_store()
            print("Vector store reset successfully!")
        except Exception as e:
            print(f"Error resetting vector store: {e}")

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            collection = self.client.get_collection(self.collection_name)
            return collection.count()
        except Exception:
            return 0


# Singleton instance
_vector_store_instance = None


def get_vector_store() -> VersaillesVectorStore:
    """Get or create the singleton vector store instance."""
    global _vector_store_instance

    if _vector_store_instance is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "versailles_knowledge")
        _vector_store_instance = VersaillesVectorStore(
            persist_directory=persist_dir, collection_name=collection_name
        )

    return _vector_store_instance
