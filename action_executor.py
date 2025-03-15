import os
import subprocess
import webbrowser
import pygetwindow as gw
import urllib.parse
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
        Perform a web search for the given query and open the results in a browser.
        
        Args:
            query (str): The search query
            
        Returns:
            str: Response message
        """
        if not query or query.strip() == "":
            return "I'm not sure what you want me to search for."
        
        try:
            # Format the query for a search URL
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Try to open in Chrome first
            chrome_path = self.app_registry.get_app_path("chrome")
            if chrome_path:
                try:
                    subprocess.Popen(f'"{chrome_path}" "{search_url}"')
                except:
                    # Fall back to default browser if Chrome fails
                    webbrowser.open(search_url)
            else:
                # Use default browser if Chrome isn't found
                webbrowser.open(search_url)
            
            return f"I've opened a search for '{query}' in your browser."
                
        except Exception as e:
            return f"Error performing search: {str(e)}"
