import requests
from time import sleep

# Read API key
with open(".credentials", "r") as f:
    key = f.read().strip("\n")
    
# create a set to keep track of already seen articles
seen = set()

while True:
    
    # Limit to articles published in the last 24 hours, query limit is 20 anyways...
    url = f'https://api.nytimes.com/svc/news/v3/content/all/all/24.json?api-key={key}'

    r = requests.get(url)

    while r.status_code != 200:
        print(f"Something wrong happened... Error code: {r.status_code}. Retrying...")
        sleep(10)

    data = r.json()

    for article in data["results"]:
        if article['title'] not in seen:
            print("Found a new article!")

            print(f"It is called {article['title']}")

            seen.add(article['title'])
                  
            with open("some_data.txt", "a") as outfile:
                outfile.write(str(article) + "\n")
                  
    sleep(120)