import os
import openai
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
import json
from dotenv import load_dotenv
import httpx

class CommandIntent(BaseModel):
    """Model representing the parsed intent from user input"""
    action: Literal["open", "close", "search", "unknown"] = Field(
        description="The primary action to perform"
    )
    application: Optional[str] = Field(
        None, description="Target application for open/close commands"
    )
    query: Optional[str] = Field(
        None, description="Search query for search commands"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters for the action"
    )

class NLPProcessor:
    """
    Processes natural language inputs to determine intent and extract parameters.
    Uses OpenAI's API to interpret user commands.
    """
    
    def __init__(self):
        # Ensure environment variables are loaded
        load_dotenv()
        
        # Initialize OpenAI client with API key from environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Create a custom HTTP client without proxies
        http_client = httpx.Client(
            base_url="https://api.openai.com",
            timeout=60.0,
            follow_redirects=True
        )
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=api_key,
            http_client=http_client
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    def process_input(self, user_input: str) -> tuple:
        """
        Process natural language input to determine intent and extract parameters.
        
        Args:
            user_input (str): The user's natural language input
            
        Returns:
            tuple: (intent, params) where intent is the determined action and params are extracted parameters
        """
        system_prompt = """
        You are an AI assistant that interprets user commands for a Windows computer assistant.
        Analyze the user's input and identify the most likely intent from these options:
        
        1. Open an application (action: "open") - When the user wants to launch or start a program
        2. Close an application (action: "close") - When the user wants to exit or terminate a program
        3. Search for information (action: "search") - When the user is asking a question, looking for information, or wants to look something up
        
        Be flexible in your interpretation. If the user's query contains phrases like "look up", "search for", "find information about", "how to", "what is", or any question formats, treat it as a search intent.
        
        For search queries, extract the full search query the user likely wants answered. Formulate a clear, comprehensive search query that would yield good results on Google.
        
        Example interpretations:
        - "Open Chrome" → Intent: open, Application: Chrome
        - "Close Word" → Intent: close, Application: Word
        - "Look up the weather" → Intent: search, Query: "current weather forecast"
        - "How tall is the Burj Khalifa?" → Intent: search, Query: "height of Burj Khalifa"
        - "Find information about Mars" → Intent: search, Query: "facts about Mars planet"
        
        RESPOND WITH A JSON OBJECT that has the following structure:
        {
            "action": "open|close|search",
            "application": "app name" (only for open/close),
            "query": "search query" (only for search)
        }

        Always include "action" field with exactly one of the values: "open", "close", or "search".
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Interpret this command: {user_input}"}
                ]
            )
            
            # Parse the JSON response
            result_json = response.choices[0].message.content
            print(f"Raw response: {result_json}")  # For debugging
            result = json.loads(result_json)
            
            # Handle different JSON format possibilities
            if "intent" in result and "action" not in result:
                result["action"] = result.pop("intent")
                
            # Ensure we have all required fields
            if "action" not in result or not result["action"]:
                result["action"] = "unknown"
                
            # Convert to CommandIntent model
            try:
                intent_obj = CommandIntent(**result)
            except Exception as e:
                print(f"Error creating CommandIntent: {e}")
                # Create a default intent object with the available data
                intent_obj = CommandIntent(
                    action="search" if "query" in result and result["query"] else "unknown",
                    application=result.get("application"),
                    query=result.get("query")
                )
            
            # Extract intent and parameters
            intent = intent_obj.action
            params = {
                "application": intent_obj.application,
                "query": intent_obj.query,
                **intent_obj.parameters
            }
            
            return intent, params
            
        except Exception as e:
            print(f"Error processing input: {e}")
            
            # In case of error, try to handle common search patterns directly
            lower_input = user_input.lower()
            if (lower_input.startswith("look up") or 
                lower_input.startswith("search for") or 
                lower_input.startswith("find") or
                lower_input.startswith("how") or
                lower_input.startswith("what") or
                lower_input.startswith("when") or
                lower_input.startswith("where") or
                lower_input.startswith("who") or
                lower_input.startswith("why") or
                "?" in lower_input):
                
                return "search", {"query": user_input}
                
            return "unknown", {"error": str(e)}
