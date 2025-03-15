import os
import sys
from dotenv import load_dotenv, find_dotenv

from nlp_processor import NLPProcessor
from action_executor import ActionExecutor

class AppController:
    """Main controller class for the AI assistant application."""
    
    def __init__(self):
        # Load environment variables from .env file with better error handling
        env_file = find_dotenv()
        if not env_file:
            print("Warning: .env file not found in current directory. Make sure it exists with your API key.")
            
        load_dotenv(env_file)
        
        # Double-check API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("\nError: OPENAI_API_KEY not found in environment variables")
            print("Please create a .env file in the project root with your API key:")
            print("OPENAI_API_KEY=your_api_key_here")
            print("OPENAI_MODEL=gpt-4o")
            sys.exit(1)
        
        # Initialize NLP processor and action executor
        self.nlp = NLPProcessor()
        self.executor = ActionExecutor()
        
    def process_command(self, user_input):
        """
        Process a natural language command from the user.
        
        Args:
            user_input (str): The user's natural language input
            
        Returns:
            str: Response to the user
        """
        # Use NLP model to determine intent and extract parameters
        intent, params = self.nlp.process_input(user_input)
        
        # Execute the appropriate action based on intent
        result = self.executor.execute_action(intent, params)
        
        return result

def main():
    controller = AppController()
    
    if len(sys.argv) > 1:
        # Process command from command line arguments
        user_input = " ".join(sys.argv[1:])
        result = controller.process_command(user_input)
        print(result)
    else:
        # Interactive mode
        print("AI Task Launcher - Your AI-powered Windows assistant")
        print("Type 'exit' or 'quit' to end the session")
        
        while True:
            user_input = input("\nHow can I help you? > ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            result = controller.process_command(user_input)
            print(result)

if __name__ == "__main__":
    main()
