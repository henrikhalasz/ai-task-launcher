# AI Task Launcher
An AI powered personal assistant to launch apps, manage files and summarize content

## Overview

AI Task Launcher is a Windows assistant that uses natural language processing to:
- Open and close applications using friendly names
- Perform web searches and summarize results
- Execute commands based on natural language input
- Interpret user intent to perform the right action

## Features

- **Launch Applications**: Open any installed application with a natural command
- **Close Applications**: Close running applications with simple requests
- **Web Search**: Ask factual questions to perform a web search and get summarized results
- **Extensible Design**: Easily integrate additional functionalities in the future

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Windows 10/11
- OpenAI API key

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment**:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     OPENAI_MODEL=gpt-4o  # or another compatible model
     ```

## Usage

1. **Start the assistant in interactive mode**:
   ```
   python main.py
   ```

2. **Example commands**:
   - "Open Chrome"
   - "Close Notepad"
   - "Search for the latest Mars rover discoveries"
   - "Who won the Nobel Prize in Physics last year?"
   - "Open Word and create a new document"

3. **Exit the assistant**:
   Type "exit" or "quit" to end the session.

## Customization

You can add new applications to the registry by modifying the `app_registry.py` file or adding custom command handlers in the `action_executor.py` file.

## Future Enhancements

- Voice command support
- Task automation
- Calendar and email integration
- File management capabilities
- Media playback controls
