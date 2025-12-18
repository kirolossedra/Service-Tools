import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote

def search_genius_lyrics(song_query):
    """
    Search for a song on Genius and get the lyrics URL and content.
    
    Args:
        song_query (str): Song name to search (e.g., "king of my heart bethel")
    
    Returns:
        dict: Contains 'url', 'title', and 'lyrics' if found
    """
    
    # Step 1: Build the search URL
    encoded_query = quote(song_query)
    search_url = f"https://genius.com/search?q={encoded_query}"
    
    print(f"Searching: {search_url}")
    
    # Step 2: Fetch the search results page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return None
    
    # Step 3: Parse HTML and find URLs ending with -lyrics
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links on the page
    lyrics_url = None
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Check if URL matches pattern: https://genius.com/...-lyrics
        if href.startswith('https://genius.com/') and href.endswith('-lyrics'):
            lyrics_url = href
            print(f"Found lyrics URL: {lyrics_url}")
            break
    
    if not lyrics_url:
        print("No lyrics URL found in search results")
        return None
    
    # Step 4: Fetch the lyrics page
    try:
        lyrics_response = requests.get(lyrics_url, headers=headers)
        lyrics_response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching lyrics page: {e}")
        return None
    
    # Step 5: Extract lyrics from the page
    lyrics_soup = BeautifulSoup(lyrics_response.text, 'html.parser')
    
    # Get title
    title_tag = lyrics_soup.find('title')
    title = title_tag.text if title_tag else "Unknown"
    
    # Find lyrics containers (Genius uses data-lyrics-container attribute)
    lyrics_containers = lyrics_soup.find_all('div', attrs={'data-lyrics-container': 'true'})
    
    if not lyrics_containers:
        # Fallback: try class-based selector
        lyrics_containers = lyrics_soup.find_all('div', class_=re.compile(r'Lyrics__Container'))
    
    if not lyrics_containers:
        print("Could not find lyrics in the page")
        return {
            'url': lyrics_url,
            'title': title,
            'lyrics': None
        }
    
    # Extract text from lyrics containers
    lyrics_text = []
    for container in lyrics_containers:
        # Replace <br> tags with newlines
        for br in container.find_all('br'):
            br.replace_with('\n')
        
        text = container.get_text()
        lyrics_text.append(text)
    
    lyrics = '\n\n'.join(lyrics_text).strip()
    
    return {
        'url': lyrics_url,
        'title': title,
        'lyrics': lyrics
    }


# Example usage
if __name__ == "__main__":
    # Test with the example
    song_name = "Firm foundation - maverick city"
    
    print(f"Searching for: {song_name}\n")
    result = search_genius_lyrics(song_name)
    
    if result:
        print(f"\n{'='*60}")
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"{'='*60}\n")
        
        if result['lyrics']:
            print("LYRICS:")
            print(result['lyrics'])
        else:
            print("Lyrics could not be extracted (but URL is available)")
    else:
        print("No results found")
    
    print("\n" + "="*60)
    print("Try other songs:")
    print("  - search_genius_lyrics('oceans hillsong')")
    print("  - search_genius_lyrics('goodness of god')")
    print("  - search_genius_lyrics('way maker sinach')")
