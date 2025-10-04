"""MCP Server for Versailles Agent Tools using FastMCP."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all tools
from tools.check_versailles_availability import check_versailles_availability
from tools.book_versailles_tickets import book_versailles_tickets, check_ticket_availability
from tools.get_next_passage import get_next_passages
from tools.get_schedule_at_times import get_schedules_at_time
from tools.get_weather import get_weather
from tools.google_maps_tool import google_maps_route
from tools.search_train import search_train
from tools.book_train import book_train
from tools.search_airbnb import search_airbnb
from tools.book_airbnb import book_airbnb
from tools.search_versailles_info import (
    search_versailles_info,
    get_versailles_opening_hours,
    get_versailles_ticket_info,
    get_versailles_access_info
)
from tools.parking_restaurants import (
    get_parking_info,
    find_restaurants,
    get_luggage_storage_info
)

# Initialize FastMCP server
mcp = FastMCP("Versailles Visit Planning Agent")


# ============================================================================
# VERSAILLES KNOWLEDGE BASE TOOLS
# ============================================================================

@mcp.tool()
def search_versailles_knowledge(query: str) -> str:
    """
    Search the Versailles knowledge base for information.
    
    Args:
        query: Search query about Versailles
        
    Returns:
        Relevant information from the knowledge base
    """
    return search_versailles_info.invoke({"query": query})


@mcp.tool()
def get_opening_hours(date: str = None) -> str:
    """
    Get opening hours for Château de Versailles.
    
    Args:
        date: Optional specific date to check
        
    Returns:
        Opening hours information
    """
    return get_versailles_opening_hours.invoke({"date": date})


@mcp.tool()
def get_ticket_information() -> str:
    """
    Get information about tickets, pricing, and reservations.
    
    Returns:
        Ticket and pricing information
    """
    return get_versailles_ticket_info.invoke({})


@mcp.tool()
def get_access_information() -> str:
    """
    Get information about accessing Versailles and transportation.
    
    Returns:
        Access and transportation information
    """
    return get_versailles_access_info.invoke({})


# ============================================================================
# VERSAILLES BOOKING TOOLS
# ============================================================================

@mcp.tool()
def check_availability(date: str, type_billet: str) -> str:
    """
    Check ticket availability for Versailles.
    
    Args:
        date: Date to check (YYYY-MM-DD or DD/MM/YYYY)
        type_billet: Type of ticket
        
    Returns:
        Availability status
    """
    return check_versailles_availability.invoke({
        "date": date,
        "type_billet": type_billet
    })


@mcp.tool()
def check_tickets(date: str, type_billet: str) -> str:
    """
    Check detailed ticket availability.
    
    Args:
        date: Date to check
        type_billet: Type of ticket
        
    Returns:
        Detailed availability information
    """
    return check_ticket_availability.invoke({
        "date": date,
        "type_billet": type_billet
    })


@mcp.tool()
def book_tickets(date: str, type_billet: str, participants: int, horaire: str = "09:00") -> str:
    """
    Book tickets for Versailles.
    
    Args:
        date: Visit date
        type_billet: Type of ticket
        participants: Number of participants
        horaire: Preferred time slot
        
    Returns:
        Booking confirmation
    """
    return book_versailles_tickets.invoke({
        "date": date,
        "type_billet": type_billet,
        "participants": participants,
        "horaire": horaire
    })


# ============================================================================
# TRANSPORTATION TOOLS
# ============================================================================

@mcp.tool()
def get_next_metro_bus(stop: str, line: str, transport_type: str = "bus") -> str:
    """
    Get next metro/bus passages.
    
    Args:
        stop: Stop name
        line: Line number
        transport_type: Type (metro, rer, bus, tram)
        
    Returns:
        Next passages information
    """
    return get_next_passages.invoke({
        "stop": stop,
        "line": line,
        "transport_type": transport_type
    })


@mcp.tool()
def get_schedules(stop: str, line: str, time: str, transport_type: str = "bus") -> str:
    """
    Get schedules at specific time.
    
    Args:
        stop: Stop name
        line: Line number
        time: Time to check
        transport_type: Type of transport
        
    Returns:
        Schedule information
    """
    return get_schedules_at_time.invoke({
        "stop": stop,
        "line": line,
        "time": time,
        "transport_type": transport_type
    })


@mcp.tool()
def search_trains(from_station: str, to_station: str, date: str, time: str) -> str:
    """
    Search for train connections.
    
    Args:
        from_station: Departure station
        to_station: Arrival station
        date: Travel date
        time: Departure time
        
    Returns:
        Available train connections
    """
    return search_train.invoke({
        "from_station": from_station,
        "to_station": to_station,
        "date": date,
        "time": time
    })


@mcp.tool()
def book_train_ticket(from_station: str, to_station: str, date: str, time: str, passengers: int) -> str:
    """
    Book a train ticket.
    
    Args:
        from_station: Departure station
        to_station: Arrival station
        date: Travel date
        time: Departure time
        passengers: Number of passengers
        
    Returns:
        Booking confirmation
    """
    return book_train.invoke({
        "from_station": from_station,
        "to_station": to_station,
        "date": date,
        "time": time,
        "passengers": passengers
    })


# ============================================================================
# ACCOMMODATION TOOLS
# ============================================================================

@mcp.tool()
def search_accommodations(city: str, checkin: str, checkout: str, guests: int) -> str:
    """
    Search for accommodations on Airbnb.
    
    Args:
        city: City to search in
        checkin: Check-in date
        checkout: Check-out date
        guests: Number of guests
        
    Returns:
        Available accommodations
    """
    return search_airbnb.invoke({
        "city": city,
        "checkin": checkin,
        "checkout": checkout,
        "guests": guests
    })


@mcp.tool()
def book_accommodation(city: str, checkin: str, checkout: str, guests: int, listing_id: str) -> str:
    """
    Book an accommodation.
    
    Args:
        city: City
        checkin: Check-in date
        checkout: Check-out date
        guests: Number of guests
        listing_id: Listing ID to book
        
    Returns:
        Booking confirmation
    """
    return book_airbnb.invoke({
        "city": city,
        "checkin": checkin,
        "checkout": checkout,
        "guests": guests,
        "listing_id": listing_id
    })


# ============================================================================
# PRACTICAL INFORMATION TOOLS
# ============================================================================

@mcp.tool()
def get_weather_forecast(city: str) -> str:
    """
    Get weather forecast for a city.
    
    Args:
        city: City name
        
    Returns:
        Weather information
    """
    return get_weather.invoke({"city": city})


@mcp.tool()
def get_parking_options(location: str = "Versailles") -> str:
    """
    Get parking information near Versailles.
    
    Args:
        location: Location to search
        
    Returns:
        Parking options and details
    """
    return get_parking_info.invoke({"location": location})


@mcp.tool()
def search_restaurants(location: str = "Versailles", cuisine: str = None, budget: str = "moyen") -> str:
    """
    Find restaurants near Versailles.
    
    Args:
        location: Location to search
        cuisine: Type of cuisine
        budget: Budget level (économique, moyen, élevé)
        
    Returns:
        Restaurant recommendations
    """
    return find_restaurants.invoke({
        "location": location,
        "cuisine": cuisine,
        "budget": budget
    })


@mcp.tool()
def get_luggage_storage() -> str:
    """
    Get luggage storage information.
    
    Returns:
        Luggage storage options
    """
    return get_luggage_storage_info.invoke({})


@mcp.tool()
def get_route_map(origin: str, destination: str, mode: str = "transit") -> str:
    """
    Get Google Maps route.
    
    Args:
        origin: Starting point
        destination: Destination
        mode: Travel mode (transit, driving, walking, bicycling)
        
    Returns:
        Google Maps link
    """
    return google_maps_route.invoke({
        "origin": origin,
        "destination": destination,
        "mode": mode
    })


# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    import uvicorn
    
    host = os.getenv("MCP_SERVER_HOST", "localhost")
    port = int(os.getenv("MCP_SERVER_PORT", 8001))
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  Versailles Visit Planning Agent - MCP Server               ║
║  Running on: http://{host}:{port}                      ║
║                                                              ║
║  Available Tools: {mcp._list_tools()} tools                                    ║
║  - Versailles Knowledge Base (4 tools)                      ║
║  - Booking & Availability (3 tools)                          ║
║  - Transportation (4 tools)                                  ║
║  - Accommodation (2 tools)                                   ║
║  - Practical Info (5 tools)                                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    mcp.run(transport="stdio")
