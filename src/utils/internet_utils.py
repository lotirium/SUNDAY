import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import re
import time

class InternetUtils:
    """Utility class for internet access capabilities."""
    
    def __init__(self, api_key=None):
        """Initialize internet utilities with optional API keys."""
        # For Google Search API (if provided)
        self.serpapi_key = api_key or os.environ.get("SERPAPI_KEY")
        
        # Default headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Cache to avoid repeating the same requests
        self.cache = {}
        self.cache_expiry = 600  # Cache expiry in seconds (10 minutes)
    
    def search_web(self, query, num_results=5):
        """Search the web for information using SerpAPI if available, or fallback to scraping."""
        cache_key = f"search_{query}_{num_results}"
        
        # Check cache
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                return cache_data
        
        results = []
        
        # Try SerpAPI if key is available
        if self.serpapi_key:
            try:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": self.serpapi_key,
                    "num": num_results
                }
                response = requests.get('https://serpapi.com/search', params=params)
                data = response.json()
                
                if 'organic_results' in data:
                    for result in data['organic_results'][:num_results]:
                        results.append({
                            'title': result.get('title', 'No Title'),
                            'link': result.get('link', '#'),
                            'snippet': result.get('snippet', 'No description available')
                        })
                
                # Cache the results
                self.cache[cache_key] = (time.time(), results)
                return results
            except Exception as e:
                print(f"SerpAPI error: {str(e)}")
                # Fall back to scraping
        
        # Fallback method: Basic web scraping with a search engine
        # Note: This is a simplified version and might not work with all search engines
        # due to anti-scraping measures
        try:
            # Using DuckDuckGo as it's more scraping-friendly
            search_url = f"https://lite.duckduckgo.com/lite/?q={query}"
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract results from DuckDuckGo Lite
                for idx, result in enumerate(soup.select('a[href^="http"]')):
                    if idx >= num_results:
                        break
                    
                    title = result.get_text().strip()
                    link = result.get('href')
                    
                    # Skip if it doesn't look like a valid result
                    if not title or not link or link.startswith('/'):
                        continue
                    
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': 'Description not available'
                    })
            
            # Cache the results
            self.cache[cache_key] = (time.time(), results)
            return results
        except Exception as e:
            return [{'title': 'Search Error', 'link': '#', 'snippet': f"Error performing search: {str(e)}"}]
    
    def fetch_webpage_content(self, url, max_length=2000):
        """Fetch content from a webpage and extract main text."""
        cache_key = f"webpage_{url}"
        
        # Check cache
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                return cache_data
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text
                text = soup.get_text()
                
                # Break into lines and remove leading and trailing space on each
                lines = (line.strip() for line in text.splitlines())
                
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                
                # Join the lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Truncate if too long
                if len(text) > max_length:
                    text = text[:max_length] + "..."
                
                # Cache result
                self.cache[cache_key] = (time.time(), text)
                return text
            else:
                return f"Error: Received status code {response.status_code}"
        except Exception as e:
            return f"Error fetching webpage: {str(e)}"
    
    def get_weather(self, location):
        """Get weather information for a location."""
        cache_key = f"weather_{location}"
        
        # Check cache
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                return cache_data
        
        try:
            # Using OpenWeatherMap API
            api_key = os.environ.get("OPENWEATHERMAP_KEY")
            if not api_key:
                return "Weather API key not configured."
            
            url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                weather_info = {
                    'location': f"{data['name']}, {data.get('sys', {}).get('country', '')}",
                    'temperature': f"{data['main']['temp']}°C",
                    'feels_like': f"{data['main']['feels_like']}°C",
                    'description': data['weather'][0]['description'],
                    'humidity': f"{data['main']['humidity']}%",
                    'wind_speed': f"{data['wind']['speed']} m/s",
                    'time': datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S UTC')
                }
                
                # Cache result
                self.cache[cache_key] = (time.time(), weather_info)
                return weather_info
            else:
                return f"Weather lookup failed with status code: {response.status_code}"
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    def get_news(self, topic="general", count=5):
        """Get latest news headlines."""
        cache_key = f"news_{topic}_{count}"
        
        # Check cache
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                return cache_data
        
        try:
            # Using NewsAPI
            api_key = os.environ.get("NEWSAPI_KEY")
            if not api_key:
                return "News API key not configured."
            
            url = f"https://newsapi.org/v2/top-headlines?category={topic}&language=en&pageSize={count}&apiKey={api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'ok':
                    articles = []
                    for article in data['articles']:
                        articles.append({
                            'title': article['title'],
                            'source': article['source']['name'],
                            'description': article.get('description', 'No description available'),
                            'url': article['url'],
                            'published_at': article['publishedAt']
                        })
                    
                    # Cache result
                    self.cache[cache_key] = (time.time(), articles)
                    return articles
                else:
                    return "Failed to fetch news data"
            else:
                return f"News API request failed with status code: {response.status_code}"
        except Exception as e:
            return f"Error getting news: {str(e)}"
    
    def check_stock(self, symbol):
        """Get stock information."""
        cache_key = f"stock_{symbol}"
        
        # Check cache - shorter expiry for stock data
        stock_cache_expiry = 300  # 5 minutes
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < stock_cache_expiry:
                return cache_data
        
        try:
            # Using Alpha Vantage API
            api_key = os.environ.get("ALPHAVANTAGE_KEY")
            if not api_key:
                return "Stock API key not configured."
            
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Global Quote' in data and data['Global Quote']:
                    quote = data['Global Quote']
                    stock_info = {
                        'symbol': quote.get('01. symbol', symbol),
                        'price': quote.get('05. price', 'N/A'),
                        'change': quote.get('09. change', 'N/A'),
                        'change_percent': quote.get('10. change percent', 'N/A'),
                        'volume': quote.get('06. volume', 'N/A'),
                        'last_trading_day': quote.get('07. latest trading day', 'N/A')
                    }
                    
                    # Cache result
                    self.cache[cache_key] = (time.time(), stock_info)
                    return stock_info
                else:
                    return f"No stock data found for {symbol}"
            else:
                return f"Stock API request failed with status code: {response.status_code}"
        except Exception as e:
            return f"Error getting stock data: {str(e)}"