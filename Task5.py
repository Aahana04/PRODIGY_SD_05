"""
Amazon Product Scraper

IMPORTANT DISCLAIMERS:
1. This script is for educational purposes only
2. Web scraping may violate Amazon's Terms of Service
3. Amazon actively blocks automated requests - this script may not work consistently
4. Amazon frequently changes their HTML structure, breaking scrapers
5. Consider using Amazon's official API for production applications
6. Use responsibly and respect rate limits

COMMON ISSUES:
- 403 Forbidden errors: Amazon detected automated requests
- Empty results: Amazon changed their page structure or blocked the request
- Slow performance: Intentional delays to avoid being blocked
"""

import requests
from bs4 import BeautifulSoup
import csv
from time import sleep
from random import randint
import re

# Set headers to mimic a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def scrape_amazon_products(search_query, pages=1):
    """Scrape Amazon product data for a given search query"""
    
    base_url = 'https://www.amazon.com'
    products = []
    
    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")
        
        # Construct the search URL
        url = f"{base_url}/s?k={search_query}&page={page}"
        
        try:
            # Make the request
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch page {page}. Status code: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all product containers - try multiple selectors
            items = (soup.find_all('div', {'data-component-type': 's-search-result'}) or
                    soup.find_all('div', class_='s-result-item') or
                    soup.find_all('div', {'data-asin': True}))
            
            if not items:
                print(f"No products found on page {page}. Amazon may have changed their structure.")
                continue
                
            print(f"Found {len(items)} products on page {page}")
            
        except requests.RequestException as e:
            print(f"Request failed for page {page}: {e}")
            continue
        except Exception as e:
            print(f"Error processing page {page}: {e}")
            continue
        
        for item in items:
            try:
                # Extract product name
                name_tag = item.find('h2', class_='a-size-mini') or item.find('h2') or item.find('span', class_='a-size-medium')
                if name_tag:
                    name = name_tag.get_text().strip()
                else:
                    name = 'N/A'
                
                # Extract price - try multiple selectors
                price = 'N/A'
                price_container = item.find('span', class_='a-price')
                if price_container:
                    price_whole = price_container.find('span', class_='a-price-whole')
                    price_fraction = price_container.find('span', class_='a-price-fraction')
                    if price_whole and price_fraction:
                        price = f"${price_whole.text.strip()}.{price_fraction.text.strip()}"
                    else:
                        price_range = price_container.find('span', class_='a-price-range')
                        if price_range:
                            price = price_range.get_text().strip()
                
                # Extract rating
                rating = 'N/A'
                rating_tag = item.find('span', class_='a-icon-alt')
                if rating_tag:
                    rating_text = rating_tag.get_text()
                    rating_match = re.search(r'(\d\.\d)', rating_text)
                    if rating_match:
                        rating = rating_match.group(1)
                
                # Extract number of reviews
                reviews = '0'
                # Try multiple selectors for reviews
                reviews_tag = (item.find('span', class_='a-size-base') or 
                             item.find('a', class_='a-link-normal') or
                             item.find('span', {'data-testid': 'reviews-count'}))
                if reviews_tag:
                    reviews_text = reviews_tag.get_text().strip()
                    # Extract numbers from reviews text
                    reviews_match = re.search(r'([\d,]+)', reviews_text)
                    if reviews_match:
                        reviews = reviews_match.group(1).replace(',', '')
                
                # Extract product URL
                product_url = 'N/A'
                link_tag = item.find('a', class_='a-link-normal')
                if link_tag and link_tag.get('href'):
                    relative_url = link_tag.get('href')
                    product_url = f"{base_url}{relative_url}"
                
            except Exception as e:
                print(f"Error extracting data from item: {e}")
                continue
            
            # Only add products with valid names
            if name != 'N/A' and len(name.strip()) > 0:
                products.append({
                    'name': name,
                    'price': price,
                    'rating': rating,
                    'reviews': reviews,
                    'url': product_url
                })
            
        # Random delay to avoid being blocked
        sleep(randint(2, 4))
    
    return products

def save_to_csv(products, filename):
    """Save scraped product data to a CSV file"""
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'price', 'rating', 'reviews', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for product in products:
                writer.writerow(product)
        
        print(f"Data saved to {filename}")
        print(f"Total products saved: {len(products)}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    print("Amazon Product Scraper")
    print("Note: This is for educational purposes only. Please respect Amazon's terms of service.")
    print("-" * 60)
    
    try:
        # Example: Scrape data for "wireless headphones" from first 2 pages
        search_term = input("Enter product to search for: ").strip()
        if not search_term:
            print("No search term provided. Exiting.")
            exit()
        
        search_term = search_term.replace(' ', '+')
        pages_to_scrape = int(input("Enter number of pages to scrape (1-5 recommended): "))
        
        if pages_to_scrape <= 0 or pages_to_scrape > 10:
            print("Please enter a number between 1 and 10.")
            exit()
        
        print(f"\nStarting to scrape {pages_to_scrape} page(s) for '{search_term.replace('+', ' ')}'...")
        
        scraped_data = scrape_amazon_products(search_term, pages=pages_to_scrape)
        
        if scraped_data:
            output_filename = f"{search_term.replace('+', '_')}_products.csv"
            save_to_csv(scraped_data, output_filename)
            print(f"\nScraping completed successfully!")
        else:
            print("No data was scraped. This might be due to:")
            print("1. Amazon blocking the request")
            print("2. No products found for the search term")
            print("3. Amazon changed their page structure")
            print("4. Network connectivity issues")
            
    except ValueError:
        print("Please enter a valid number for pages.")
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")