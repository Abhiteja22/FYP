```
# Riment - Final Year Project

Riment is a AI powered wealth management application. This document provides instructions for setting up and running the project locally.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11
- Node.js and npm
- An OpenAI API key
- A SerpAPI key

## Setup

### Backend Setup

1. **Create a Virtual Environment:**

   Navigate to the project's root directory and run:

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment:**

   - On Windows:
     ```cmd
     .\venv\Scripts\activate
     ```

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies:**

   With the virtual environment activated, install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Backend Server:**

   Change directory to the `fyp` folder and run the Django development server:

   ```bash
   cd fyp
   python manage.py runserver
   ```

   The backend server should now be running and accessible.

### Frontend Setup

1. **Open a New Terminal:**

   You will need to open a new terminal window or tab for the frontend setup. Ensure you are in the project's root directory.

2. **Navigate to the Frontend Directory:**

   ```bash
   cd fyp/frontend
   ```

3. **Install NPM Packages:**

   Install the required npm packages:

   ```bash
   npm install
   ```

4. **Start the Frontend Development Server:**

   ```bash
   npm run dev
   ```

   The frontend should now be running and accessible.

## Usage

- Access the backend API at [http://localhost:8000](http://localhost:8000).
- Access the frontend application at [http://localhost:3000](http://localhost:3000).