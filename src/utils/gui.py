import os
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog, messagebox
from tkinter.font import Font
import threading
import time
from .assistant import FridayAssistant

class FridayGUI:
    def __init__(self, root):
        """Initialize the GUI for Friday Assistant."""
        self.root = root
        self.root.title("F.R.I.D.A.Y.")
        self.root.geometry("700x550")
        
        # Set Stark Industries theme colors
        self.colors = {
            "bg": "#1a1a1a",        # Dark background
            "accent": "#e62e00",     # Iron Man red
            "secondary": "#4d4d4d",  # Dark gray
            "text": "#f2f2f2",       # Light text
            "highlight": "#0099cc",  # Tech blue highlight
            "success": "#33cc33",    # Green for success
            "warning": "#ffcc00"     # Yellow for warnings
        }
        
        # Configure the root window
        self.root.configure(bg=self.colors["bg"])
        
        # Custom fonts
        self.fonts = {
            "title": Font(family="Arial", size=14, weight="bold"),
            "subtitle": Font(family="Arial", size=12, weight="bold"),
            "regular": Font(family="Arial", size=10),
            "input": Font(family="Consolas", size=11),
            "status": Font(family="Arial", size=9, slant="italic")
        }
        
        # Get API key if not set in environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            api_key = self.get_api_key()
        
        # Initialization status
        self.startup_complete = False
        self.is_processing = False
        
        # Initialize Friday assistant with all API keys
        try:
            self.friday = FridayAssistant(
                api_key=api_key,
                serpapi_key=os.environ.get("SERPAPI_KEY"),
                weather_key=os.environ.get("OPENWEATHERMAP_KEY"),
                news_key=os.environ.get("NEWSAPI_KEY"),
                stock_key=os.environ.get("ALPHAVANTAGE_KEY")
            )
            self.api_key_valid = True
        except Exception as e:
            self.friday = None
            self.api_key_valid = False
            messagebox.showerror("System Error", f"Error initializing F.R.I.D.A.Y.: {str(e)}")
        
        # Create and configure GUI elements
        self.create_widgets()
        
        # Startup sequence
        self.run_startup_sequence()

    def get_api_key(self):
        """Get OpenAI API key from user."""
        api_key = simpledialog.askstring("Authentication Required", 
                                      "Please enter your OpenAI API key:", 
                                      show="*")
                                      
        # Optionally ask for other API keys for internet features
        if api_key:
            serpapi_key = simpledialog.askstring("Internet Search Capability (Optional)", 
                                              "Enter SerpAPI key for web search (leave empty to skip):", 
                                              show="*")
            
            if serpapi_key:
                os.environ["SERPAPI_KEY"] = serpapi_key
                
            weather_key = simpledialog.askstring("Weather Capability (Optional)", 
                                             "Enter OpenWeatherMap API key for weather data (leave empty to skip):", 
                                             show="*")
            
            if weather_key:
                os.environ["OPENWEATHERMAP_KEY"] = weather_key
            
            news_key = simpledialog.askstring("News Capability (Optional)", 
                                          "Enter NewsAPI key for news data (leave empty to skip):", 
                                          show="*")
            
            if news_key:
                os.environ["NEWSAPI_KEY"] = news_key
            
            stock_key = simpledialog.askstring("Stock Market Capability (Optional)", 
                                           "Enter Alpha Vantage API key for stock data (leave empty to skip):", 
                                           show="*")
            
            if stock_key:
                os.environ["ALPHAVANTAGE_KEY"] = stock_key
        
        return api_key
    
    def create_widgets(self):
        """Create all widgets for the GUI."""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title bar with Stark Industries branding
        title_frame = tk.Frame(main_frame, bg=self.colors["bg"], height=40)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(title_frame, text="F.R.I.D.A.Y.", font=self.fonts["title"], 
                             bg=self.colors["bg"], fg=self.colors["accent"])
        title_label.pack(side=tk.LEFT, padx=5)
        
        subtitle_label = tk.Label(title_frame, 
                                text="Female Replacement Intelligent Digital Assistant Youth", 
                                font=self.fonts["status"], 
                                bg=self.colors["bg"], fg=self.colors["text"])
        subtitle_label.pack(side=tk.LEFT, padx=5)
        
        # Status indicator
        self.status_var = tk.StringVar(value="Initializing systems...")
        self.status_label = tk.Label(title_frame, textvariable=self.status_var, 
                                   font=self.fonts["status"], 
                                   bg=self.colors["bg"], fg=self.colors["highlight"])
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Internet status indicator
        self.internet_status_var = tk.StringVar(value="◉ ONLINE")
        self.internet_status = tk.Label(title_frame, textvariable=self.internet_status_var,
                                     font=self.fonts["status"],
                                     bg=self.colors["bg"], fg=self.colors["success"])
        self.internet_status.pack(side=tk.RIGHT, padx=5)
        
        # Chat display with tech-inspired border
        chat_frame = tk.LabelFrame(main_frame, text="Interface", 
                                 font=self.fonts["subtitle"],
                                 bg=self.colors["bg"], fg=self.colors["accent"],
                                 bd=2, relief=tk.GROOVE, 
                                 highlightbackground=self.colors["accent"],
                                 highlightthickness=1)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, 
                                                    bg=self.colors["secondary"], 
                                                    fg=self.colors["text"], 
                                                    font=self.fonts["regular"],
                                                    insertbackground=self.colors["highlight"])
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for text styling
        self.chat_display.tag_configure("friday", foreground=self.colors["accent"])
        self.chat_display.tag_configure("user", foreground=self.colors["highlight"])
        self.chat_display.tag_configure("system", foreground=self.colors["warning"])
        self.chat_display.tag_configure("alert", foreground=self.colors["warning"], font=self.fonts["subtitle"])
        
        # Input area with tech-inspired border
        input_frame = tk.LabelFrame(main_frame, text="Command Input", 
                                  font=self.fonts["subtitle"],
                                  bg=self.colors["bg"], fg=self.colors["accent"],
                                  bd=2, relief=tk.GROOVE, 
                                  highlightbackground=self.colors["accent"],
                                  highlightthickness=1)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # User input field
        self.user_input = tk.Entry(input_frame, font=self.fonts["input"], 
                                 bg=self.colors["secondary"], 
                                 fg=self.colors["text"],
                                 insertbackground=self.colors["highlight"],
                                 relief=tk.SUNKEN, bd=2)
        self.user_input.pack(fill=tk.X, padx=10, pady=(10, 5), ipady=3)
        self.user_input.bind("<Return>", self.process_input)
        
        # Button frame
        button_frame = tk.Frame(input_frame, bg=self.colors["bg"])
        button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Send button - white with red text as requested
        self.send_button = tk.Button(button_frame, text="SEND", font=self.fonts["subtitle"],
                                  bg="white", fg=self.colors["accent"],
                                  activebackground="white", activeforeground=self.colors["accent"],
                                  bd=1, width=10, command=self.process_input)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear button - white with accent color
        self.clear_button = tk.Button(button_frame, text="CLEAR", font=self.fonts["subtitle"],
                                   bg="white", fg=self.colors["accent"],
                                   activebackground="white", activeforeground=self.colors["accent"],
                                   bd=1, width=10, command=self.clear_chat)
        self.clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Save button - white with accent color
        self.save_button = tk.Button(button_frame, text="SAVE LOGS", font=self.fonts["subtitle"],
                                 bg="white", fg=self.colors["accent"],
                                 activebackground="white", activeforeground=self.colors["accent"],
                                 bd=1, width=10, command=self.save_conversation)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Set input field as disabled until startup completes
        self.user_input.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        
        # Check internet connectivity
        self.check_internet_status()

    def run_startup_sequence(self):
        """Run a startup sequence animation."""
        self.startup_steps = [
            "Initializing systems...",
            "Establishing secure connection...",
            "Loading personality matrix...",
            "Calibrating voice recognition...",
            "Running security protocols...",
            "All systems nominal."
        ]
        
        # Start the sequence in a separate thread
        threading.Thread(target=self._animate_startup).start()
    
    def _animate_startup(self):
        """Animate the startup sequence."""
        for i, step in enumerate(self.startup_steps):
            self.status_var.set(step)
            
            # Show system message in chat display
            if i > 0:  # Skip showing the first message
                self.display_message("System", step)
            
            # Delay between steps
            time.sleep(0.8)
        
        # Enable input after startup
        self.user_input.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        
        # Set focus to input field
        self.user_input.focus_set()
        
        # Display welcome message
        if self.friday and self.api_key_valid:
            greeting = self.friday.get_greeting()
            # Add internet capability information to the greeting
            greeting += " I now have internet access capabilities. I can search the web, check weather, news, and stocks in real-time."
            self.display_message("FRIDAY", greeting)
        
        self.startup_complete = True
        
        # Set final status
        self.status_var.set("Ready")
    
    def process_input(self, event=None):
        """Process user input and get response from Friday."""
        if self.is_processing or not self.startup_complete:
            return
        
        user_message = self.user_input.get().strip()
        
        if not user_message or not self.api_key_valid:
            return
        
        # Clear input field
        self.user_input.delete(0, tk.END)
        
        # Display user message
        self.display_message("You", user_message)
        
        # Set processing state
        self.is_processing = True
        self.status_var.set("Processing request...")
        self.send_button.config(state=tk.DISABLED)
        
        # Display acknowledgement
        self.display_message("FRIDAY", self.friday.get_acknowledgement())
        
        # Create a thread for getting the response
        thread = threading.Thread(target=self.get_response_thread, args=(user_message,))
        thread.daemon = True
        thread.start()
    
    def get_response_thread(self, user_message):
        """Thread function to get response from Friday."""
        try:
            # Analyze sentiment to determine if user is stressed
            sentiment = self.friday.analyze_sentiment(user_message)
            
            # Get response
            response = self.friday.ask(user_message)
            
            # Display the response
            if sentiment == "concerned":
                # Add a special alert sound effect or visual
                self.display_message("FRIDAY", response, tag="alert")
            else:
                self.display_message("FRIDAY", response)
                
        except Exception as e:
            self.display_message("System", f"System error: {str(e)}")
        
        # Reset processing state
        self.is_processing = False
        self.status_var.set("Ready")
        self.send_button.config(state=tk.NORMAL)
        self.user_input.focus_set()
    
    def display_message(self, sender, message, tag=None):
        """Display a message in the chat display."""
        self.chat_display.config(state=tk.NORMAL)
        
        # Insert timestamp
        timestamp = f"[{time.strftime('%H:%M:%S')}] "
        self.chat_display.insert(tk.END, timestamp)
        
        # Insert sender with appropriate tag
        if sender == "You":
            self.chat_display.insert(tk.END, f"{sender}: ", "user")
        elif sender == "FRIDAY":
            self.chat_display.insert(tk.END, f"{sender}: ", "friday")
        else:
            self.chat_display.insert(tk.END, f"{sender}: ", "system")
        
        # Insert message with tag if provided
        if tag:
            self.chat_display.insert(tk.END, f"{message}\n\n", tag)
        else:
            self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Scroll to the bottom
        self.chat_display.see(tk.END)
        
        # Disable text widget
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """Clear the chat display and conversation history."""
        # Clear display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Clear Friday's conversation history
        if self.friday:
            self.friday.clear_history()
        
        # Display system reset message
        self.display_message("System", "Chat memory cleared.")
        self.display_message("FRIDAY", "Systems reset complete. How can I help you, Boss?")
    
    def check_internet_status(self):
        """Check internet connectivity and update status indicator."""
        import threading
        import requests
        
        def check_connection():
            try:
                # Try to reach a reliable site
                response = requests.get("https://www.google.com", timeout=5)
                if response.status_code == 200:
                    self.internet_status_var.set("◉ ONLINE")
                    self.internet_status.config(fg=self.colors["success"])
                else:
                    self.internet_status_var.set("◉ LIMITED")
                    self.internet_status.config(fg=self.colors["warning"])
            except:
                self.internet_status_var.set("◉ OFFLINE")
                self.internet_status.config(fg=self.colors["danger"])
            
            # Schedule periodic checks if window is still active
            if self.root.winfo_exists():
                self.root.after(60000, lambda: threading.Thread(target=check_connection).start())  # Check every minute
        
        # Start the check in a separate thread
        threading.Thread(target=check_connection).start()
    
    def save_conversation(self):
        """Save the current conversation."""
        if not self.friday:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"friday_logs_{time.strftime('%Y%m%d_%H%M')}.json"
        )
        
        if file_path:
            try:
                filename = self.friday.save_conversation(file_path)
                self.display_message("System", f"Conversation logs saved to {filename}")
            except Exception as e:
                self.display_message("System", f"Error saving conversation: {str(e)}")
    
    def load_conversation(self, filename):
        """Load a conversation from file."""
        if not self.friday:
            return False
            
        try:
            if self.friday.load_conversation(filename):
                # Clear chat display
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete(1.0, tk.END)
                self.chat_display.config(state=tk.DISABLED)
                
                # Display loaded conversation
                self.display_message("System", f"Loaded conversation from {filename}")
                return True
            else:
                self.display_message("System", f"File not found: {filename}")
                return False
        except Exception as e:
            self.display_message("System", f"Error loading conversation: {str(e)}")
            return False