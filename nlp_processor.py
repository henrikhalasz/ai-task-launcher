import os
import openai
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
import json
from dotenv import load_dotenv

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
        
        self.client = openai.OpenAI(api_key=api_key)
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
        Analyze the user's input and identify whether they want to:
        
        1. Open an application (action: "open")
        2. Close an application (action: "close")
        3. Search for information (action: "search")
        
        For open/close commands, extract the application name.
        For search commands, extract the search query.
        Respond with a JSON object containing the structured command.
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
            result = json.loads(response.choices[0].message.content)
            
            # Convert to CommandIntent model
            intent_obj = CommandIntent(**result)
            
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
            return "unknown", {"error": str(e)}
