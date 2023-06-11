import json
import re
from urllib.parse import quote

import requests

HTML_TAG_CLEANER = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
THEMES = ["food","architecture","safaris_wildlife","outdoor","local_culture","city_sightseeing","nature","water_activities","art","water_sports"]
AUDIENCES = ["activities_for_couples","children_s_activities"]
POI_TYPES = ["religious","museum","historic_and_archeological","plaza_square","national_park","park_or_garden","castle_or_palace","landmark","river","beach"]
TRANSPORTATION_TYPES = ["van","car","bus_coach","sightseeing_cruise","jeep_suv","speed_boat","on_foot","bicycle"]

## https://travelers-api.getyourguide.com/search/v2/search?p=1&themes=food,architecture,safaris_wildlife,outdoor,local_culture,city_sightseeing,nature,water_activities,art,water_sports&audiences=activities_for_couples,children_s_activities&poiTypes=religious,museum,historic_and_archeological,plaza_square,national_park,park_or_garden,castle_or_palace,landmark,river,beach&transportationTypes=van,car,bus_coach,sightseeing_cruise,jeep_suv,speed_boat,on_foot,bicycle&size=16&sortBy=popularity


def find_things_to_do(query: str, num_results: int = 20, start_date: str = None, end_date: str = None, category: str = None) -> str | list[str]:
    """Return the results of a GetYourGuide search
    Args:
        query (str): The search query.
        num_results (int): The number of results to return.
        start_date (str): The start date to find available activities. Date formatting is yyyy-mm-dd.
        end_date (str): The last date to find available activities. Date formatting is yyyy-mm-dd
        category: A comma separated list of strings from the THEMES array
    Returns:
        str: The results of the search. The resulting string is a `json.dumps`
             of a list of len `num_results` containing dictionaries with the
             following structure: `{'title': <title>, ‘price’: <price>, 'availability': <next available date and time>, 
             'review_rating': <score>, 'number_of_reviews': <number>,
             'description': <short description>],
             'category': <category name of the activity>,
             'activity_id': <internal id of the activity>,
             'url': <url to relevant page>}`
             
    """
    
    search_url = (
        "https://travelers-api.getyourguide.com/search/v2/search?" +
        "searchSource=3&sortBy=popularity&" +
        f"q={quote(query)}" +
        (f"&themes={category}" if category else "") +
        (f"&startDate={start_date}" if start_date else "") +
        (f"&endDate={end_date}" if end_date else "")
    )
    
    print("url:")
    print(search_url)
    
   
    with requests.Session() as session:
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; "
                    "Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/"
                    "112.0.5615.49 Safari/537.36"
                )
            }
        )
        session.headers.update({"Accept": "application/json"})
        ## currency required by API
        session.headers.update({"Accept-Currency": "USD"})

        results = session.get(search_url)

        items = []
        try:
            results = results.json()
            for item in results["items"]:
                items.append(
                    {
                        "title": item["title"],
                        "Price": item["price"]["startingPrice"],
                        "availability": item["availability"]["nextAvailableDateTime"],
                        "review_rating": item["reviewStatistics"]["rating"],
                        "number_of_reviews": item["reviewStatistics"]["quantity"],
                        "description": item["abstract"],
                        "category_label": item["categoryLabel"] if "categoryLabel" in item else None,
                        "activity_id": item["id"],
                        "url": f"http://getyourguide.com{item['url']}",                    }
                )
                if len(items) == num_results:
                    break
        except Exception as e:
            return f"’find_things_to_do' on query: {query} raised exception: {e}"

    return json.dumps(items, ensure_ascii=False, indent=4)
    
