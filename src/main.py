import os
import sys
import tkinter as tk
from dotenv import load_dotenv
from utils.gui import FridayGUI
import threading

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'openai',
        'python-dotenv',
        'requests',
        'beautifulsoup4',
        're',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            if package == 're':  # re is part of standard library
                continue
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        import subprocess
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}. Please install it manually.")
                return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write("# FRIDAY API Keys\n")
            f.write("OPENAI_API_KEY=\n")
            f.write("SERPAPI_KEY=\n")
            f.write("OPENWEATHERMAP_KEY=\n")
            f.write("NEWSAPI_KEY=\n")
            f.write("ALPHAVANTAGE_KEY=\n")
        print(f"Created .env file at {env_path}")

def main():
    """Main function to run the FRIDAY Assistant application."""
    # Ensure all dependencies are installed
    if not check_dependencies():
        print("Error: Missing required dependencies. Please install them and try again.")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    create_env_file()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Set up the Tkinter root window
    root = tk.Tk()
    
    # Set window title and icon
    root.title("F.R.I.D.A.Y. - Stark Industries")
    
    # Try to set icon if available
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "stark_icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass
    
    # Center the window on screen
    window_width = 700
    window_height = 550
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Initialize the GUI
    app = FridayGUI(root)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()