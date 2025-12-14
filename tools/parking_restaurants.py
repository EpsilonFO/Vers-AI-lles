"""Tools for parking and restaurant information near Versailles."""

from langchain.tools import tool
from typing import List, Dict


@tool(description="Get parking information near Versailles")
def get_parking_info(location: str = "Versailles") -> str:
    """
    Get parking information near the Château de Versailles.

    Args:
        location: Specific location or area (default: Versailles)

    Returns:
        Parking information including locations, prices, and availability
    """
    try:
        # Parking options near Versailles (TODO: Integrate with real-time parking API)
        parking_options = [
            {
                "name": "Parking Place d'Armes",
                "address": "Place d'Armes, 78000 Versailles",
                "distance": "50m du château",
                "price": "4€/heure, 20€/jour",
                "capacity": "~400 places",
                "type": "Payant",
                "hours": "24h/24",
                "notes": "Le plus proche du château",
            },
            {
                "name": "Parking Gare Rive Droite",
                "address": "Rue de la Paroisse, 78000 Versailles",
                "distance": "800m du château (10 min à pied)",
                "price": "2€/heure, 12€/jour",
                "capacity": "~200 places",
                "type": "Payant",
                "hours": "6h-22h",
                "notes": "Proche de la gare RER",
            },
            {
                "name": "Parking Notre-Dame",
                "address": "Rue Royale, 78000 Versailles",
                "distance": "600m du château (8 min à pied)",
                "price": "2.50€/heure, 15€/jour",
                "capacity": "~150 places",
                "type": "Payant",
                "hours": "7h-21h",
                "notes": "Centre-ville, proche commerces",
            },
            {
                "name": "Parking Trianon (Grille de la Reine)",
                "address": "Avenue de Trianon, 78000 Versailles",
                "distance": "Accès direct au domaine de Trianon",
                "price": "12€/véhicule (forfait journée)",
                "capacity": "~100 places",
                "type": "Payant",
                "hours": "8h-18h30",
                "notes": "Idéal pour visiter Trianon en premier",
            },
        ]

        result = "🅿️ **Parkings près du Château de Versailles**\n\n"

        for i, parking in enumerate(parking_options, 1):
            result += f"**{i}. {parking['name']}**\n"
            result += f"   📍 Adresse: {parking['address']}\n"
            result += f"   📏 Distance: {parking['distance']}\n"
            result += f"   💰 Tarif: {parking['price']}\n"
            result += f"   🚗 Capacité: {parking['capacity']}\n"
            result += f"   🕐 Horaires: {parking['hours']}\n"
            result += f"   ℹ️ {parking['notes']}\n\n"

        result += """
💡 **Conseils:**
- Arrivez tôt le matin pour trouver une place facilement
- Le parking Place d'Armes est le plus pratique mais se remplit vite
- Pensez aux transports en commun (RER C) pour éviter les problèmes de stationnement
- Les parkings sont gratuits pour les personnes à mobilité réduite (sur présentation de la carte)
"""

        return result

    except Exception as e:
        return f"Erreur lors de la récupération des informations de parking: {str(e)}"


@tool(description="Find restaurants near Versailles")
def find_restaurants(
    location: str = "Versailles", cuisine: str = None, budget: str = "moyen"
) -> str:
    """
    Find restaurants near the Château de Versailles.

    Args:
        location: Location to search (default: Versailles)
        cuisine: Type of cuisine (française, italienne, asiatique, etc.)
        budget: Budget level (économique, moyen, élevé)

    Returns:
        List of recommended restaurants with details
    """
    try:
        # Restaurant recommendations (TODO: Integrate with restaurant API like Google Places)
        restaurants = [
            {
                "name": "La Flottille",
                "type": "Restaurant du château",
                "cuisine": "Française",
                "location": "Dans le parc du château",
                "price": "€€€",
                "rating": "4.2/5",
                "speciality": "Cuisine traditionnelle française",
                "hours": "12h-15h",
                "notes": "Vue sur le Grand Canal, réservation recommandée",
            },
            {
                "name": "La Petite Venise",
                "type": "Restaurant du château",
                "cuisine": "Française/Italienne",
                "location": "Dans le parc du château",
                "price": "€€",
                "rating": "4.0/5",
                "speciality": "Pizzas, pâtes, salades",
                "hours": "11h30-18h",
                "notes": "Idéal pour un déjeuner rapide",
            },
            {
                "name": "Ore - Ducasse au Château",
                "type": "Restaurant gastronomique",
                "cuisine": "Française gastronomique",
                "location": "Pavillon Dufour (entrée du château)",
                "price": "€€€€",
                "rating": "4.5/5",
                "speciality": "Cuisine d'Alain Ducasse",
                "hours": "12h-14h30, 19h-21h30",
                "notes": "Restaurant étoilé, réservation obligatoire",
            },
            {
                "name": "Le Bistrot du 11",
                "type": "Bistrot",
                "cuisine": "Française",
                "location": "11 Rue de la Chancellerie (5 min à pied)",
                "price": "€€",
                "rating": "4.3/5",
                "speciality": "Cuisine bistrot, plats du jour",
                "hours": "12h-14h30, 19h-22h",
                "notes": "Ambiance conviviale, bon rapport qualité-prix",
            },
            {
                "name": "Le Montbauron",
                "type": "Brasserie",
                "cuisine": "Française",
                "location": "7 Rue Montbauron (10 min à pied)",
                "price": "€€",
                "rating": "4.1/5",
                "speciality": "Fruits de mer, viandes grillées",
                "hours": "12h-15h, 19h-23h",
                "notes": "Grande terrasse, menu enfants disponible",
            },
            {
                "name": "Angelina Versailles",
                "type": "Salon de thé",
                "cuisine": "Pâtisserie/Salon de thé",
                "location": "Dans le château",
                "price": "€€",
                "rating": "4.4/5",
                "speciality": "Mont-Blanc, chocolat chaud",
                "hours": "10h-18h",
                "notes": "Parfait pour un goûter après la visite",
            },
        ]

        # Filter by cuisine if specified
        if cuisine:
            restaurants = [
                r for r in restaurants if cuisine.lower() in r["cuisine"].lower()
            ]

        # Filter by budget
        budget_map = {
            "économique": ["€", "€€"],
            "moyen": ["€€", "€€€"],
            "élevé": ["€€€", "€€€€"],
        }
        if budget.lower() in budget_map:
            price_range = budget_map[budget.lower()]
            restaurants = [r for r in restaurants if r["price"] in price_range]

        if not restaurants:
            return "Aucun restaurant trouvé avec ces critères. Essayez d'élargir votre recherche."

        result = "🍽️ **Restaurants près du Château de Versailles**\n\n"

        for i, resto in enumerate(restaurants, 1):
            result += f"**{i}. {resto['name']}**\n"
            result += f"   🍴 Type: {resto['type']}\n"
            result += f"   🌍 Cuisine: {resto['cuisine']}\n"
            result += f"   📍 Localisation: {resto['location']}\n"
            result += f"   💰 Prix: {resto['price']}\n"
            result += f"   ⭐ Note: {resto['rating']}\n"
            result += f"   👨‍🍳 Spécialité: {resto['speciality']}\n"
            result += f"   🕐 Horaires: {resto['hours']}\n"
            result += f"   ℹ️ {resto['notes']}\n\n"

        result += """
💡 **Conseils:**
- Réservez à l'avance, surtout le week-end
- Les restaurants du château ferment tôt (vers 15h-18h)
- Pour un budget serré, pensez aux boulangeries et cafés du quartier
- Menu enfants disponibles dans la plupart des restaurants
"""

        return result

    except Exception as e:
        return f"Erreur lors de la recherche de restaurants: {str(e)}"


@tool(description="Get luggage storage information")
def get_luggage_storage_info() -> str:
    """
    Get information about luggage storage facilities near Versailles.

    Returns:
        Luggage storage options and details
    """
    try:
        info = """
🎒 **Consignes à bagages - Château de Versailles**

**1. Consigne du Château**
   📍 Localisation: Pavillon Dufour (entrée principale)
   💰 Tarif: Gratuit
   📏 Taille max: Sacs à dos et petits bagages
   🕐 Horaires: Pendant les heures d'ouverture du château
   ⚠️ Limitations: 
      - Pas de valises de grande taille
      - Capacité limitée
      - Fermeture obligatoire avec cadenas (non fourni)

**2. Nannybag - Gare Versailles Rive Gauche**
   📍 Localisation: Commerces partenaires près de la gare
   💰 Tarif: 6€/bagage/jour
   📏 Taille: Tous types de bagages acceptés
   🕐 Horaires: Variables selon le commerce
   ℹ️ Réservation en ligne: www.nannybag.com
   
**3. Bounce - Versailles Centre**
   📍 Localisation: Plusieurs points en ville
   💰 Tarif: 5.90€/bagage/jour
   📏 Taille: Tous types de bagages
   🕐 Horaires: Variables selon le point
   ℹ️ Réservation en ligne: www.usebounce.com

**4. Consignes Gare Montparnasse (Paris)**
   📍 Localisation: Gare Montparnasse (30 min en train)
   💰 Tarif: 5.50€-9.50€ selon taille
   📏 Taille: Tous types de bagages
   🕐 Horaires: 6h15-23h15
   ℹ️ Solution si vous venez de Paris

💡 **Conseils:**
- Réservez en ligne pour garantir une place
- Arrivez léger pour profiter pleinement de la visite
- Les grands sacs ne sont pas autorisés dans le château
- Prévoyez un cadenas pour les consignes gratuites
- En haute saison, les consignes se remplissent vite

⚠️ **Objets interdits dans le château:**
- Valises et grands sacs
- Objets tranchants
- Liquides en grande quantité
- Trépieds et perches à selfie
"""
        return info

    except Exception as e:
        return f"Erreur lors de la récupération des informations: {str(e)}"
