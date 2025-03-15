import os
import subprocess
import time
import pygetwindow as gw
import webbrowser
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

from app_registry import AppRegistry

class ActionExecutor:
    """
    Executes actions based on the intent determined by the NLP processor.
    """
    
    def __init__(self):
        self.app_registry = AppRegistry()
    
    def execute_action(self, intent: str, params: Dict[str, Any]) -> str:
        """
        Execute an action based on the intent and parameters.
        
        Args:
            intent (str): The determined intent (open, close, search, etc.)
            params (Dict[str, Any]): Parameters for the action
            
        Returns:
            str: Response message indicating the result of the action
        """
        if intent == "open":
            return self._open_application(params.get("application", ""))
        
        elif intent == "close":
            return self._close_application(params.get("application", ""))
        
        elif intent == "search":
            return self._perform_search(params.get("query", ""))
        
        else:
            return "I'm not sure what you want me to do. Can you be more specific?"
    
    def _open_application(self, app_name: str) -> str:
        """
        Open an application by name.
        
        Args:
            app_name (str): Name of the application to open
            
        Returns:
            str: Response message
        """
        if not app_name:
            return "I'm not sure which application you want me to open."
        
        # Get the executable path from the app registry
        executable_path = self.app_registry.get_app_path(app_name)
        
        if not executable_path:
            return f"I don't know how to open '{app_name}'. Can you provide more details?"
        
        try:
            # Open the application
            subprocess.Popen(executable_path)
            return f"Opening {app_name} for you."
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    
    def _close_application(self, app_name: str) -> str:
        """
        Close an application by name.
        
        Args:
            app_name (str): Name of the application to close
            
        Returns:
            str: Response message
        """
        if not app_name:
            return "I'm not sure which application you want me to close."
        
        # Get the window title pattern from the app registry
        window_pattern = self.app_registry.get_window_pattern(app_name)
        
        if not window_pattern:
            return f"I don't know how to close '{app_name}'. Can you provide more details?"
        
        try:
            # Find windows matching the pattern
            matching_windows = [w for w in gw.getAllWindows() if window_pattern.lower() in w.title.lower()]
            
            if not matching_windows:
                return f"I couldn't find any open windows for {app_name}."
            
            # Close all matching windows
            for window in matching_windows:
                window.close()
            
            return f"Closed {app_name} for you."
        except Exception as e:
            return f"Error closing {app_name}: {str(e)}"
    
    def _perform_search(self, query: str) -> str:
        """
        Perform a web search for the given query, open Chrome, and return a summary of results.
        
        Args:
            query (str): The search query
            
        Returns:
            str: Summary of search results
        """
        if not query:
            return "I'm not sure what you want me to search for."
        
        try:
            # Format the query for a search URL - use proper URL encoding
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Open Chrome with the search URL
            chrome_path = self.app_registry.get_app_path("chrome")
            if chrome_path:
                try:
                    # Print debugging info
                    print(f"Launching Chrome: {chrome_path}")
                    print(f"Search URL: {search_url}")
                    
                    # Use a more robust method to launch Chrome with the URL
                    subprocess.Popen(f'"{chrome_path}" "{search_url}"')
                except Exception as chrome_error:
                    print(f"Error launching Chrome: {str(chrome_error)}")
                    # Fallback to default browser
                    webbrowser.open(search_url)
            else:
                # Fallback to default browser if Chrome not found
                print("Chrome path not found, using default browser")
                webbrowser.open(search_url)
            
            # Return a success message immediately
            return f"I've opened a web search for '{query}'. You can view the results in the browser window."
            
            # The code below attempts to fetch and parse the search results, but this is optional
            # and often doesn't work well due to Google's anti-scraping measures
            # We're commenting it out for now to ensure the basic functionality works
            """
            # Give the page time to load
            time.sleep(2)
            
            # Fetch and parse the search results
            try:
                response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract search result snippets (this is a simplified approach and may need adjustment)
                search_results = []
                for div in soup.find_all("div", class_=["g"]):
                    snippet = div.find("div", class_="IsZvec")
                    if snippet:
                        search_results.append(snippet.get_text())
                
                if search_results:
                    # Combine the first few results into a summary
                    summary = "\n\n".join(search_results[:3])
                    return f"I've opened Chrome with your search for '{query}'. Here's a summary of what I found:\n\n{summary}"
                else:
                    return f"I've opened Chrome with your search for '{query}', but couldn't generate a summary of the results."
            
            except Exception as e:
                # Still return a successful message even if summarization fails
                return f"I've opened Chrome with your search for '{query}'. You can view the results in the browser window."
            """
                
        except Exception as e:
            return f"Error performing search for '{query}': {str(e)}"
