import json
import os
import re
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - keeps the app importable when SDK is absent.
    genai = None

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "*")}})

MODEL_NAME = "gemini-1.5-flash"
DEFAULT_SUGGESTIONS = [
    # North India - Delhi & NCR
    "Delhi", "New Delhi", "Agra", "Mathura", "Firozabad", "Aligarh", "Meerut", "Ghaziabad",
    "Faridabad", "Noida", "Gurgaon", "Bulandshahr", "Etah", "Mainpuri", "Etawah",
    # Uttar Pradesh
    "Lucknow", "Varanasi", "Kanpur", "Allahabad", "Meerut", "Bareilly", "Moradabad",
    "Saharanpur", "Gorakhpur", "Basti", "Azamgarh", "Ballia", "Jaunpur", "Mirzapur",
    "Ghazipur", "Auraiya", "Hamirpur", "Banda", "Kaushambi", "Raibareilly", "Raebareli",
    # Uttarakhand
    "Rishikesh", "Haridwar", "Dehradun", "Nainital", "Mussoorie", "Almora", "Bageshwar",
    "Chamoli", "Rudraprayag", "Uttarkashi", "Chopta", "Auli", "Lansdowne", "Dhanaulti",
    "Chakrata", "Munsiyari", "Pauri", "Garhwal", "Kumaon",
    # Himachal Pradesh
    "Shimla", "Manali", "Dharamshala", "McLeod Ganj", "Kullu", "Dalhousie", "Palampur",
    "Kasauli", "Chail", "Baijnath", "Kangra", "Spiti", "Kinnaur", "Tirthan Valley", "Bir",
    "Billing", "Khajjiar", "Solan", "Mandi", "Bilaspur", "Rampur", "Woodstock",
    # Punjab & Chandigarh
    "Amritsar", "Ludhiana", "Pathankot", "Jullundur", "Patiala", "Chandigarh", "Jalandhar",
    "Gurdaspur", "Hoshiarpur", "Roopnagar", "Sangrur", "Mansa",
    # Rajasthan
    "Jaipur", "Jodhpur", "Jaisalmer", "Udaipur", "Ajmer", "Pushkar", "Bikaner", "Churu",
    "Barmer", "Pali", "Sirohi", "Jhunjhunu", "Sikar", "Nagaur", "Kishangarh", "Tonk",
    "Bundi", "Kota", "Baran", "Jhalawar", "Alwar", "Bharatpur", "Dholpur", "Sawai Madhopur",
    "Karauli", "Banswara", "Dungarpur", "Rajasamand", "Pratapgarh",
    # South India - Tamil Nadu
    "Chennai", "Madurai", "Coimbatore", "Salem", "Tiruppur", "Erode", "Thanjavur",
    "Trichy", "Kanyakumari", "Nagercoil", "Tirunelveli", "Rameshwaram", "Virudunagar",
    "Thoothukudi", "Nellore", "Tirupati", "Chidambaram", "Kumbakonam", "Mayavaram",
    # Andhra Pradesh & Telangana
    "Hyderabad", "Vijayawada", "Visakhapatnam", "Warangal", "Khammam", "Rajahmundry",
    "Tirupati", "Nellore", "Kurnool", "Anantapur", "Guntur", "Tenali", "Ongole",
    "Kadapa", "Nandyal", "Hindupur", "Chittoor", "Vikarabad",
    # Karnataka
    "Bangalore", "Mysore", "Coorg", "Belgaum", "Hubli", "Dharwad", "Gulbarga",
    "Bijapur", "Raichur", "Bellary", "Tumkur", "Kolar", "Chikmagalur", "Kodagu",
    "Shimoga", "Udupi", "Mangalore", "Kasaragod", "Davangere", "Hassan",
    # Kerala & Coastal South
    "Kochi", "Thiruvananthapuram", "Munnar", "Alleppey", "Wayanad", "Kannur", "Kasaragod",
    "Ernakulathappan", "Idukki", "Pathanamthitta", "Alappuzha", "Thrissur", "Palakkad",
    "Malappuram", "Kozhikode", "Vadakara", "Thalassery", "Varkala", "Kumarakom",
    # Goa & Union Territories
    "Panaji", "Margao", "Vasco", "Canacona", "Ponda", "Pernem", "Bicholim", "Sattari",
    "Quepem", "Daman", "Silvassa", "Pondicherry", "Yanam", "Mahe", "Karaikal",
    # West India - Maharashtra
    "Mumbai", "Pune", "Nagpur", "Aurangabad", "Nashik", "Solapur", "Sangli",
    "Satara", "Kolhapur", "Ratnagiri", "Sindhudurg", "Parbhani", "Latur", "Nanded",
    "Jalna", "Buldhana", "Akola", "Amravati", "Yavatmal", "Wardha", "Chandrapur",
    # Gujarat
    "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar", "Baroda", "Anand",
    "Kheda", "Mahesana", "Sabarkantha", "Banaskantha", "Aravalli", "Kutch", "Jamnagar",
    "Porbandar", "Dwarka", "Junagadh", "Bhavnagar", "Amreli", "Gondal", "Botad",
    "Surendranagar", "Morbi", "Halfwaypoint",
    # Central India - Madhya Pradesh
    "Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Mhow", "Omkareshwar",
    "Khajuraho", "Chhatarpur", "Tikamgarh", "Panna", "Satna", "Mandla", "Balaghat",
    "Burhanpur", "Khandwa", "Betul", "Hoshangabad", "Itarsi", "Pipariya", "Chhindwara",
    "Seoni", "Dindori", "Katni", "Sagar", "Damoh", "Panna", "Ashoknagar", "Vidisha",
    "Guna", "Morena", "Sheopur", "Bhind",
    # East India - Kolkata & West Bengal
    "Kolkata", "Darjeeling", "Kalimpong", "Kurseong", "Siliguri", "Alipurduar",
    "Jalpaiguri", "Cooch Behar", "Dinajpur", "Murshidabad", "Nadia", "Birbhum",
    "Bankura", "Purulia", "Medinipur", "Hooghly", "Howrah", "24 Parganas",
    # Odisha
    "Bhubaneswar", "Puri", "Konark", "Cuttack", "Balasore", "Baripada", "Jharsuguda",
    "Sambalpur", "Rourkela", "Sundargarh", "Dhenkanal", "Angul", "Kalahandi",
    "Bargarh", "Bolangir", "Nuapada", "Malkangiri", "Koraput", "Rayagada", "Gajapati",
    # Assam & North East
    "Guwahati", "Shillong", "Cherrapunjee", "Silchar", "Dibrugarh", "Assam", "Kaziranga",
    "Majuli", "Jorhat", "Golaghat", "Kohima", "Dimapur", "Imphal", "Aizawl", "Agartala",
]
LOCATION_ALIASES = {
    "delhi": ["New Delhi", "Old Delhi", "Central Delhi"],
    "agra": ["Taj Mahal", "Agra Fort"],
    "jaipur": ["Pink City", "Amer Fort", "Hawa Mahal"],
    "lucknow": ["Charbagh", "Lucknow City"],
    "varanasi": ["Benares", "Kashi"],
    "rishikesh": ["Yoga Capital", "Neelkanth"],
    "himachal pradesh": ["Palampur", "Baijnath", "Kangra"],
    "ladakh": ["Leh", "Kargil", "Khardung La"],
    "kashmir": ["Srinagar", "Gulmarg", "Pahalgam"],
    "nainital": ["Naini Lake", "Nainital City"],
    "mussoorie": ["Mall Road", "Landour"],
    "shimla": ["The Ridge", "Shimla City"],
    "manali": ["Hadimba Temple", "Vashisht"],
    "chennai": ["Marina Beach", "Chennai City"],
    "bangalore": ["Vidhana Soudha", "Cubbon Park"],
    "hyderabad": ["Charminar", "Hyderabad City"],
    "kochi": ["Fort Kochi", "Mattancherry"],
    "thiruvananthapuram": ["Padmanabha Swamy", "Trivandrum City"],
    "mysore": ["Mysore Palace", "Chamundi Hill"],
    "coorg": ["Madikeri", "Coorg Region"],
    "ooty": ["Udhagamandalam", "Nilgiris"],
    "munnar": ["Munnar Hills", "Tea Estates"],
    "kerala": ["Munnar", "Alleppey", "Kochi"],
    "pondicherry": ["Puducherry City", "Auroville"],
    "madurai": ["Meenakshi Temple", "Madurai City"],
    "kolkata": ["Victoria Memorial", "Kolkata City"],
    "darjeeling": ["Tiger Hill", "Darjeeling Town"],
    "sikkim": ["Gangtok", "Kanyam"],
    "assam": ["Guwahati", "Kaziranga"],
    "meghalaya": ["Shillong", "Cherrapunjee"],
    "odisha": ["Bhubaneswar", "Puri"],
    "guwahati": ["Guwahati City", "Umananda"],
    "mumbai": ["South Mumbai", "Bandra", "Juhu"],
    "pune": ["Shaniwar Wada", "Pune City"],
    "ahmedabad": ["Sabarmati Ashram", "Ahmedabad City"],
    "rajkot": ["Rajkot City", "Kaba Gandhi"],
    "goa": ["North Goa", "South Goa", "Panaji"],
    "diu": ["Diu Town", "Diu Fort"],
    "gujarat": ["Ahmedabad", "Vadodara"],
    "indore": ["Indore City", "Rajwada"],
    "bhopal": ["Bhopal City", "Van Vihar"],
    "jabalpur": ["Jabalpur City", "Marble Rocks"],
    "khajuraho": ["Khajuraho Temples", "Khajuraho Town"],
    "madhya pradesh": ["Indore", "Bhopal"],
    "udaipur": ["City Palace", "Lake Pichola", "Sajjangarh"],
}


def _gemini_model() -> Optional[Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None:
        return None

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME)


def _strip_json_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    cleaned = _strip_json_fences(text)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return None


def _budget_label(budget: Any) -> str:
    if budget is None:
        return "Medium"
    return str(budget).strip() or "Medium"


def _budget_tier(budget: Any) -> str:
    value = str(budget).lower().strip() if budget is not None else "medium"
    if any(token in value for token in ["high", "premium", "luxury"]):
        return "high"
    if any(token in value for token in ["low", "budget", "economy"]):
        return "low"
    return "medium"


def _scale_cost(base: int, tier: str) -> str:
    if tier == "low":
        return f"₹{max(150, int(base * 0.7))} - ₹{max(300, int(base * 0.95))}"
    if tier == "high":
        return f"₹{int(base * 1.3)} - ₹{int(base * 1.8)}"
    return f"₹{base} - ₹{int(base * 1.25)}"


def _get_unsplash_image(query: str) -> str:
    """Generate Unsplash image URL for a query"""
    safe_query = query.replace(" ", "+").lower()
    return f"https://source.unsplash.com/800x600/?{safe_query},india"


def _get_location_specific_data(location: str) -> Dict[str, Any]:
    """Get realistic, location-specific itinerary data"""
    location_lower = location.lower()
    
    location_database = {
        "delhi": {
            "places": ["Red Fort", "India Gate", "Jama Masjid", "Humayun's Tomb", "Lotus Temple", "Chandni Chowk"],
            "food": ["Paranthe Wali Gali", "Karim's Restaurant", "Haldiram's", "Old Delhi Street Food", "Indian Coffee House", "Bukhara"],
            "breakfast": [("Chole Bhature", "Paranthe Wali Gali"), ("Poori-Aloo", "Local Dhaba"), ("Tea with Samosa", "Street Vendor")],
            "lunch": [("Biryani", "Karim's Restaurant"), ("Butter Chicken", "Bukhara"), ("Dal Makhani", "Moti Mahal")],
            "dinner": [("Tandoori Chicken", "Bukhara"), ("Kebabs", "Karim's Restaurant"), ("Mughlai Cuisine", "Moti Mahal")],
            "snacks": [("Jalebi", "Chandni Chowk Market"), ("Gol Gappa", "Street Vendor"), ("Samosa", "Haldiram's")],
        },
        "agra": {
            "places": ["Taj Mahal", "Agra Fort", "Mehtab Bagh", "Akbar's Tomb", "Fatehpur Sikri"],
            "food": ["Petha Shop", "Mughlai Restaurant", "Street Food Market", "Local Dhabas", "Taj Bakes"],
            "breakfast": [("Poori with Paneer", "Local Dhaba"), ("Tea and Toast", "Taj Bakes"), ("Puri-Sabzi", "Street Vendor")],
            "lunch": [("Mutton Biryani", "Mughlai Restaurant"), ("Tandoori Chicken", "Local Dhaba"), ("Paneer Masala", "Agra Restaurant")],
            "dinner": [("Mughlai Feast", "Mughlai Restaurant"), ("Kebab Platter", "Local Dhaba"), ("Fish Curry", "River View Restaurant")],
            "snacks": [("Petha", "Petha Shop"), ("Kheer", "Sweet Shop"), ("Samosa", "Street Vendor")],
        },
        "jaipur": {
            "places": ["Hawa Mahal", "City Palace", "Jantar Mantar", "Albert Hall Museum", "Nahargarh Fort", "Ram Niwas Garden"],
            "food": ["Bapu Bazaar Food", "Chanakya Restaurant", "Chokhi Dhani", "Street Food Market", "Cafe Coffee Day"],
            "breakfast": [("Bajra Roti", "Chokhi Dhani"), ("Mohan Maas", "Local Dhaba"), ("Mirchi Bajji", "Street Vendor")],
            "lunch": [("Laal Maas", "Chanakya Restaurant"), ("Gatte ki Sabzi", "Chokhi Dhani"), ("Ker Sangri", "Rajasthani Restaurant")],
            "dinner": [("Rajasthani Thali", "Chokhi Dhani"), ("Bikaneri Bhujia Curry", "Chanakya Restaurant"), ("Dal Baati Churma", "Traditional Restaurant")],
            "snacks": [("Ghevar", "Mithai Shop"), ("Fafda", "Bapu Bazaar"), ("Pyaaz Kachori", "Street Vendor")],
        },
        "goa": {
            "places": ["Baga Beach", "Colva Beach", "Fort Aguada", "Basilica of Bom Jesus", "Dudhsagar Falls", "Anjuna Market"],
            "food": ["Beach Shacks", "Peixaria", "Fisherman's Wharf", "Vindaloo Restaurant", "Local Market"],
            "breakfast": [("Puri-Curry", "Local Shack"), ("Idli-Sambar", "Restaurant"), ("Coconut Bread", "Bakery")],
            "lunch": [("Fish Curry Rice", "Peixaria"), ("Prawn Ghee Roast", "Fisherman's Wharf"), ("Crab Masala", "Beach Restaurant")],
            "dinner": [("Tandoori Fish", "Beach Shack"), ("Seafood Platter", "Vindaloo Restaurant"), ("Goan Prawn Curry", "Local Restaurant")],
            "snacks": [("Cutlets", "Bakery"), ("Empanadas", "Portuguese Cafe"), ("Goan Sweets", "Local Shop")],
        },
        "mumbai": {
            "places": ["Gateway of India", "Marine Drive", "Siddhivinayak Temple", "Haji Ali Dargah", "Colaba Causeway", "Dharavi Slum Tour"],
            "food": ["Colaba Food Market", "Mahesh Lunch Home", "Copper Chimney", "Bade Miyan Chote Miyan", "Street Food Stalls"],
            "breakfast": [("Vada Pav", "Street Vendor"), ("Pav Bhaji", "Bade Miyan Chote Miyan"), ("Dosa", "South Indian Restaurant")],
            "lunch": [("Biryani", "Mahesh Lunch Home"), ("Tandoori", "Copper Chimney"), ("Butter Chicken", "North Indian Restaurant")],
            "dinner": [("Seafood", "Mahesh Lunch Home"), ("North Indian Cuisine", "Copper Chimney"), ("Street Food Crawl", "Food Market")],
            "snacks": [("Pav Bhaji", "Bade Miyan Chote Miyan"), ("Sev Puri", "Street Vendor"), ("Bhelpuri", "Chowpati Beach")],
        },
        "bangalore": {
            "places": ["Vidhana Soudha", "Cubbon Park", "Lalbagh Botanical Garden", "Tipu Sultan Palace", "Nandi Hills", "MG Road"],
            "food": ["Koshy's", "MTR", "Vidyarthi Bhavan", "Toit Brewery", "Tech Park Food Courts"],
            "breakfast": [("Dosa", "Vidyarthi Bhavan"), ("Idli-Sambar", "MTR"), ("Puttu", "South Indian Restaurant")],
            "lunch": [("Biryani", "Nagarjuna Restaurant"), ("Curry Rice", "MTR"), ("Masala Dosa", "Vidyarthi Bhavan")],
            "dinner": [("North Indian", "Koshy's"), ("Coastal Cuisine", "Toit Brewery"), ("International Food", "High Street Restaurant")],
            "snacks": [("Medhu Vada", "MTR"), ("Filter Coffee", "Koshy's"), ("Khichdi", "Street Vendor")],
        },
        "hyderabad": {
            "places": ["Charminar", "Mecca Masjid", "Golconda Fort", "Hussain Sagar Lake", "Salar Jung Museum", "Ramakrishna Temple"],
            "food": ["Paradise Biryani", "Haleem Restaurant", "Pista House", "Biryani Stalls", "Nizamia Foods"],
            "breakfast": [("Puri-Dal", "Local Restaurant"), ("Idli", "South Indian Restaurant"), ("Dosa", "Restaurant")],
            "lunch": [("Hyderabadi Biryani", "Paradise Biryani"), ("Haleem", "Haleem Restaurant"), ("Mirch Masala", "Traditional Restaurant")],
            "dinner": [("Biryani Feast", "Pista House"), ("Kebabs", "Nizamia Foods"), ("Tandoori", "Restaurant")],
            "snacks": [("Lukhmi", "Sweet Shop"), ("Double Egg Biryani", "Biryani Stalls"), ("Nihari", "Daawat Restaurant")],
        },
        "kochi": {
            "places": ["Fort Kochi", "Mattancherry Palace", "Chinese Fishing Nets", "Jew Town", "Kathakali Performance", "Munnar"],
            "food": ["Seafood Restaurants", "Spice Market", "Paradesi Restaurant", "Local Markets", "Juice Bars"],
            "breakfast": [("Appam", "Traditional Restaurant"), ("Idiyappam", "Kerala Restaurant"), ("Puttu", "Local Restaurant")],
            "lunch": [("Fish Curry Rice", "Paradesi Restaurant"), ("Prawn Masala", "Seafood Restaurant"), ("Duck Curry", "Local Dhaba")],
            "dinner": [("Kerala Sadya", "Traditional Restaurant"), ("Seafood Platter", "Seafood Restaurant"), ("Coconut Curry", "Kochi Restaurant")],
            "snacks": [("Banana Chips", "Local Shop"), ("Ginger Cookies", "Bakery"), ("Mango Pickle", "Spice Market")],
        },
        "varanasi": {
            "places": ["Ganges River", "Kashi Vishwanath Temple", "Dashashwamedh Ghat", "Annapurna Temple", "Boat Rides"],
            "food": ["Ghat Dhabas", "Kachori Vendor", "Sweet Shop", "Temple Prasad", "Local Stalls"],
            "breakfast": [("Kachori-Jalebi", "Kachori Vendor"), ("Puri-Aloo", "Ghat Dhaba"), ("Chai", "Tea Stall")],
            "lunch": [("Dal Puri", "Local Restaurant"), ("Paneer Sabzi", "Vegetarian Restaurant"), ("Litti Chikhalwali", "Traditional Restaurant")],
            "dinner": [("Vegetarian Thali", "Ghat Dhaba"), ("Samosa", "Street Vendor"), ("Sweets", "Sweet Shop")],
            "snacks": [("Jalebi", "Sweet Shop"), ("Paan", "Paan Shop"), ("Prasad", "Temple")],
        },
        "rishikesh": {
            "places": ["Ram Jhula", "Laxman Jhula", "Parmarth Niketan", "Yoga Capital", "Triveni Ghat", "Beatles Ashram"],
            "food": ["Yoga Cafe", "Rajsa Restaurant", "Ghat Cafes", "Health Food Shops", "Juice Bars"],
            "breakfast": [("Pancakes", "Yoga Cafe"), ("Smoothie Bowl", "Health Food Shop"), ("Granola", "Cafe")],
            "lunch": [("Vegetarian Cuisine", "Rajsa Restaurant"), ("Ayurvedic Food", "Health Restaurant"), ("Brown Rice & Veggies", "Yoga Cafe")],
            "dinner": [("Vegan Options", "Health Food Shop"), ("Light Meals", "Ghat Cafe"), ("Herbal Tea", "Cafe")],
            "snacks": [("Protein Bars", "Health Shop"), ("Fruits", "Market"), ("Nuts", "Shop")],
        },
    }
    
    # Get location data or return default
    data = location_database.get(location_lower, {
        "places": ["Main Attraction", "Historical Site", "Local Market", "Scenic Viewpoint", "Cultural Center"],
        "food": ["Local Restaurant", "Street Food Vendor", "Traditional Eatery", "Market Stall", "Cafe"],
        "breakfast": [("Local Breakfast", "Local Restaurant")],
        "lunch": [("Local Lunch", "Local Restaurant")],
        "dinner": [("Local Dinner", "Local Restaurant")],
        "snacks": [("Local Snacks", "Local Shop")],
    })
    
    return data


def _demo_location_validation(location: str) -> Dict[str, Any]:
    normalized = location.strip().lower()
    if normalized in LOCATION_ALIASES:
        return {
            "valid": True,
            "canonical_location": location.strip().title(),
            "suggestions": LOCATION_ALIASES[normalized],
            "message": f"{location.strip().title()} looks like a valid travel destination.",
        }

    for known in DEFAULT_SUGGESTIONS:
        if normalized and normalized in known.lower():
            return {
                "valid": True,
                "canonical_location": known,
                "suggestions": [known],
                "message": f"Did you mean {known}?",
            }

    suggestions = [item for item in DEFAULT_SUGGESTIONS if item.lower().startswith(normalized[:1])][:3]
    return {
        "valid": False,
        "canonical_location": "",
        "suggestions": suggestions or DEFAULT_SUGGESTIONS[:3],
        "message": f"{location.strip().title()} could not be verified. Try one of the suggested locations.",
    }


def _demo_itinerary(location: str, days: int, people: int, preferences: str, budget: Any) -> Dict[str, Any]:
    budget_tier = _budget_tier(budget)
    preference_text = preferences.strip() if preferences else "scenic spots, local food, and relaxed exploration"
    location_data = _get_location_specific_data(location)

    scenic_templates = [
        (
            "Heritage Walk",
            "Start with the best-known landmark and nearby photo stops.",
            [location_data["places"][0], location_data["places"][1]],
            [location_data["food"][0], location_data["food"][1]],
        ),
        (
            "Nature & Views",
            "Mix open-air sightseeing with a scenic lunch break.",
            [location_data["places"][2], location_data["places"][3]],
            [location_data["food"][2], location_data["food"][3]],
        ),
        (
            "Local Culture",
            "Spend the afternoon around markets, museums, or cultural streets.",
            [location_data["places"][4], location_data["places"][5] if len(location_data["places"]) > 5 else location_data["places"][0]],
            [location_data["food"][4], location_data["food"][0]],
        ),
    ]

    days_payload: List[Dict[str, Any]] = []
    for index in range(days):
        template = scenic_templates[index % len(scenic_templates)]
        day_number = index + 1
        day_cost_multiplier = 1 + (0.08 * (day_number % 3))
        
        # Food-focused itinerary
        food_day = {
            "day": day_number,
            "title": f"Day {day_number} - Food Trail",
            "theme": "Culinary Experience",
            "summary": f"A delicious food-focused journey through {location.title()}",
            "morning": {
                "title": "Morning",
                "timestamp": "7:00 AM - 10:00 AM",
                "description": "Start your day with authentic local breakfast",
                "food": [
                    {
                        "name": f"{location_data['breakfast'][0][0]} at {location_data['breakfast'][0][1]}" if location_data.get("breakfast") else "Local breakfast speciality",
                        "cuisine": "Regional breakfast",
                        "description": f"Traditional morning meal loved by locals in {location.title()}",
                        "cost": _scale_cost(int(150 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"{location_data['breakfast'][0][0]} {location}"),
                    },
                    {
                        "name": "Morning beverage spot",
                        "cuisine": "Coffee/Tea/Juice",
                        "description": "Fresh local drinks to start your day",
                        "cost": _scale_cost(int(80 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"Indian tea coffee {location}"),
                    }
                ],
            },
            "afternoon": {
                "title": "Afternoon",
                "timestamp": "12:30 PM - 4:00 PM",
                "description": "Explore the best local lunch and street food",
                "food": [
                    {
                        "name": f"{location_data['lunch'][0][0]} at {location_data['lunch'][0][1]}" if location_data.get("lunch") else "Main lunch dish",
                        "cuisine": "Local cuisine",
                        "description": f"Signature dish of {location.title()}",
                        "cost": _scale_cost(int(400 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"{location_data['lunch'][0][0]} {location} food"),
                    },
                    {
                        "name": f"{location_data['snacks'][0][0]} at {location_data['snacks'][0][1]}" if location_data.get("snacks") else "Street food",
                        "cuisine": "Street food",
                        "description": "Popular local snack or appetizer",
                        "cost": _scale_cost(int(120 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"{location_data['snacks'][0][0]} street food"),
                    }
                ],
            },
            "evening": {
                "title": "Evening",
                "timestamp": "6:00 PM - 11:00 PM",
                "description": "Dinner and late-night food experiences",
                "food": [
                    {
                        "name": f"{location_data['dinner'][0][0]} at {location_data['dinner'][0][1]}" if location_data.get("dinner") else "Dinner restaurant",
                        "cuisine": "Local dinner",
                        "description": "Premium dining experience",
                        "cost": _scale_cost(int(550 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"{location_data['dinner'][0][0]} restaurant {location}"),
                    },
                    {
                        "name": "Dessert or evening treat",
                        "cuisine": "Sweets/Desserts",
                        "description": f"Local sweet speciality from {location.title()}",
                        "cost": _scale_cost(int(150 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"Indian sweets desserts {location}"),
                    }
                ],
            },
        }
        
        # Tourist places itinerary
        places_day = {
            "day": day_number,
            "title": f"Day {day_number} - {template[0]}",
            "theme": template[0],
            "summary": f"Explore tourist spots and attractions",
            "morning": {
                "title": "Morning",
                "timestamp": "8:00 AM - 12:00 PM",
                "description": template[1],
                "places": [
                    {
                        "name": template[2][0],
                        "description": f"A famous start to the day for {people} traveler(s).",
                        "cost": _scale_cost(int(250 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"{template[2][0]} {location} tourist attraction"),
                    }
                ],
            },
            "afternoon": {
                "title": "Afternoon",
                "timestamp": "1:00 PM - 5:00 PM",
                "description": "Keep the pace lighter with a lunch stop and a second attraction.",
                "places": [
                    {
                        "name": template[2][1],
                        "description": f"Recommended for {people} traveler(s) after lunch.",
                        "cost": _scale_cost(int(320 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"{template[2][1]} {location}"),
                    },
                    {
                        "name": template[2][0] if len(template[2]) < 3 else "Local Market",
                        "description": "A compact follow-up stop to keep the day moving.",
                        "cost": _scale_cost(int(140 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"{location} market local bazaar"),
                    },
                ],
            },
            "evening": {
                "title": "Evening",
                "timestamp": "6:00 PM - 9:00 PM",
                "description": "Finish with a relaxed stop and a sunset view or market walk.",
                "places": [
                    {
                        "name": "Sunset point or promenade",
                        "description": "An easy evening stop before dinner.",
                        "cost": _scale_cost(int(120 * day_cost_multiplier), budget_tier),
                        "image": _get_unsplash_image(f"{location} sunset viewpoint scenic"),
                    }
                ],
            },
        }
        
        days_payload.append({"food": food_day, "places": places_day})

    return {
        "location": location.title(),
        "days": days,
        "people": people,
        "budget": _budget_label(budget),
        "preferences": preferences,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": f"A {budget_tier} budget plan for {people} traveler(s) in {location.title()} with focus on {preference_text}.",
        "days_plan": days_payload,
    }


def _validate_location_with_gemini(location: str) -> Dict[str, Any]:
    model = _gemini_model()
    if model is None:
        return _demo_location_validation(location)

    prompt = f"""
You are verifying travel destinations for a trip planner.

Return JSON only with this shape:
{{
  "valid": true or false,
  "canonical_location": "resolved location or empty string",
  "suggestions": ["similar valid locations"],
  "message": "short user-friendly explanation"
}}

Rules:
- If the input is a real location, city, region, or tourist destination, mark valid true.
- If it is ambiguous or misspelled, mark valid false and provide up to 5 similar valid destinations.
- If it does not exist, return valid false with useful alternatives.

Input location: {location}
""".strip()

    response = model.generate_content(prompt)
    parsed = _extract_json(getattr(response, "text", "") or "")
    if parsed is None:
        return _demo_location_validation(location)
    return parsed


def _generate_itinerary_with_gemini(payload: Dict[str, Any]) -> Dict[str, Any]:
    model = _gemini_model()
    location = str(payload.get("location", "")).strip()
    days = int(payload.get("days") or 1)
    people = int(payload.get("people") or 1)
    preferences = str(payload.get("preferences") or "").strip()
    budget = payload.get("budget")

    if model is None:
        return _demo_itinerary(location, days, people, preferences, budget)

    prompt = f"""
You are a world-class travel planner and historian creating a detailed day-wise itinerary for a Food & Travel Assistant covering {location}.

Return ONLY valid JSON with this EXACT structure (no extra text):

{{
  "location": "{location}",
  "days": {days},
  "people": {people},
  "budget": "{_budget_label(budget)}",
  "preferences": "{preferences or 'sightseeing and local cuisine'}",
  "summary": "Brief overall trip summary",
  "days_plan": [
    {{
      "food": {{
        "day": 1,
        "title": "Day 1 - Food Trail",
        "theme": "Culinary Experience",
        "summary": "Food-focused activities",
        "morning": {{
          "title": "Morning",
          "timestamp": "7:00 AM - 10:00 AM",
          "description": "Start with breakfast",
          "food": [
            {{
              "name": "Dish Name at Restaurant Name",
              "cuisine": "Cuisine type",
              "description": "DETAILED description: What is this dish? When was it created? What makes it special? Why is it famous in {location}? What ingredients are used? Why do people love it? (2-3 sentences minimum)",
              "cost": "₹XXX - ₹YYY",
              "image": "https://source.unsplash.com/800x600/?DishName,food"
            }}
          ]
        }},
        "afternoon": {{
          "title": "Afternoon",
          "timestamp": "12:30 PM - 4:00 PM",
          "description": "Lunch and snacks",
          "food": [
            {{
              "name": "Dish Name at Restaurant Name",
              "cuisine": "Cuisine type",
              "description": "DETAILED description with history, origin, ingredients, and why it's famous (2-3 sentences)",
              "cost": "₹XXX - ₹YYY",
              "image": "https://source.unsplash.com/800x600/?DishName,food"
            }}
          ]
        }},
        "evening": {{
          "title": "Evening",
          "timestamp": "6:00 PM - 11:00 PM",
          "description": "Dinner and desserts",
          "food": [
            {{
              "name": "Dish Name at Restaurant Name",
              "cuisine": "Cuisine type",
              "description": "DETAILED description with background and significance (2-3 sentences)",
              "cost": "₹XXX - ₹YYY",
              "image": "https://source.unsplash.com/800x600/?DishName,food"
            }}
          ]
        }}
      }},
      "places": {{
        "day": 1,
        "title": "Day 1 - Famous Places",
        "theme": "Sightseeing",
        "summary": "Tourist attractions",
        "morning": {{
          "title": "Morning",
          "timestamp": "8:00 AM - 12:00 PM",
          "description": "Start with main attraction",
          "places": [
            {{
              "name": "Landmark/Place Name",
              "description": "COMPREHENSIVE DESCRIPTION: When was it built? Who built it? What historical period? What is it famous for? What are the main attractions inside or around it? Why do millions visit it? What architectural style? What makes it unique? (3-4 sentences minimum)",
              "cost": "₹XXX - ₹YYY",
              "image": "https://source.unsplash.com/800x600/?LandmarkName,architecture"
            }}
          ]
        }},
        "afternoon": {{
          "title": "Afternoon",
          "timestamp": "1:00 PM - 5:00 PM",
          "description": "Secondary attractions",
          "places": [
            {{
              "name": "Place Name",
              "description": "COMPREHENSIVE historical and cultural description with details about its significance (3-4 sentences)",
              "cost": "₹XXX - ₹YYY",
              "image": "https://source.unsplash.com/800x600/?PlaceName,landmark"
            }}
          ]
        }},
        "evening": {{
          "title": "Evening",
          "timestamp": "6:00 PM - 9:00 PM",
          "description": "Sunset and evening experiences",
          "places": [
            {{
              "name": "Sunset Point or Evening Attraction",
              "description": "COMPREHENSIVE description about the location, best time to visit, what to see, and why it's special (3-4 sentences)",
              "cost": "₹XXX - ₹YYY",
              "image": "https://source.unsplash.com/800x600/?Sunset,evening"
            }}
          ]
        }}
      }}
    }}
  ]
}}

CRITICAL REQUIREMENTS:

FOR PLACES/LANDMARKS - Description must include:
- When it was built/established and what era/period
- Who built it (rulers, architects, communities)
- Historical significance and events
- What makes it architecturally or culturally unique
- Main attractions and what visitors can see
- Why it's famous and attracts millions of tourists
- Best time to visit and estimated time needed
(Each description should be 3-4 detailed sentences)

FOR FOOD/DISHES - Description must include:
- History and origin of the dish
- When it was created and by whom
- Traditional ingredients and preparation method
- What makes it special and authentic in {location}
- Why it's a must-try and what the locals recommend
- Flavor profile and best way to enjoy it
(Each description should be 2-3 detailed sentences)

IMAGE URLS MUST BE:
- From Unsplash using this format: https://source.unsplash.com/800x600/?keyword
- Must work and return actual images
- Use relevant keywords separated by commas

OTHER REQUIREMENTS:
1. Generate exactly {days} days of itinerary
2. For FOOD items: Use format "Dish Name at Restaurant Name"
3. For PLACES: Use actual landmark/attraction names that exist in {location}
4. Include realistic costs for {_budget_label(budget)} budget and {people} people
5. Include specific timestamps for each time slot
6. Make recommendations unique for {location}
7. Prefer well-known, established venues
8. Focus on DETAILED, INFORMATIVE descriptions
9. Every description must educate the traveler

Trip Details:
- Location: {location}
- Days: {days}
- People: {people}
- Budget: {_budget_label(budget)}
- Preferences: {preferences or 'sightseeing and local cuisine'}
""".strip()

    try:
        response = model.generate_content(prompt)
        text = getattr(response, "text", "") or ""
        parsed = _extract_json(text)
        if parsed and isinstance(parsed, dict) and "days_plan" in parsed:
            return parsed
    except Exception as e:
        print(f"Gemini API error: {e}")
    
    return _demo_itinerary(location, days, people, preferences, budget)


def _chat_response_with_gemini(payload: Dict[str, Any]) -> Dict[str, Any]:
    model = _gemini_model()
    message = str(payload.get("message", "")).strip()
    trip_context = payload.get("tripContext") or {}
    history = payload.get("history") or []

    if model is None:
        location = str(trip_context.get("location") or "your destination").strip()
        if "cheaper" in message.lower():
            reply = f"For {location}, I would switch to local breakfast spots, public transit, and one paid attraction per day to keep costs down."
        elif "beach" in message.lower():
            reply = f"A beach day in {location} works best with a relaxed morning slot, seafood lunch, and a sunset walk."
        elif "street food" in message.lower():
            reply = f"Look for busy local markets and evening food lanes in {location}; that usually gives the best street-food picks."
        else:
            reply = f"I can refine the plan for {location}. Ask me to adjust cost, food focus, pace, or sightseeing style."
        return {"reply": reply, "suggested_action": None}

    prompt = f"""
You are a helpful travel-planning chatbot for a Food & Travel Assistant.

Trip context:
{json.dumps(trip_context, ensure_ascii=False, indent=2)}

Conversation history:
{json.dumps(history, ensure_ascii=False, indent=2)}

User message: {message}

Return JSON only with this shape:
{{
  "reply": "short helpful answer",
  "suggested_action": "optional short action or null"
}}

Rules:
- Keep continuity with the trip context.
- If the user asks for a change, describe the adjustment clearly.
- If the user asks for cheaper alternatives, prefer budget-friendly swaps.
- Keep the answer concise and practical.
""".strip()

    response = model.generate_content(prompt)
    parsed = _extract_json(getattr(response, "text", "") or "")
    if parsed is None:
        return {"reply": "I could not parse the Gemini response. Please try again.", "suggested_action": None}
    return parsed


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/validate-location")
def validate_location():
    payload = request.get_json(silent=True) or {}
    location = str(payload.get("location", "")).strip()

    if not location:
        return jsonify({"error": "Location is required."}), 400

    result = _validate_location_with_gemini(location)
    return jsonify(result)


@app.post("/generate-itinerary")
def generate_itinerary():
    payload = request.get_json(silent=True) or {}
    location = str(payload.get("location", "")).strip()
    days = int(payload.get("days") or 0)
    people = int(payload.get("people") or 0)

    if not location:
        return jsonify({"error": "Location is required."}), 400
    if days < 1:
        return jsonify({"error": "Number of days must be at least 1."}), 400
    if people < 1:
        return jsonify({"error": "Number of people must be at least 1."}), 400

    itinerary = _generate_itinerary_with_gemini(payload)
    return jsonify({"itinerary": itinerary})


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    response = _chat_response_with_gemini(payload)
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
