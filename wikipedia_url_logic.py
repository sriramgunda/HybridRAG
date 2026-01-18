import requests
import time
 
BASE_URL = "https://en.wikipedia.org/w/api.php"
 
TARGET_COUNT = 300

BATCH_SIZE = 10   # Wikipedia API limit per request
 
params = {

    "action": "query",

    "format": "json",

    "list": "random",

    "rnnamespace": 0,   # Main article namespace

    "rnlimit": BATCH_SIZE

}
 
unique_urls = set()

# Use a session with a descriptive User-Agent so Wikimedia doesn't block us
session = requests.Session()
session.headers.update({
    "User-Agent": "MyWikiCollector/1.0 (contact: dev@example.com)",
    "From": "dev@example.com",
})
 
while len(unique_urls) < TARGET_COUNT:

    # polite retry loop for transient errors (including occasional 403 if UA missing)
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = session.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            break
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else getattr(response, 'status_code', None)
            if status == 403:
                print("ERROR: 403 Forbidden from Wikimedia API — ensure User-Agent identifies your app and includes contact info.")
                raise
            if attempt == max_attempts:
                raise
            backoff = 0.5 * attempt
            time.sleep(backoff)
 
    for page in data["query"]["random"]:

        title = page["title"]

        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

        unique_urls.add(url)
 
    print(f"Collected: {len(unique_urls)} URLs")
 
    # Be polite to the API

    time.sleep(0.2)
 
# Convert to list if needed

wiki_urls = list(unique_urls)
 
# Save to file

with open("wikipedia_urls_300.txt", "w", encoding="utf-8") as f:

    f.write("\n".join(wiki_urls))
 