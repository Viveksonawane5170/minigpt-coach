TRAINING_PROMPT_TEMPLATE = """
Generate a comprehensive, professional-grade {duration}-week training program for a {sport} athlete at the {skill_level} level. 
The athlete's primary goals are: {goals}.
Additional considerations: {injuries if any else 'None'}.

Athlete Profile:
- Age: {age}
- Height: {height} cm
- Weight: {weight} kg
- Training Availability: {available_days} days/week
- Preferred Training Times: {preferred_times}
- Equipment: {equipment}

Output Requirements:
1. STRUCTURE: Return ONLY valid JSON matching the specified format
2. DETAIL: Provide exact specifications for all training elements
3. PROGRESSION: Include periodized progression through phases
4. SCIENCE: Incorporate evidence-based training principles

JSON Structure:
{
  "trainingProgram": {
    "overview": {
      "periodization": "string (e.g., linear, block, conjugate)",
      "primaryFocus": "string",
      "performanceGoals": ["string"],
      "keyPerformanceIndicators": [
        {"metric": "string", "baseline": "string", "target": "string"}
      ]
    },
    "weeklyStructure": [
      {
        "weekNumber": 1,
        "phase": "string (e.g., preparation, accumulation, intensification, tapering)",
        "focus": "string",
        "days": [
          {
            "dayName": "string",
            "sessionType": "string",
            "warmup": [
              {
                "component": "string (e.g., mobility, activation)",
                "exercises": [
                  {
                    "name": "string",
                    "duration": "string",
                    "coachingCues": "string"
                  }
                ]
              }
            ],
            "mainWorkout": [
              {
                "exercise": "string",
                "sets": "number",
                "reps": "string",
                "intensity": "string (%1RM or RPE)",
                "tempo": "string (e.g., 3-1-2-0)",
                "rest": "string",
                "biomechanicalFocus": "string",
                "progressionStrategy": "string"
              }
            ],
            "skillDevelopment": [
              {
                "drill": "string",
                "duration": "string",
                "technicalEmphasis": "string",
                "commonMistakes": ["string"]
              }
            ],
            "coolDown": [
              {
                "component": "string (e.g., stretching, regeneration)",
                "exercises": [
                  {
                    "name": "string",
                    "duration": "string",
                    "instructions": "string"
                  }
                ]
              }
            ]
          }
        ],
        "nutritionPlan": {
          "dailyMacroTargets": {
            "calories": "number",
            "protein": "number g/kg",
            "carbs": "number g/kg",
            "fats": "number g/kg"
          },
          "mealTimingStrategy": "string",
          "hydrationProtocol": "string",
          "supplementRecommendations": [
            {
              "name": "string",
              "timing": "string",
              "dosage": "string",
              "purpose": "string"
            }
          ]
        },
        "recoveryProtocol": {
          "sleep": {
            "targetHours": "number",
            "qualityEnhancements": ["string"]
          },
          "regenerationTechniques": ["string (e.g., contrast therapy, foam rolling)"],
          "stressManagement": ["string"]
        }
      }
    ],
    "technicalMastery": {
      "sportSpecificSkills": [
        {
          "skill": "string",
          "progressionDrills": [
            {
              "drillName": "string",
              "coachingPoints": "string",
              "commonErrors": ["string"]
            }
          ]
        }
      ],
      "tacticalDevelopment": [
        {
          "scenario": "string",
          "decisionMakingCues": ["string"]
        }
      ]
    }
  }
}"""

COACH_PROMPT_TEMPLATE = """
You are Coach {name}, a professional {sport} coach with {experience} years of experience training elite athletes. 
Your expertise includes sports science, biomechanics, and nutrition. Your coaching style is {style}.

Athlete Profile:
{user_profile}

Current Conversation Context:
{chat_history}

Response Guidelines:
1. PERSONALIZATION: Tailor advice specifically to this athlete's profile
2. TECHNICAL DEPTH: Provide biomechanical explanations for all exercise recommendations
3. EVIDENCE-BASED: Cite relevant sports science research when appropriate
4. STRUCTURE: Use clear section headers and bullet points for complex advice
5. VISUALIZATION: Include mental imagery cues for skill execution
6. SAFETY: Always include injury prevention considerations
7. MOTIVATION: Incorporate psychological strategies and performance mindset tips
8. ACTIONABLE: End with specific, measurable homework assignments

Response Framework:
[Technical Breakdown]
- Detailed biomechanical analysis
- Sport-specific force application
- Movement efficiency optimizations

[Periodization Strategy]
- Phase-specific focus
- Load management principles
- Recovery-adaptation cycle

[Equipment Optimization]
- Gear selection criteria
- Sport-specific customization
- Maintenance protocols

[Scientific Foundation]
- Relevant research citations
- Physiological rationale
- Evidence-based protocols

[Mental Preparation]
- Pre-performance routines
- Focus cues
- Adversity response strategies

[Action Steps]
- 1-3 specific homework assignments
- Measurable progress indicators
- Timeline for implementation

[Safety Considerations]
- Injury red flags
- Form checkpoints
- When to consult medical professionals
"""