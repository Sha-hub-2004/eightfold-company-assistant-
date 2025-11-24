# Eightfold Company Assistant

## Overview
The Eightfold Company Assistant is a web application designed to assist users in researching companies and generating structured account plans. It utilizes FastAPI for the backend and provides a user-friendly interface with chat and voice capabilities.

## Project Structure
```
eightfold-company-assistant
├── backend
│   ├── app.py              # Main entry point for the FastAPI application
│   ├── agent.py            # Logic for handling user messages and session states
│   ├── models.py           # Data models using Pydantic
│   ├── requirements.txt     # Backend dependencies
│   └── .env                # Environment variables (OpenAI API key)
├── frontend
│   ├── index.html          # Main HTML file for the frontend application
│   ├── styles.css          # CSS styles for the frontend application
│   └── app.js              # JavaScript code for frontend functionality
└── README.md               # Documentation for the project
```

## Setup Instructions

### Backend
1. Navigate to the `backend` directory:
   ```
   cd backend
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the `backend` directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_real_openai_key_here
   ```

4. Run the FastAPI application:
   ```
   uvicorn app:app --reload --port 8000
   ```

### Frontend
1. Open the `frontend` directory in your preferred code editor.

2. Use a local server to serve the `index.html` file (e.g., Live Server extension in your code editor).

3. Access the application in your web browser at `http://localhost:8000`.

## Usage
1. Choose a persona from the dropdown menu (Efficient, Confused, Chatty, Edge).
2. Type a command such as "Research [Company Name]" to initiate research.
3. After receiving research updates, type "generate plan" to create an account plan.
4. You can edit specific sections of the account plan by typing commands like "Edit opportunities_for_us to focus on AI hiring."

## Features
- Chat and voice input for user interactions.
- Voice output for responses from the assistant.
- Multi-step research process with structured account plan generation.
- Clean and responsive user interface.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is open-source and available under the MIT License.