
from datetime import datetime

import requests
import threading
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor


class ThreadSafeCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1

    def get_count(self):
        with self.lock:
            return self.count

def check_links(url, visited_links, filtered_domains,counter):
    # Add the current URL to the visited links list
    counter.increment()
    print(f"{counter.get_count()}. Checking link: {url}")
    if url not in visited_links:
        visited_links.add(url)
        try:
            # Send a GET request to the URL
            response = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
            # Check the response status code
            if response.status_code == 200:
                print(f"{counter.get_count()}::{datetime.now()} Link OK: {url}")
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all anchor tags in the HTML
                anchor_tags = soup.find_all('a')

                with ThreadPoolExecutor() as executor:
                    futures = []

                    for tag in anchor_tags:
                        # Get the href attribute of each anchor tag
                        href = tag.get('href')

                        # Make sure the href is not None and not an anchor link
                        if href is not None and not href.startswith('#'):
                            # Join the href with the base URL to get the absolute URL
                            absolute_url = urljoin(url, href)

                            # Check if the absolute URL is within the filtered domains
                            if any(domain in absolute_url for domain in filtered_domains):
                                # Check if the absolute URL has already been visited
                                if absolute_url not in visited_links:
                                    # Submit the link checking task to the executor
                                    futures.append(executor.submit(check_links, absolute_url, visited_links, filtered_domains,counter))

                    # Wait for all tasks to complete
                    for future in futures:
                        future.result()
            else:
                print(f"Link not OK: {url}")
                print(f"Response: {response}")

        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occur during the request
            print(f"An error occurred while checking {url}: {e}")
    else:
        print(f"Link already visited: {url}")


# Example usage
starting_url = 'https://crawler-test.com'
visited = set()
filtered_domains = ['crawler-test.com']
counter = ThreadSafeCounter()

check_links(starting_url, visited, filtered_domains,counter)

print("\n\n\n\nVisited Links:",len(visited))
for link in visited:
    print(link)

#write to file
with open('visited.txt', 'w') as f:
    for item in visited:
        f.write("%s\n" % item)