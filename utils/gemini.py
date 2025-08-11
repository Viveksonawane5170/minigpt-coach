import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model():
    """Initialize and return the Gemini model"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment variables")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.0-pro')

def generate_training_plan(user_profile):
    try:
        model = get_gemini_model()
        
        prompt = (
            "Generate a detailed 4-week training, nutrition, and gym plan for an athlete based on the following profile:\n\n"
            + str(user_profile) +
            """
            
Output should be in JSON format with the following structure:
{
    "weeks": [
        {
            "week_number": 1,
            "training_days": [
                {
                    "day": "Monday",
                    "workout": "Strength training - Upper body",
                    "exercises": [
                        {"name": "Bench press", "sets": 4, "reps": "8-10", "notes": "Moderate weight"},
                        {"name": "Pull-ups", "sets": 3, "reps": "8-10"}
                    ],
                    "nutrition": {
                        "breakfast": "Oatmeal with protein powder and berries",
                        "lunch": "Grilled chicken with quinoa and vegetables",
                        "dinner": "Salmon with sweet potato and asparagus",
                        "snacks": ["Greek yogurt", "Handful of almonds"]
                    }
                }
            ],
            "rest_days": ["Sunday"],
            "goals_focus": "Building strength and endurance",
            "notes": "Ensure proper hydration throughout the week"
        }
    ]
}
"""
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Failed to generate training plan: {str(e)}")

def chat_with_coach(user_profile, chat_history, new_message):
    try:
        model = get_gemini_model()
        
        context = f"""
        You are a professional athletic coach assistant. The user profile is:
        {str(user_profile)}
        
        Previous conversation context:
        {str(chat_history)}
        """
        
        response = model.generate_content([context, new_message])
        return response.text
    except Exception as e:
        raise Exception(f"Failed to chat with coach: {str(e)}")