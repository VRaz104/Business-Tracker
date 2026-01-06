# Business-Tracker
Local Business Finder (OpenStreetMap)
A Python script that finds real-world local businesses in any city using OpenStreetMap data and exports the results to structured JSON.

What Problem This Solves
Finding reliable, structured data about local businesses is harder than it should be.
Most sources are either:
  -Paid APIs (Google Places, Yelp)
  -Rate-limited
  -Locked behind accounts
  -Not easily exportable
This script solves that by:
  -Using OpenStreetMap (OSM), a free and open global dataset
  -Converting a city name into coordinates
  -Searching for nearby businesses by type
  -Exporting clean, reusable JSON data
  -Logging every step for transparency and debugging
No API keys. No accounts. No scraping.

Who This Is For
This tool is useful for:

  -Python beginners learning real-world scripting

  -Developers building datasets for:
  -> Market research
  -> Local business analysis
  -> Data science projects
  -Indie hackers and automation builders
  -Anyone who wants free, structured business data
If you are learning Python and APIs, this script shows:
  -API usage
  -Error handling
  -Retries
  -Logging
  -JSON output
  -Clean program structure

How It Works (High Level)
1. User enters a city name
2. City is converted into latitude/longitude using OpenStreetMap (Nominatim)
3. Businesses are searched within a 10 km radius using Overpass API
4. Results are filtered, normalized, and saved to JSON
5. A detailed log file is generated

#INSTALLATION
Requirements
  -Python 3.8+
  -Internet connection

Install Dependencies
pip install requests

Clone the Repository
git clone https://github.com/VRaz104/local-business-finder.git
cd local-business-finder

Now to run the Script you just need to type the following commands in the terminal after downloading the script:
```bash
pip install requests
```

```bash
git clone https://github.com/yourusername/local-business-finder.git
cd local-business-finder
```

```bash
python business_finder.py
```

#EXAMPLE
```JSON
{
  "search": {
    "city": "Berlin",
    "business_type": "cafe",
    "limit": 10,
    "coordinates": {
      "latitude": 52.517,
      "longitude": 13.3889
    }
  },
  "created_at": "2026-01-06T14:21:33+00:00",
  "businesses": [
    {
      "name": "Five Elephant",
      "business_type": "cafe",
      "location": {
        "latitude": 52.4991,
        "longitude": 13.4312
      },
      "address": {
        "street": "Reichenberger Straße",
        "city": "Berlin"
      },
      "phone": "+49 30 123456",
      "website": "https://fiveelephant.com"
    }
  ]
}

```
