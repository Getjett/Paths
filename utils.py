import os
import json
import openai
from datetime import datetime
import streamlit as st
import uuid

# AI Functions
def chat_with_ai(message, space_topic, customization=None):
    if not customization:
        customization = st.session_state.content_customization
    
    # Prepare the message with customization settings
    system_message = f"""
    You are an expert tutor on the topic: {space_topic}.
    Generate educational content with these preferences:
    - Difficulty Level: {customization['difficulty_level']}
    - Content Format: {customization['content_format']}
    - Learning Style: {customization['learning_style']}
    
    Always provide accurate, well-structured explanations that are easy to understand.
    Use markdown formatting for better readability.
    """
    
    try:
        messages = [
            {"role": "system", "content": system_message},
        ]
        
        # Add chat history for context
        if space_topic in st.session_state.chat_history:
            messages.extend(st.session_state.chat_history[space_topic][-5:])  # Last 5 messages for context
        
        # Add the new user message
        messages.append({"role": "user", "content": message})
        
        # Get response from OpenAI
        response = openai.chat.completions.create(
            model="gpt-4",  # You can change this to your preferred model
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        ai_response = response.choices[0].message.content
        
        # Update chat history
        if space_topic not in st.session_state.chat_history:
            st.session_state.chat_history[space_topic] = []
        
        st.session_state.chat_history[space_topic].append({"role": "user", "content": message})
        st.session_state.chat_history[space_topic].append({"role": "assistant", "content": ai_response})
        
        return ai_response
        
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"

def generate_learning_content(topic, customization=None):
    if not customization:
        customization = st.session_state.content_customization
    
    prompt = f"""
    Create a comprehensive introduction to {topic} with these specifications:
    - Difficulty Level: {customization['difficulty_level']}
    - Content Format: {customization['content_format']}
    - Learning Style: {customization['learning_style']}
    
    Include:
    1. A brief overview of {topic}
    2. Key concepts to understand
    3. Why this topic is important
    4. How to approach learning this topic
    5. A learning path or roadmap
    
    Format the response with proper Markdown formatting, including:
    - Headers and subheaders
    - Bullet points where appropriate
    - Code examples if relevant
    - Bold or italic text for emphasis
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",  # You can change this to your preferred model
            messages=[
                {"role": "system", "content": "You are an educational content creator who specializes in creating engaging learning materials."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating content: {str(e)}"

def generate_quiz_questions(topic, difficulty="intermediate", num_questions=5):
    """Generate quiz questions for a given topic"""
    
    prompt = f"""
    Create {num_questions} quiz questions on the topic of "{topic}" at a {difficulty} difficulty level.
    
    For each question:
    1. Provide a clear question
    2. Include 4 possible answers (A, B, C, D)
    3. Indicate the correct answer
    4. Add a brief explanation of why the answer is correct
    
    Format the output as a structured JSON list of question objects:
    [
        {{
            "question": "Question text here?",
            "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
            "answer": "B",
            "explanation": "Explanation of why Option 2 is correct."
        }},
        ...
    ]
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an educational content creator skilled at creating assessment materials."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        questions = json.loads(content)
        
        return questions.get("questions", []) if isinstance(questions, dict) else questions
        
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return []

def generate_learning_resources(topic):
    """Generate recommended learning resources for a topic"""
    
    prompt = f"""
    Provide a curated list of learning resources for the topic: "{topic}"
    
    Include:
    1. Books (2-3 recommendations)
    2. Online courses (2-3 platforms)
    3. YouTube channels or specific videos
    4. Websites, blogs, or documentation
    5. Forums or communities for discussion
    
    Format the output as JSON with these categories:
    {{
        "books": [{"title": "Book Title", "author": "Author Name", "description": "Brief description"}],
        "courses": [{"platform": "Platform Name", "title": "Course Title", "link": "generic-url-placeholder", "description": "Brief description"}],
        "videos": [{"channel": "Channel Name", "title": "Video Title", "description": "Brief description"}],
        "websites": [{"name": "Website Name", "description": "What this site offers"}],
        "communities": [{"name": "Community Name", "description": "What this community offers"}]
    }}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable educator who knows about learning resources across many fields."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        resources = json.loads(content)
        return resources
        
    except Exception as e:
        st.error(f"Error generating resources: {str(e)}")
        return {}

# Data storage and retrieval functions
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create default users file if it doesn't exist
        default_users = {"admin": "password"}
        with open("users.json", "w") as f:
            json.dump(default_users, f)
        return default_users

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def load_user_spaces():
    try:
        with open("user_spaces.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create empty spaces file if it doesn't exist
        with open("user_spaces.json", "w") as f:
            json.dump({}, f)
        return {}

def save_user_spaces(spaces):
    with open("user_spaces.json", "w") as f:
        json.dump(spaces, f)

def create_learning_space(username, topic):
    user_spaces = load_user_spaces()
    
    if username not in user_spaces:
        user_spaces[username] = []
    
    # Generate a unique ID for the space
    space_id = str(uuid.uuid4())
    
    # Create the space
    new_space = {
        "id": space_id,
        "topic": topic,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_accessed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": generate_learning_content(topic),
        "resources": generate_learning_resources(topic),
        "has_quiz": False,
        "quiz_questions": []
    }
    
    user_spaces[username].append(new_space)
    save_user_spaces(user_spaces)
    
    # Update session state
    st.session_state.user_spaces = user_spaces
    
    return space_id

# UI Helper Functions
def display_space_card(space, index):
    """Display a card for a learning space with all actions"""
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{space['topic']}**")
            st.caption(f"Created: {space['created_at']}")
            st.caption(f"Last accessed: {space['last_accessed']}")
        
        with col2:
            if st.button("Learn", key=f"learn_{index}_{space['id']}"):
                st.session_state.current_space = space['id']
                st.session_state.space_view = "content"
                # Update last accessed time
                update_space_last_accessed(space['id'])
                st.rerun()
        
        with col3:
            if st.button("Quiz", key=f"quiz_{index}_{space['id']}"):
                st.session_state.current_space = space['id']
                st.session_state.space_view = "quiz"
                update_space_last_accessed(space['id'])
                st.rerun()
        
        with col4:
            if st.button("Delete", key=f"delete_{index}_{space['id']}"):
                delete_space(space['id'])
                st.rerun()
        
        st.divider()

def update_space_last_accessed(space_id):
    """Update the last accessed time for a space"""
    user_spaces = load_user_spaces()
    username = st.session_state.username
    
    if username in user_spaces:
        for space in user_spaces[username]:
            if space['id'] == space_id:
                space['last_accessed'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        
        save_user_spaces(user_spaces)

def delete_space(space_id):
    """Delete a learning space"""
    user_spaces = load_user_spaces()
    username = st.session_state.username
    
    if username in user_spaces:
        # Remove the space from user's spaces
        user_spaces[username] = [s for s in user_spaces[username] if s['id'] != space_id]
        save_user_spaces(user_spaces)
        
        # Update session state
        st.session_state.user_spaces = user_spaces
        if st.session_state.current_space == space_id:
            st.session_state.current_space = None
            st.session_state.space_view = None
    
def get_space_by_id(space_id):
    """Get a space by its ID"""
    user_spaces = load_user_spaces()
    username = st.session_state.username
    
    if username in user_spaces:
        for space in user_spaces[username]:
            if space['id'] == space_id:
                return space
    
    return None

def update_space(space):
    """Update a space in the storage"""
    user_spaces = load_user_spaces()
    username = st.session_state.username
    
    if username in user_spaces:
        for i, s in enumerate(user_spaces[username]):
            if s['id'] == space['id']:
                user_spaces[username][i] = space
                save_user_spaces(user_spaces)
                return True
    
    return False
