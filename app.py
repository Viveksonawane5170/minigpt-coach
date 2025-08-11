# app.py
import streamlit as st
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Import our centralized DB helper
from utils.db import get_db, initialize_firebase

# Configure Gemini if provided
def initialize_gemini():
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.warning("GEMINI_API_KEY not set. AI features will be disabled.")
            return None
        genai.configure(api_key=api_key)
        # Using Gemini 1.5 Flash model
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Gemini initialization failed: {e}")
        return None

# Firebase authentication functions
def firebase_register(email, password, user_data):
    try:
        db = get_db()
        if db is None:
            st.error("Firebase Admin SDK is not initialized. Can't create user.")
            return None

        user = auth.create_user(
            email=email,
            password=password,
            display_name=user_data.get('name', 'Athlete')
        )

        user_data.setdefault('name', 'Athlete')
        user_data.setdefault('created_at', datetime.now().isoformat())
        return user.uid
    except auth.EmailAlreadyExistsError:
        st.error("⚠️ Email already registered. Please login instead.")
    except ValueError as e:
        st.error(f"❌ Invalid data: {str(e)}")
    except FirebaseError as e:
        st.error(f"🔥 Firebase error: {e.code} - {e.message}")
    except Exception as e:
        st.error(f"🚨 Registration failed: {str(e)}")
    return None

def firebase_get_user_by_email(email):
    try:
        db = get_db()
        if db is None:
            st.error("Firebase Admin SDK is not initialized. Can't look up user.")
            return None
        user = auth.get_user_by_email(email)
        return user.uid
    except auth.UserNotFoundError:
        st.error("🔍 User not found. Please register first.")
    except FirebaseError as e:
        st.error(f"🔥 Firebase error: {e.code} - {e.message}")
    except Exception as e:
        st.error(f"🚨 Login failed: {str(e)}")
    return None

# AI helper functions
def generate_training_plan(model, user_profile, duration=4):
    try:
        if not model:
            raise ValueError("AI model not initialized")
        
        prompt = f"""
Generate a detailed {duration}-week training plan in JSON format for:
Sport: {user_profile.get('sport', 'general fitness')}
Level: {user_profile.get('experience', 'beginner')}
Goals: {user_profile.get('goals', 'improve fitness')}
Available Equipment: {', '.join(user_profile.get('equipment', ['None']))}

IMPORTANT: Return ONLY valid JSON with this structure:
{{
  "trainingPlan": {{
    "sport": "string",
    "level": "string",
    "goals": "string",
    "equipment": "string",
    "weeks": [
      {{
        "weekNumber": 1,
        "focus": "string",
        "days": [
          {{
            "day": "string",
            "workout": "string",
            "details": "string"  // optional additional details
          }}
        ]
      }}
    ]
  }}
}}"""
        
        response = model.generate_content(prompt)
        if not response or not getattr(response, "text", None):
            return None
            
        # Clean the response text to ensure valid JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        return json.loads(response_text)
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse the generated plan. Raw response: {response_text}")
        return None
    except Exception as e:
        st.error(f"AI error: {e}")
        return None

def chat_with_coach(model, user_profile, chat_history, message):
    try:
        if not model:
            raise ValueError("AI model not initialized")
        context = f"You're a professional coach. Profile: {user_profile}\nHistory: {chat_history[-3:] if chat_history else 'None'}"
        response = model.generate_content([context, message])
        return response.text if response and getattr(response, "text", None) else "AI error"
    except Exception as e:
        st.error(f"AI error: {e}")
        return "I'm having trouble responding right now. Please try again later."

# Main application
def main():
    st.set_page_config(page_title="MiniGPT Coach", page_icon="🏋️", layout="wide")
    st.title("🏋️ MiniGPT Coach")

    # Initialize Firebase
    db = get_db()
    if db is None:
        st.warning(
            "Firestore is not initialized. Database features (register/login/save profile, store plans/chats) "
            "will be disabled until you provide a valid service account JSON and set FIREBASE_CONFIG_PATH.\n\n"
            "Place `firebase_config.json` in project root OR set env var FIREBASE_CONFIG_PATH to its path."
        )

    gemini_model = initialize_gemini()

    # Initialize session state
    st.session_state.setdefault('user', None)
    st.session_state.setdefault('profile', None)
    st.session_state.setdefault('chat_history', [])
    st.session_state.setdefault('generated_plan', None)

    # Authentication section
    if not st.session_state.user:
        login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

        with login_tab:
            st.subheader("Welcome Back!")
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_pw")

            if st.button("Sign In", key="login_btn"):
                if email and password:
                    if db is None:
                        st.error("Database not initialized. Can't authenticate.")
                    else:
                        with st.spinner("Authenticating..."):
                            user_id = firebase_get_user_by_email(email)
                            if user_id:
                                try:
                                    doc = db.collection('users').document(user_id).get()
                                    profile = doc.to_dict() if doc.exists else {'name': 'Athlete'}
                                except Exception as e:
                                    st.error(f"Failed to load profile: {e}")
                                    profile = {'name': 'Athlete'}
                                st.session_state.user = user_id
                                st.session_state.profile = profile
                                st.rerun()
                else:
                    st.warning("Please enter both email and password")

        with register_tab:
            st.subheader("Create Your Account")
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email Address", key="reg_email")
                password = st.text_input("Password", type="password", key="reg_pw")
                confirm = st.text_input("Confirm Password", type="password", key="reg_conf")
            with col2:
                name = st.text_input("Full Name", key="reg_name")
                sport = st.selectbox("Primary Sport",
                                   ["General Fitness", "Running", "Cycling", "Swimming",
                                    "Weight Training", "Yoga", "Other"],
                                   key="reg_sport")
            if st.button("Create Account", key="reg_btn"):
                if not all([email, password, confirm, name]):
                    st.warning("Please fill all required fields")
                elif password != confirm:
                    st.error("Passwords don't match!")
                else:
                    if db is None:
                        st.error("Database not initialized. Can't create account.")
                    else:
                        with st.spinner("Creating your account..."):
                            user_data = {"name": name, "sport": sport, "created_at": datetime.now().isoformat()}
                            user_id = firebase_register(email, password, user_data)
                            if user_id:
                                try:
                                    db.collection('users').document(user_id).set(user_data)
                                    st.session_state.user = user_id
                                    st.session_state.profile = user_data
                                    st.success("Account created successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to store user profile: {e}")

    else:
        # Main application after login
        with st.sidebar:
            st.title(f"👋 {st.session_state.profile.get('name', 'Athlete')}")
            st.caption(f"Sport: {st.session_state.profile.get('sport', 'General Fitness')}")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()
            st.divider()
            app_mode = st.radio("Menu", ["📝 Profile", "📅 Training Plan", "💬 AI Coach"], index=1, label_visibility="collapsed")

        if app_mode == "📝 Profile":
            st.header("Your Profile")
            with st.form("profile_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name", value=st.session_state.profile.get('name', ''))
                    age = st.number_input("Age", min_value=12, max_value=100, value=st.session_state.profile.get('age', 25))
                    height = st.number_input("Height (cm)", min_value=100, max_value=250, value=st.session_state.profile.get('height', 170))
                    weight = st.number_input("Weight (kg)", min_value=30, max_value=300, value=st.session_state.profile.get('weight', 70))
                with col2:
                    sport = st.selectbox("Primary Sport",
                                       ["General Fitness", "Running", "Cycling", "Swimming",
                                        "Weight Training", "Yoga", "Other"],
                                       index=["General Fitness","Running","Cycling","Swimming","Weight Training","Yoga","Other"]
                                       .index(st.session_state.profile.get('sport','General Fitness')))
                    experience = st.selectbox("Experience Level", ["Beginner","Intermediate","Advanced","Professional"],
                                            index=["Beginner","Intermediate","Advanced","Professional"]
                                            .index(st.session_state.profile.get('experience','Beginner')))
                    goals = st.text_area("Your Goals", value=st.session_state.profile.get('goals',''))
                    injuries = st.text_area("Injuries/Limitations", value=st.session_state.profile.get('injuries',''))
                available_days = st.slider("Days available per week", 1, 7, st.session_state.profile.get('available_days', 3))
                equipment = st.multiselect("Available Equipment", ["Gym Access", "Dumbbells", "Resistance Bands", "Yoga Mat", "Treadmill", "None"], 
                                          default=st.session_state.profile.get('equipment', []))
                if st.form_submit_button("💾 Save Profile"):
                    updated_profile = {
                        **st.session_state.profile,
                        "name": name, "age": age, "height": height, "weight": weight,
                        "sport": sport, "experience": experience, "goals": goals, "injuries": injuries,
                        "available_days": available_days, "equipment": equipment,
                        "last_updated": datetime.now().isoformat()
                    }
                    if db is None:
                        st.error("Database not initialized. Can't save profile.")
                    else:
                        try:
                            db.collection('users').document(st.session_state.user).set(updated_profile, merge=True)
                            st.session_state.profile = updated_profile
                            st.success("Profile saved successfully!")
                        except Exception as e:
                            st.error(f"Failed to save profile: {e}")

        elif app_mode == "📅 Training Plan":
            st.header("Your Training Plan")
            if not st.session_state.profile.get('age'):
                st.warning("Please complete your profile for personalized plans")
                st.stop()
            
            with st.expander("⚙️ Plan Settings"):
                col1, col2 = st.columns(2)
                with col1:
                    duration = st.slider("Plan Duration (weeks)", 1, 12, 4)
                with col2:
                    focus = st.selectbox("Primary Focus", ["Strength", "Endurance", "Weight Loss", "Muscle Gain", "Skill Development"])
            
            if st.button("✨ Generate New Plan"):
                with st.spinner("Creating your personalized plan..."):
                    plan_data = generate_training_plan(gemini_model, st.session_state.profile, duration)
                    if plan_data:
                        try:
                            st.session_state.generated_plan = plan_data
                            if db:
                                db.collection('plans').document(st.session_state.user).collection('training_plans').add({
                                    "plan": plan_data,
                                    "created_at": datetime.now().isoformat(),
                                    "duration": duration,
                                    "focus": focus
                                })
                            st.success("Plan generated successfully!")
                        except Exception as e:
                            st.error(f"Failed to save plan: {e}")
            
            if st.session_state.generated_plan:
                st.subheader("Your Current Plan")
                plan = st.session_state.generated_plan.get('trainingPlan', {})
                
                st.write(f"**Sport:** {plan.get('sport', 'N/A')}")
                st.write(f"**Level:** {plan.get('level', 'N/A')}")
                st.write(f"**Goals:** {plan.get('goals', 'N/A')}")
                st.write(f"**Equipment:** {plan.get('equipment', 'N/A')}")
                
                for week in plan.get('weeks', []):
                    with st.expander(f"Week {week.get('weekNumber')} - {week.get('focus')}"):
                        for day in week.get('days', []):
                            st.write(f"**{day.get('day')}:** {day.get('workout')}")
                            if day.get('details'):
                                st.caption(day.get('details'))
                
                st.download_button(
                    "📥 Download Plan",
                    data=json.dumps(st.session_state.generated_plan, indent=2),
                    file_name=f"training_plan_{datetime.now().date()}.json",
                    mime="application/json"
                )

        elif app_mode == "💬 AI Coach":
            st.header("AI Coach Chat")
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            if prompt := st.chat_input("Ask your coach anything..."):
                st.session_state.chat_history.append({"role":"user","content":prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.spinner("Thinking..."):
                    response = chat_with_coach(gemini_model, st.session_state.profile, st.session_state.chat_history, prompt)
                    if response:
                        st.session_state.chat_history.append({"role":"assistant","content":response})
                        if db:
                            try:
                                db.collection('chats').document(st.session_state.user).collection('messages').add({
                                    "message": prompt, 
                                    "response": response, 
                                    "timestamp": datetime.now().isoformat()
                                })
                            except Exception as e:
                                st.warning(f"Failed to persist chat: {e}")
                        with st.chat_message("assistant"):
                            st.markdown(response)

if __name__ == "__main__":
    main()