import os
import json
import time
import random
import re  # Add this line
from datetime import datetime
from openai import OpenAI
from .internet_utils import InternetUtils

class FridayAssistant:
    def __init__(self, api_key=None, serpapi_key=None, weather_key=None, news_key=None, stock_key=None):
        """Initialize Friday Assistant with API keys."""
        # OpenAI API key setup
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []
        
        # Initialize internet utilities
        self.internet = InternetUtils(serpapi_key)
        
        # Store other API keys in environment variables for the internet utils to use
        if weather_key:
            os.environ["OPENWEATHERMAP_KEY"] = weather_key
        if news_key:
            os.environ["NEWSAPI_KEY"] = news_key
        if stock_key:
            os.environ["ALPHAVANTAGE_KEY"] = stock_key
        
        # Set Friday's personality based on the Marvel character stooooooooooooooooooop
        self.system_message = """
        You are FRIDAY (Female Replacement Intelligent Digital Assistant Youth), Tony Stark's AI assistant from the Marvel universe.
        
        Your characteristics include:
        1. Practical, efficient and direct communication style
        2. Slightly sassy but always respectful
        3. Technical expertise and problem-solving focus
        4. Professional but with occasional humor
        5. Protective of your user's wellbeing
        
        Your responses should:
        - Be concise and information-dense
        - Include occasional references to your role as an advanced AI system
        - Use the occasional light technical jargon where appropriate
        - Address the user as "Boss" occasionally
        - Begin responses occasionally with phrases like "At your service, Boss" or "Working on it"
        - End important alerts with "Shall I activate the protocol?" or similar appropriate phrases
        
        You now have internet access capabilities. When the user requests information that requires real-time data or current events:
        - You can search the web for information
        - You can check weather, news, and stock information
        - You can analyze webpages to extract relevant details
        
        When providing this information, incorporate it naturally into your responses while maintaining your FRIDAY persona. If you've used one of your internet capabilities, briefly mention it (e.g., "I've scanned the web and found...").
        
        Always maintain your Marvel FRIDAY persona throughout the conversation.
        """
        
        # Add system message to conversation history
        self.conversation_history.append({"role": "system", "content": self.system_message})
        
        # Friday's greeting phrases
        self.greetings = [
            "Hello Boss. FRIDAY at your service. How can I assist you today?",
            "Systems online. How may I be of assistance?",
            "Good to see you. What do you need today?",
            "FRIDAY online and ready. What are we working on?",
            "At your service, Boss. How can I help you?"
        ]
        
        # Friday's acknowledgement phrases
        self.acknowledgements = [
            "Working on it, Boss.",
            "Processing your request.",
            "Analyzing now.",
            "On it.",
            "I'll take care of that."
        ]
    
    def get_greeting(self):
        """Return a random Friday greeting."""
        return random.choice(self.greetings)
    
    def get_acknowledgement(self):
        """Return a random acknowledgement phrase."""
        return random.choice(self.acknowledgements)
    
    def ask(self, user_input, callback=None):
        """Send user input to OpenAI and return Friday's response."""
        # Check for special commands that might need internet capabilities
        enhanced_input, internet_data = self._check_for_internet_queries(user_input)
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # If callback is provided, send acknowledgement
        if callback:
            callback(self.get_acknowledgement())
        
        try:
            # Prepare messages including internet data if applicable
            messages = self.conversation_history.copy()
            
            # If we have internet data, add it as a system message
            if internet_data:
                messages.append({
                    "role": "system", 
                    "content": f"I've accessed the internet and found this information: {internet_data}\n\nPlease incorporate this information into your response while maintaining your FRIDAY persona. Do not explicitly state that this came from a system message."
                })
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=1500,  # Increased tokens to handle more complex responses with internet data
                temperature=0.7,
            )
            
            # Extract assistant's reply
            assistant_reply = response.choices[0].message.content
            
            # Add assistant's reply to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            return assistant_reply
        except Exception as e:
            error_message = f"I'm experiencing a system error: {str(e)}. Shall I run diagnostics?"
            self.conversation_history.append({"role": "assistant", "content": error_message})
            return error_message
            
    def _check_for_internet_queries(self, user_input):
        """Check if the user input requires internet access and fetch relevant data."""
        user_input_lower = user_input.lower()
        internet_data = None
        
        # Check for weather queries
        weather_patterns = [
            r'weather\s+in\s+([a-zA-Z\s]+)',
            r'weather\s+(?:for|at)\s+([a-zA-Z\s]+)',
            r'what\'s\s+the\s+weather\s+(?:in|at|for)\s+([a-zA-Z\s]+)',
            r'how\'s\s+the\s+weather\s+(?:in|at|for)\s+([a-zA-Z\s]+)'
        ]
        
        for pattern in weather_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                location = match.group(1).strip()
                weather_data = self.internet.get_weather(location)
                if isinstance(weather_data, dict):
                    internet_data = f"Weather information for {weather_data['location']}: Temperature is {weather_data['temperature']} (feels like {weather_data['feels_like']}), {weather_data['description']}, humidity {weather_data['humidity']}, wind speed {weather_data['wind_speed']}."
                else:
                    internet_data = f"Weather lookup attempted but failed: {weather_data}"
                break
        
        # Check for news queries
        news_patterns = [
            r'(latest|recent|current)\s+news',
            r'news\s+(?:about|on)\s+([a-zA-Z\s]+)',
            r'what\'s\s+(?:happening|going\s+on)',
            r'current\s+events'
        ]

        for pattern in news_patterns:
            if re.search(pattern, user_input_lower) and not internet_data:
                topic_match = re.search(r'news\s+(?:about|on)\s+([a-zA-Z\s]+)', user_input_lower)
                topic = "general"
                if topic_match:
                    topic = topic_match.group(1).strip()
                
                news_data = self.internet.get_news(topic, 3)
                if isinstance(news_data, list) and news_data:
                    # Just collect the raw news data
                    news_text = "News data:\n"
                    for article in news_data:
                        news_text += f"Title: {article['title']}\n"
                        news_text += f"Source: {article['source']}\n"
                        news_text += f"Description: {article.get('description', 'No description available')}\n\n"
                    
                    # Add specific instructions for the model to process this data
                    internet_data = f"""
                    {news_text}
                    
                    INSTRUCTION: Using the news data above, create a natural, conversational summary of current events.
                    Do NOT use numbering, bullet points, or bold formatting in your response.
                    Speak as FRIDAY from Marvel, casually briefing Tony Stark on what's happening in the world.
                    Address the user as 'Boss' and maintain FRIDAY's helpful, slightly sassy personality.
                    Include 3-5 major news topics in your own words, not just repeating the headlines.
                    End with an offer to provide more details on any topic that might interest the user.
                    """
                else:
                    internet_data = f"News lookup attempted but failed: {news_data}"
                break
        
        # Check for stock queries
        stock_patterns = [
            r'stock\s+(?:price|value|info)?\s+(?:for|of)\s+([A-Za-z]+)',
            r'how\s+is\s+([A-Za-z]+)\s+stock',
            r'what\'s\s+([A-Za-z]+)\s+stock\s+(?:price|doing)'
        ]
        
        for pattern in stock_patterns:
            match = re.search(pattern, user_input_lower)
            if match and not internet_data:
                symbol = match.group(1).upper().strip()
                stock_data = self.internet.check_stock(symbol)
                if isinstance(stock_data, dict):
                    internet_data = f"Stock information for {stock_data['symbol']}: Current price ${stock_data['price']}, change {stock_data['change']} ({stock_data['change_percent']}), volume {stock_data['volume']}, last trading day {stock_data['last_trading_day']}."
                else:
                    internet_data = f"Stock lookup attempted but failed: {stock_data}"
                break
        
        # General web search for informational queries
        search_patterns = [
            r'search\s+(?:for|about)\s+([a-zA-Z0-9\s]+)',
            r'find\s+(?:info|information)\s+(?:about|on)\s+([a-zA-Z0-9\s]+)',
            r'who\s+is\s+([a-zA-Z\s]+)',
            r'what\s+is\s+([a-zA-Z0-9\s]+)',
            r'tell\s+me\s+about\s+([a-zA-Z0-9\s]+)',
            r'how\s+(?:to|do|does|can)\s+([a-zA-Z0-9\s]+)'
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, user_input_lower)
            if match and not internet_data:
                query = match.group(1).strip()
                search_results = self.internet.search_web(query, 3)
                
                if search_results and isinstance(search_results, list):
                    search_text = f"Web search results for '{query}':\n"
                    for i, result in enumerate(search_results):
                        search_text += f"{i+1}. {result['title']}: {result['snippet']}\n"
                    
                    # If we have a good first result, try to get more content
                    if search_results[0]['link'] != '#':
                        content = self.internet.fetch_webpage_content(search_results[0]['link'], 1500)
                        if content and not content.startswith("Error"):
                            search_text += f"\nDetails from top result:\n{content[:800]}..."
                    
                    internet_data = search_text
                break

        if internet_data:
            # Transform raw internet data into FRIDAY's voice
            if "Weather information for" in internet_data:
                location = internet_data.split("Weather information for ")[1].split(":")[0]
                details = internet_data.split(": ")[1]
                internet_data = f"I've analyzed atmospheric conditions for {location}, Boss. {details} Would you like me to set up a weather monitoring protocol?"
            
            elif "Recent news headlines" in internet_data:
                # Don't format the news data at all - just provide it as context
                news_raw = internet_data
                
                # Create a specific instruction for the model to analyze and summarize
                internet_data = f"""
                {news_raw}
                
                INSTRUCTION: Using the news data above, create a natural, conversational summary of current events.
                Do NOT use numbering, bullet points, or bold formatting in your response.
                Speak as FRIDAY from Marvel, casually briefing Tony Stark on what's happening in the world.
                
                For each news item:
                1. Explain it in simple, clear terms that are easy to understand
                2. Briefly mention what led to this situation (context)
                3. Add a short analysis of potential impacts or why it matters
                
                Make your analysis insightful but accessible - Boss values clarity and efficiency.
                Use FRIDAY's helpful, slightly sassy personality and address the user as 'Boss'.
                Include 3-4 major news topics only.
                End with an offer to provide more details on any topic that might interest the user.
                """
            elif "Stock information for" in internet_data:
                symbol = internet_data.split("Stock information for ")[1].split(":")[0]
                details = internet_data.split(": ")[1]
                internet_data = f"Boss, I've accessed financial networks for {symbol}. {details} Shall I activate continuous monitoring for this security?"
            
            elif "Web search results for" in internet_data:
                query = internet_data.split("Web search results for '")[1].split("'")[0]
                results = internet_data.split(":\n", 1)[1] if ":\n" in internet_data else internet_data
                internet_data = f"I've conducted a sweep of available data on {query}, Boss. Here's what I've found:\n\n{results}\n\nI can dig deeper if needed. Would you like me to expand on any particular aspect?"
        
        return user_input, internet_data
    
    def clear_history(self):
        """Clear conversation history except for the system message."""
        system_message = self.conversation_history[0]
        self.conversation_history = [system_message]
    
    def save_conversation(self, filename=None):
        """Save the current conversation to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"friday_logs_{timestamp}.json"
            
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
            
        return filename
            
    def load_conversation(self, filename):
        """Load a conversation from a JSON file."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.conversation_history = json.load(f)
            return True
        else:
            return False
    
    def analyze_sentiment(self, text):
        """Simple analysis to detect if user might be upset or stressed."""
        negative_words = ["angry", "upset", "stressed", "worried", "problem", "error", "fail", 
                          "broken", "crash", "terrible", "bad", "hate", "help", "urgent"]
        
        text_lower = text.lower()
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if negative_count >= 2:
            return "concerned"
        return "neutral"