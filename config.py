# config.py

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Fetch environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set. Please check your .env file.")