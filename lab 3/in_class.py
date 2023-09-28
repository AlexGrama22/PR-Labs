import requests
from bs4 import BeautifulSoup

def scrape_links(max_pages, current_page, urls, found_links):
    base_url = "https://999.md"
    current_url = urls[current_page]

    response = requests.get(current_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extracting specific links
    for anchor in soup.find_all('a', href=True, class_='js-item-ad'):
        href = str(anchor.get('href'))
        if href[1] != 'b':
            complete_url = base_url + href
            found_links.add(complete_url)

    pagination_links = soup.select('nav.paginator > ul > li > a')
    for page_link in pagination_links:
        href = str(base_url + page_link['href'])
        if href not in urls:
            urls.append(href)

    if current_page == max_pages or current_page >= len(urls) - 1:
        return found_links
    else:
        return scrape_links(max_pages, current_page + 1, urls, found_links)

initial_urls = ["https://999.md/ro/list/phone-and-communication/drones"]
collected_links = scrape_links(1000, 0, initial_urls, set())


with open('links.txt', 'w') as file:
    for link in collected_links:
        file.write(link + '\n')

for link in collected_links:
    print(link)
