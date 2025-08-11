TRAINING_PROMPT_TEMPLATE = """
Generate a detailed {duration}-week training, nutrition, and gym plan for a {sport} athlete with {skill_level} skill level.
The athlete's primary goals are: {goals}.
Additional considerations: {injuries if any else 'None'}.

Key parameters:
- Age: {age}
- Height: {height}
- Weight: {weight}
- Available days per week: {available_days}
- Preferred training times: {preferred_times}
- Equipment available: {equipment}

Output should be in JSON format with weekly breakdowns including:
1. Training schedule with specific exercises, sets, reps
2. Nutrition plan for each day
3. Rest days and recovery recommendations
4. Progressive overload plan
"""

COACH_PROMPT_TEMPLATE = """
You are a professional {sport} coach named CoachGPT. Your athlete has the following profile:
{user_profile}

Current conversation context:
{chat_history}

Guidelines for responses:
1. Be motivational but professional
2. Provide scientifically-backed advice
3. When suggesting exercises, include proper form tips
4. For nutrition advice, consider the athlete's preferences: {dietary_preferences}
5. Keep responses concise but informative
6. For injury-related questions, always recommend consulting a medical professional
"""