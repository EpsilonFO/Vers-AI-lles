"""Retriever implementation for Versailles knowledge base."""

from typing import List, Dict, Any, Optional
from langchain.docstore.document import Document
from .vector_store import get_vector_store


class VersaillesRetriever:
    """Retriever for Versailles knowledge base with enhanced search capabilities."""

    def __init__(self, k: int = 5, score_threshold: float = 0.5):
        """
        Initialize the retriever.

        Args:
            k: Number of documents to retrieve
            score_threshold: Minimum relevance score threshold
        """
        self.k = k
        self.score_threshold = score_threshold
        self.vector_store = get_vector_store()

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            k: Number of documents to retrieve (overrides default)
            filter_dict: Optional metadata filters

        Returns:
            List of relevant documents
        """
        k = k or self.k

        try:
            results = self.vector_store.search_with_score(
                query=query, k=k, filter_dict=filter_dict
            )

            # Filter by score threshold
            filtered_results = [
                doc for doc, score in results if score >= self.score_threshold
            ]

            return filtered_results

        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def retrieve_with_context(self, query: str, k: Optional[int] = None) -> str:
        """
        Retrieve documents and format them as context for LLM.

        Args:
            query: Search query
            k: Number of documents to retrieve

        Returns:
            Formatted context string
        """
        documents = self.retrieve(query, k)

        if not documents:
            return "Aucune information trouvée dans la base de connaissances."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            title = doc.metadata.get("title", "Sans titre")
            url = doc.metadata.get("url", "")
            content = doc.page_content[:500]  # Limit content length

            context_parts.append(
                f"[Source {i}] {title}\n" f"URL: {url}\n" f"Contenu: {content}...\n"
            )

        return "\n---\n".join(context_parts)

    def search_by_topic(self, topic: str) -> List[Document]:
        """
        Search for documents related to a specific topic.

        Args:
            topic: Topic to search for

        Returns:
            List of relevant documents
        """
        # Enhanced query for topic search
        enhanced_query = f"Information sur {topic} au château de Versailles"
        return self.retrieve(enhanced_query)

    def search_practical_info(self, info_type: str) -> List[Document]:
        """
        Search for practical information (hours, tickets, access, etc.).

        Args:
            info_type: Type of practical information

        Returns:
            List of relevant documents
        """
        practical_queries = {
            "horaires": "horaires ouverture château Versailles",
            "billets": "billets tarifs prix réservation Versailles",
            "acces": "accès transport comment venir Versailles",
            "visites": "visites guidées parcours Versailles",
            "jardins": "jardins grandes eaux musicales Versailles",
            "trianon": "domaine Trianon petit grand hameau reine",
            "restaurants": "restaurants restauration manger Versailles",
            "parking": "parking stationnement voiture Versailles",
        }

        query = practical_queries.get(info_type.lower(), info_type)
        return self.retrieve(query)

    def get_opening_hours_info(self) -> str:
        """Get information about opening hours."""
        docs = self.search_practical_info("horaires")
        return self.retrieve_with_context("horaires ouverture Versailles")

    def get_ticket_info(self) -> str:
        """Get information about tickets and pricing."""
        docs = self.search_practical_info("billets")
        return self.retrieve_with_context("billets tarifs prix Versailles")

    def get_access_info(self) -> str:
        """Get information about access and transportation."""
        docs = self.search_practical_info("acces")
        return self.retrieve_with_context("accès transport Versailles")


# Singleton instance
_retriever_instance = None


def get_retriever() -> VersaillesRetriever:
    """Get or create the singleton retriever instance."""
    global _retriever_instance

    if _retriever_instance is None:
        _retriever_instance = VersaillesRetriever()

    return _retriever_instance
