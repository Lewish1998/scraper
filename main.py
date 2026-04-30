#!/usr/bin/env python3
"""
Web scraper to extract Success Criterion headings and body content
from the W3.org Web Sustainability Guidelines.
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
from pathlib import Path


def scrape_success_criteria(url: str) -> list[dict]:
    """
    Scrape all Success Criterion headings and their body content from the given URL.
    
    Args:
        url: The URL to scrape
        
    Returns:
        A list of dictionaries containing 'heading' and 'body' for each criterion
    """
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    criteria = []
    
    # Find all sections that contain "Success Criterion:"
    for section in soup.find_all('section'):
        heading = section.find(['h2', 'h3', 'h4', 'h5', 'h6'])
        if heading and 'Success Criterion:' in heading.get_text():
            heading_text = heading.get_text(strip=True)
            
            # Extract body content from all elements in the section except the header
            body_content = []
            for element in section.find_all(['p', 'ul', 'ol', 'pre', 'blockquote', 'div'], recursive=True):
                # Skip elements that are inside the header-wrapper
                if element.find_parent('div', class_='header-wrapper'):
                    continue
                
                text = element.get_text(strip=True)
                if text and text.strip() not in [item.strip() for item in body_content]:  # Avoid duplicates
                    body_content.append(text)
            
            criteria.append({
                'heading': heading_text,
                'body': '\n\n'.join(body_content)
            })
    
    return criteria


def save_to_json(data: list[dict], output_file: str) -> None:
    """Save the scraped data to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} criteria to {output_file}")


def main():
    url = "https://w3.org/TR/web-sustainability-guidelines"
    output_file = "success_criteria.json"
    
    print("Starting scraper...")
    criteria = scrape_success_criteria(url)
    
    if criteria:
        save_to_json(criteria, output_file)
        print(f"\nFound {len(criteria)} Success Criteria")
        print("\nFirst criterion:")
        print(f"  {criteria[0]['heading'][:100]}...")
    else:
        print("No Success Criteria found.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
