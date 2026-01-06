import requests
from datetime import datetime, timezone
import json
import time
import logging
logging.basicConfig(
    filename='business_search.log',  
    level=logging.INFO,  
    format='%(asctime)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)
CITY_LOOKUP_URL = "https://nominatim.openstreetmap.org/search"
BUSINESS_LOOKUP_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {
    "User-Agent": "SimpleLocalBusinessParser/1.0"
}
def get_city_coordinates(city_name):
    params = {
        "q": city_name,
        "format": "json",
        "limit": 1
    }
    time.sleep(1) 
    try:
        logging.info(f"\nLooking up coordinates for: {city_name}")
        response = requests.get(CITY_LOOKUP_URL, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json() 
        if not data:
            logging.warning(f"City '{city_name}' not found in database")
            print(f"City '{city_name}' not found")
            return None 
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        logging.info(f"Found {city_name} at coordinates: {lat}, {lon}")
        print(f"Found coordinates for {city_name}: {lat}, {lon}")
        return lat, lon
    except requests.exceptions.Timeout:
        logging.error(f"Timed out while searching for {city_name}")
        print("Connection timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        logging.error(f"No internet connection when searching for {city_name}")
        print("No internet connection. Please check your network.")
        return None
    except Exception as e:
        logging.error(f"Error getting coordinates for {city_name}: {str(e)}")
        print(f"Error getting coordinates: {e}")
        return None
def get_businesses(latitude, longitude, business_type, max_results, max_retries=3):
    query = f"""
    [out:json][timeout:90];
    (
      node["amenity"="{business_type}"](around:10000,{latitude},{longitude});
      way["amenity"="{business_type}"](around:10000,{latitude},{longitude});
    );
    out center {max_results};
    """
    logging.info(f"Searching for {business_type} businesses at {latitude}, {longitude}")
    for attempt in range(max_retries):
        try:
            print(f"\nSearching... (attempt {attempt + 1}/{max_retries})")
            response = requests.post(BUSINESS_LOOKUP_URL, data={'data': query}, headers=HEADERS, timeout=120)
            response.raise_for_status()
            data = response.json()  
            businesses = []
            no_name_count = 0
            no_coords_count = 0  
            for element in data.get("elements", []):
                if len(businesses) >= max_results:
                    break       
                tags = element.get("tags", {})
                name = tags.get("name", "").strip()  
                if not name:
                    no_name_count += 1
                    continue  
                if element.get("type") == "node":
                    lat = element.get("lat")
                    lon = element.get("lon")
                elif element.get("type") == "way":
                    center = element.get("center", {})
                    lat = center.get("lat")
                    lon = center.get("lon")
                else:
                    continue      
                if lat is None or lon is None:
                    no_coords_count += 1
                    continue      
                business = {
                    "name": name,
                    "business_type": business_type,
                    "location": {
                        "latitude": lat,
                        "longitude": lon
                    },
                    "address": {
                        "street": tags.get("addr:street", ""),
                        "city": tags.get("addr:city", ""),
                    },
                    "phone": tags.get("phone", ""),
                    "website": tags.get("website", ""),
                }
                businesses.append(business)
            if businesses:
                logging.info(f"Found {len(businesses)} {business_type} businesses")
                if no_name_count > 0:
                    logging.info(f"Skipped {no_name_count} places without names")
                if no_coords_count > 0:
                    logging.info(f"Skipped {no_coords_count} places without coordinates")  
            print(f"Found {len(businesses)} businesses")
            return businesses  
        except requests.exceptions.Timeout:
            logging.warning(f"Search timed out on attempt {attempt + 1}")
            print(f"Search timed out. Retrying...")
            time.sleep(2)   
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 504:
                logging.warning(f"Server busy (504 error) on attempt {attempt + 1}")
                print(f"Server is busy. Retrying...")
                time.sleep(3)
            else:
                logging.error(f"HTTP error on attempt {attempt + 1}: {e}")
                print(f"Server error: {e}")
                if attempt == max_retries - 1:
                    return []
                time.sleep(2)       
        except Exception as e:
            logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            print(f"Error: {e}")
            if attempt == max_retries - 1:
                return []
            time.sleep(2)
    logging.error(f"Failed to find businesses after {max_retries} tries")
    print(f"Could not find businesses after {max_retries} attempts.")
    return []
def main():
    logging.info("\n")
    logging.info("=" * 50)
    logging.info("Program started")
    logging.info("=" * 50)
    print("\n" + "="*50)
    print("BUSINESS FINDER")
    print("="*50)
    while True:
        city_name = input("\nEnter city name: ").strip()     
        coordinates = get_city_coordinates(city_name)
        if coordinates is not None:
            latitude, longitude = coordinates
            logging.info(f"User selected city: {city_name}")
            break
        print("City not found. Please try again.")
    business_type = input("\nWhat type of business? (e.g., restaurant, cafe, bank): ").strip().lower()
    logging.info(f"User searching for: {business_type}")
    while True:
        try:
            limit = int(input(f"\nHow many {business_type}s to find? (1-50): "))
            if 1 <= limit <= 50:
                logging.info(f"User requested {limit} results")
                break
            print("Please enter a number between 1 and 50.")
        except ValueError:
            print("Please enter a number.")
    print(f"\n{'='*50}")
    print(f"Searching for {business_type}s in {city_name}...")
    print(f"{'='*50}")
    businesses = get_businesses(latitude, longitude, business_type, limit)
    result_data = {
        "search": {
            "city": city_name,
            "business_type": business_type,
            "limit": limit,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            }
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "businesses": businesses
    }
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"businesses.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as file:
            json.dump(result_data, file, indent=2, ensure_ascii=False)
        logging.info(f"Saved results to: {output_filename}")
        print(f"\n✓ Results saved to: {output_filename}")
        with open('business_search.log', 'a', encoding='utf-8') as log_file:
            log_file.write(f"\nResults saved to: {output_filename}\n")
            log_file.write(f"Found {len(businesses)} businesses in {city_name}\n")
            if businesses:
                log_file.write("Businesses found:\n")
                for business in businesses:
                    log_file.write(f"  - {business['name']}\n")    
    except IOError as e:
        logging.error(f"Failed to save results: {e}")
        print(f"\n✗ Error saving file: {e}")
    print(f"\n{'='*50}")
    print("Search complete! Check 'business_search.log' for details.")
    print(f"{'='*50}")
    logging.info("Program finished successfully")
if __name__ == "__main__":
    main()