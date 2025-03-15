"""
AI Task Launcher - A Windows assistant that transforms natural language into computer actions.
Run this script to start the assistant in interactive mode.
"""

from app_controller import AppController

def main():
    print("=======================================")
    print("AI Task Launcher - Your Windows Assistant")
    print("=======================================")
    print("Type 'exit' or 'quit' to end the session")
    
    controller = AppController()
    
    while True:
        try:
            user_input = input("\nHow can I help you? > ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            result = controller.process_command(user_input)
            print(result)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
