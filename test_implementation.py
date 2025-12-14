#!/usr/bin/env python3
"""
Comprehensive test script for Versailles Agent
Run in WSL: python3 test_implementation.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Test results
passed = 0
failed = 0
tests = []


def test(name, func):
    """Run a test and track results."""
    global passed, failed
    try:
        func()
        print(f"✓ {name}")
        passed += 1
        tests.append((name, True, None))
        return True
    except Exception as e:
        print(f"✗ {name}: {str(e)}")
        failed += 1
        tests.append((name, False, str(e)))
        return False


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def main():
    """Run all tests."""
    print_header("🏰 Versailles Agent - Critical Path Tests")

    # ========================================================================
    # 1. IMPORT TESTS
    # ========================================================================
    print("\n1. Import Tests")
    print("-" * 70)

    test("Import langgraph_flow", lambda: __import__("agents.langgraph_flow"))
    test("Import agent_multistep", lambda: __import__("agents.agent_multistep"))
    test("Import app", lambda: __import__("app.app"))

    # ========================================================================
    # 2. MODEL TESTS
    # ========================================================================
    print("\n2. Model Tests")
    print("-" * 70)

    def test_reservation_plan():
        from llm.reservation_memory import ReservationPlan

        rp = ReservationPlan()
        assert len(rp.get_missing_slots()) == 4, "Should have 4 missing required slots"
        assert rp.get_completion_percentage() == 0.0, "Should be 0% complete"
        assert not rp.is_complete(), "Should not be complete"

    test("ReservationPlan creation and methods", test_reservation_plan)

    def test_reservation_state():
        from llm.reservation_memory import ReservationState

        rs = ReservationState(session_id="test123")
        assert rs.session_id == "test123"
        rs.add_message("user", "Hello")
        assert len(rs.conversation_history) == 1

    test("ReservationState creation and methods", test_reservation_state)

    # ========================================================================
    # 3. TOOL TESTS
    # ========================================================================
    print("\n3. Tool Import Tests")
    print("-" * 70)

    test(
        "Import search_versailles_info",
        lambda: __import__("tools.search_versailles_info"),
    )
    test(
        "Import book_versailles_tickets",
        lambda: __import__("tools.book_versailles_tickets"),
    )
    test("Import parking_restaurants", lambda: __import__("tools.parking_restaurants"))
    test("Import get_weather", lambda: __import__("tools.get_weather"))
    test("Import google_maps_tool", lambda: __import__("tools.google_maps_tool"))

    # ========================================================================
    # 4. TOOL FUNCTIONALITY TESTS
    # ========================================================================
    print("\n4. Tool Functionality Tests")
    print("-" * 70)

    def test_google_maps():
        from tools.google_maps_tool import google_maps_route

        result = google_maps_route.invoke(
            {"origin": "Paris", "destination": "Versailles", "mode": "transit"}
        )
        assert "google.com/maps" in result, "Should return Google Maps URL"

    test("Google Maps tool", test_google_maps)

    def test_parking():
        from tools.parking_restaurants import get_parking_info

        result = get_parking_info.invoke({"location": "Versailles"})
        assert "parking" in result.lower(), "Should contain parking info"
        assert "Place d'Armes" in result, "Should mention specific parking"

    test("Parking info tool", test_parking)

    def test_restaurants():
        from tools.parking_restaurants import find_restaurants

        result = find_restaurants.invoke(
            {"location": "Versailles", "cuisine": None, "budget": "moyen"}
        )
        assert "restaurant" in result.lower(), "Should contain restaurant info"

    test("Restaurant finder tool", test_restaurants)

    def test_luggage():
        from tools.parking_restaurants import get_luggage_storage_info

        result = get_luggage_storage_info.invoke({})
        assert "consigne" in result.lower() or "bagage" in result.lower()

    test("Luggage storage tool", test_luggage)

    def test_booking():
        from tools.book_versailles_tickets import book_versailles_tickets

        result = book_versailles_tickets.invoke(
            {
                "date": "2025-06-15",
                "type_billet": "passeport",
                "participants": 2,
                "horaire": "09:00",
            }
        )
        assert "VER" in result, "Should contain booking reference"
        assert "confirmée" in result.lower(), "Should be confirmed"

    test("Ticket booking tool", test_booking)

    def test_availability():
        from tools.book_versailles_tickets import check_ticket_availability

        result = check_ticket_availability.invoke(
            {"date": "2025-06-15", "type_billet": "passeport"}
        )
        assert "disponibilité" in result.lower() or "disponible" in result.lower()

    test("Availability check tool", test_availability)

    # ========================================================================
    # 5. MEMORY TESTS
    # ========================================================================
    print("\n5. Memory Tests")
    print("-" * 70)

    def test_memory():
        from memory.memory import save_session, load_session

        test_data = {"test": "data", "number": 123}
        save_session("test_session", test_data)
        loaded = load_session("test_session")
        assert loaded.get("test") == "data", "Should load saved data"

    test("Session save/load", test_memory)

    # ========================================================================
    # 6. RAG SYSTEM TESTS (if ChromaDB available)
    # ========================================================================
    print("\n6. RAG System Tests")
    print("-" * 70)

    def test_vector_store_import():
        from rag.vector_store import VersaillesVectorStore

        # Just test import, don't initialize (requires data)

    test("Vector store import", test_vector_store_import)

    def test_retriever_import():
        from rag.retriever import VersaillesRetriever

        # Just test import

    test("Retriever import", test_retriever_import)

    # ========================================================================
    # 7. LANGGRAPH TESTS
    # ========================================================================
    print("\n7. LangGraph Tests")
    print("-" * 70)

    def test_langgraph_state():
        from agents.langgraph_flow import State

        state = State(input_text="test", response="", session_id="test")
        assert state["input_text"] == "test"

    test("LangGraph State", test_langgraph_state)

    def test_routing():
        from agents.langgraph_flow import route_input, State

        # Test agent routing
        agent_state = State(
            input_text="Je veux réserver un billet", response="", session_id="test"
        )
        assert route_input(agent_state) == "Agent_Response"

        # Test LLM routing
        llm_state = State(input_text="Bonjour", response="", session_id="test")
        assert route_input(llm_state) == "LLM_Response"

    test("LangGraph routing logic", test_routing)

    # ========================================================================
    # 8. MCP SERVER TESTS
    # ========================================================================
    print("\n8. MCP Server Tests")
    print("-" * 70)

    def test_mcp_import():
        import mcp_server

        # Just test import

    test("MCP server import", test_mcp_import)

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("Test Summary")

    print(f"\n✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {passed + failed}")

    if failed > 0:
        print("\n" + "=" * 70)
        print("Failed Tests:")
        print("=" * 70)
        for name, success, error in tests:
            if not success:
                print(f"\n✗ {name}")
                print(f"  Error: {error}")

    print("\n" + "=" * 70)
    if failed == 0:
        print("✅ All tests passed!")
        print("=" * 70)
        return 0
    else:
        print("⚠️  Some tests failed. See details above.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
