# utils/diet.py
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model():
    """Initialize and return the Gemini model"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment variables")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_diet_plan(user_profile, duration=7):
    """Generate a personalized diet plan based on user profile"""
    try:
        model = get_gemini_model()
        
        # Extract relevant user information
        sport = user_profile.get('sport', 'general fitness')
        experience = user_profile.get('experience', 'beginner')
        goals = user_profile.get('goals', 'improve fitness')
        age = user_profile.get('age', 25)
        weight = user_profile.get('weight', 70)
        height = user_profile.get('height', 170)
        injuries = user_profile.get('injuries', 'None')
        performance_goal = user_profile.get('performance_goal', '')
        
        prompt = f"""
Create a comprehensive {duration}-day personalized diet plan for a {age}-year-old {experience} {sport} athlete.
Weight: {weight} kg, Height: {height} cm
Primary Goals: {goals}
Performance Goal: {performance_goal}
Injuries/Limitations: {injuries}

Structure the response EXACTLY as follows:

<dietplan>
<div class='diet-plan'>
<div class='diet-header'>
<h2>{sport.title()} Nutrition Blueprint</h2>
<h3>For {experience.title()} Level Athletes</h3>
</div>

<div class='nutrition-principles'>
<h4>Nutrition Principles</h4>
<p><strong>Caloric Target:</strong> [Daily calorie range based on goals]</p>
<p><strong>Macronutrient Ratio:</strong> [Protein/Carbs/Fats ratio]</p>
<p><strong>Hydration Strategy:</strong> [Daily water intake and timing]</p>
<p><strong>Meal Timing:</strong> [When to eat around training]</p>
</div>

<div class='daily-plan'>
<h4>{duration}-Day Meal Plan</h4>
[For each day]
<div class='day-section'>
<h5>Day [X]: [Day Focus - e.g., Training Day, Rest Day]</h5>
<p><strong>Pre-Workout Meal (if applicable):</strong> [Food items, portions, timing, benefits]</p>
<p><strong>Breakfast:</strong> [Food items, portions, nutritional benefits]</p>
<p><strong>Lunch:</strong> [Food items, portions, nutritional benefits]</p>
<p><strong>Snack:</strong> [Food items, portions, nutritional benefits]</p>
<p><strong>Dinner:</strong> [Food items, portions, nutritional benefits]</p>
<p><strong>Post-Workout Nutrition (if applicable):</strong> [Food items, portions, timing, benefits]</p>
</div>
</div>

<div class='supplement-section'>
<h4>Supplement Recommendations</h4>
<p><strong>Essential Supplements:</strong> [List with dosage, timing, and purpose]</p>
<p><strong>Optional Supplements:</strong> [List with dosage, timing, and purpose]</p>
</div>

<div class='shopping-list'>
<h4>Grocery Shopping List</h4>
<p><strong>Proteins:</strong> [List of protein sources]</p>
<p><strong>Carbohydrates:</strong> [List of carb sources]</p>
<p><strong>Fats:</strong> [List of healthy fat sources]</p>
<p><strong>Vegetables:</strong> [List of vegetables]</p>
<p><strong>Fruits:</strong> [List of fruits]</p>
<p><strong>Other:</strong> [Spices, herbs, etc.]</p>
</div>

<div class='recipe-section'>
<h4>Key Recipes</h4>
<p><strong>[Recipe Name 1]:</strong> [Ingredients and preparation instructions]</p>
<p><strong>[Recipe Name 2]:</strong> [Ingredients and preparation instructions]</p>
</div>

<div class='adaptation-section'>
<h4>Plan Adaptation</h4>
<p><strong>For Weight Loss:</strong> [How to modify the plan]</p>
<p><strong>For Muscle Gain:</strong> [How to modify the plan]</p>
<p><strong>For Vegetarians/Vegans:</strong> [Alternative options]</p>
</div>
</div>
</dietplan>

Include:
- Specific food items and portions
- Nutritional information (calories, protein, carbs, fats)
- Timing of meals relative to training
- Benefits of each food for athletic performance
- Recipe ideas for key meals
- Shopping list for the week
- Supplement recommendations with scientific rationale
- Hydration strategy

Focus on foods that enhance performance in {sport} specifically.
"""
        
        response = model.generate_content(prompt)
        if not response or not getattr(response, "text", None):
            return None
            
        # Extract the plan content
        response_text = response.text.strip()
        
        # Find the plan content between <dietplan> tags
        start = response_text.find('<dietplan>') + len('<dietplan>')
        end = response_text.find('</dietplan>')
        
        if start != -1 and end != -1:
            return response_text[start:end].strip()
        return response_text
        
    except Exception as e:
        print(f"Diet plan generation error: {e}")
        return None