""" 
Environment setup utility script.
This will create a properly formatted .env file for the application.
"""

import os
import sys

def create_env_file():
    """Creates a properly formatted .env file in the current directory."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Check if .env file already exists
    if os.path.exists(env_path):
        overwrite = input("The .env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # Get API key from user
    api_key = input("Enter your OpenAI API key: ")
    if not api_key.strip():
        print("API key cannot be empty")
        return
    
    # Default model to use
    model = "gpt-4o"
    
    # Write the .env file with proper formatting
    with open(env_path, 'w') as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")
        f.write(f"OPENAI_MODEL={model}\n")
    
    print(f".env file created successfully at {env_path}")
    print("The file contains:")
    print(f"OPENAI_API_KEY=****{api_key[-4:] if len(api_key) > 4 else ''}")
    print(f"OPENAI_MODEL={model}")

def test_env_file():
    """Tests if the .env file can be loaded correctly."""
    try:
        from dotenv import load_dotenv
        
        # Get the absolute path to the .env file
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        
        # Check if file exists
        if not os.path.exists(env_path):
            print(f"Error: .env file not found at {env_path}")
            return False
        
        # Try to load the .env file
        load_dotenv(env_path)
        
        # Check if variables were loaded
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL")
        
        if not api_key:
            print("Error: OPENAI_API_KEY not loaded from .env file")
            return False
        
        if not model:
            print("Warning: OPENAI_MODEL not loaded from .env file, will use default")
        
        print("Environment variables loaded successfully!")
        print(f"Using API key: ****{api_key[-4:] if len(api_key) > 4 else ''}")
        print(f"Using model: {model or 'default'}")
        return True
        
    except Exception as e:
        print(f"Error testing .env file: {str(e)}")
        return False

if __name__ == "__main__":
    print("Environment Setup Utility")
    print("=========================")
    
    action = input("Do you want to create a new .env file or test the existing one? (create/test): ")
    
    if action.lower() == "create":
        create_env_file()
    elif action.lower() == "test":
        test_env_file()
    else:
        print("Invalid option. Please run again and choose 'create' or 'test'")
