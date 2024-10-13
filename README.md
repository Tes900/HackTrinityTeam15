# RentaLyze

## Overview
RentaLyze is an AI-powered solution designed to streamline tenant-landlord dispute resolution. Our platform assists tenants in generating formal complaint letters based on their rental agreements, facilitating conflict resolution through AI-driven analysis of key contract clauses. By leveraging technologies such as Python, Bootstrap, and OpenAI's GPT, we make legal assistance accessible and affordable for all tenants, empowering them to assert their rights while promoting fair and transparent communication.

## Key Features
- **AI-Powered Letter Generation**: Automatically generate complaint letters tailored to the specific rental issues by analyzing rental contracts.
- **User-Friendly Interface**: Simple forms for tenants to input their personal details, rental contract information, problems, and communication history.
- **Customizable Tone**: Choose from different tones, such as "Concerned," to match the nature of your complaint.
- **Downloadable PDFs**: After generating a letter, users can edit and download it as a PDF for submission to their landlords.

## How to Use the Web App

### Step 1: Download Python and Pip
- Download and install Python from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Pip will be installed automatically with Python.

### Step 2: Install Requirements
- Open your command line (CMD or Poweshell) and navigate to the project's backend directory.
- Run the following command to install the required dependencies:
  ```bash
  pip install -r requirements.txt

### Step 3: Add API key
- Navigate to `backend` `app` then open `utils.py`
- On line 15 - api_key="", insert your own api key.
  
### Step 4: Run the Frontend Server
- Navigate to the `frontend` folder using the command line.
- Run the following command:
  ```bash
  python -m http.server 5500

### Step 5: Run the Backend Server
- Open another command line window and navigate to the `backend` folder.
- Run the backend with the following command:
  ```bash
  python -m app.main

### Step 6: Access the Web App
- Open a web browser and go to:
http://localhost:5500/html/homepage.html
