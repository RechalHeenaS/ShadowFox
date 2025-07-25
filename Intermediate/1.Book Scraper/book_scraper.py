import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = "https://books.toscrape.com/catalogue/"

def get_soup(url):
    """Returns a BeautifulSoup object of the given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Error: Unable to fetch page {url}")
        return None

def get_books_from_page(soup):
    """Extract book title and price from a single page soup."""
    books = []
    articles = soup.find_all('article', class_='product_pod')

    for article in articles:
        title = article.h3.a['title']
        price = article.find('p', class_='price_color').text.strip()
        books.append((title, price))

    return books

def get_next_page(soup):
    """Returns the full URL of the next page if available, else None."""
    next_btn = soup.find('li', class_='next')
    if next_btn:
        next_page = next_btn.a['href']
        return CATALOGUE_URL + next_page
    return None

def scrape_books():
    """Scrapes all pages and stores book data to books.csv."""
    url = CATALOGUE_URL + "page-1.html"
    all_books = []

    while url:
        print(f"📄 Scraping: {url}")
        soup = get_soup(url)
        if soup:
            books = get_books_from_page(soup)
            all_books.extend(books)
            url = get_next_page(soup)
        else:
            break

    # Save results to CSV
    with open("books.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price"])
        writer.writerows(all_books)

    print("✅ Done! Data saved to 'books.csv'.")

# Run the scraper
if __name__ == "__main__":
    scrape_books()
