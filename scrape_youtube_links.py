import requests
from bs4 import BeautifulSoup
import re
import argparse
import logging

def get_links_from_page(url):
    youtube_link_pattern = re.compile(r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})')

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the response is not successful
        soup = BeautifulSoup(response.content, 'html.parser')

        youtube_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('http'):
                match = youtube_link_pattern.match(href)
                if match:
                    youtube_links.append(href)

        return youtube_links
    except requests.exceptions.RequestException as e:
        logging.error("Error while making the request: %s", str(e))
        return []

def main():
    logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

    parser = argparse.ArgumentParser(description="Get YouTube links from a webpage.")
    parser.add_argument("page_url", help="URL of the page to extract links from")
    parser.add_argument("-s", "--silent", action="store_true", default=False, help="Suppress output to the console")
    parser.add_argument("-o", "--output", help="Output filename to save the links")
    args = parser.parse_args()

    links = get_links_from_page(args.page_url)

    if args.output:
        with open(args.output, "w") as output_file:
            for link in links:
                output_file.write(link + "\n")

    if not args.silent:
        for link in links:
            print(link)

if __name__ == "__main__":
    main()
