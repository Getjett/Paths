import os
import streamlit as st
from datetime import datetime
import json
import openai
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_spaces' not in st.session_state:
    st.session_state.user_spaces = {}
if 'current_space' not in st.session_state:
    st.session_state.current_space = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'content_customization' not in st.session_state:
    st.session_state.content_customization = {
        'difficulty_level': 'Intermediate',
        'content_format': 'Mixed (Text, Images, Code)',
        'learning_style': 'Conceptual'
    }

# Load users from JSON file (or create it if it doesn't exist)
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

# Save users to JSON file
def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# Load user spaces from JSON file (or create it if it doesn't exist)
def load_user_spaces():
    try:
        with open("user_spaces.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create empty spaces file if it doesn't exist
        with open("user_spaces.json", "w") as f:
            json.dump({}, f)
        return {}

# Save user spaces to JSON file
def save_user_spaces(spaces):
    with open("user_spaces.json", "w") as f:
        json.dump(spaces, f)

# Chat with AI
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

# Generate learning content
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

# Create a new learning space
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
        "content": generate_learning_content(topic)
    }
    
    user_spaces[username].append(new_space)
    save_user_spaces(user_spaces)
    
    # Update session state
    st.session_state.user_spaces = user_spaces
    
    return space_id

# Login page
def login_page():
    st.title("Learning Tool Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("Login")
        
        if submitted:
            users = load_users()
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                
                # Load user's spaces
                user_spaces = load_user_spaces()
                if username in user_spaces:
                    st.session_state.user_spaces = user_spaces
                
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    # Add a register option
    with st.expander("Create an account"):
        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            register_submitted = st.form_submit_button("Register")
            
            if register_submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    users = load_users()
                    if new_username in users:
                        st.error("Username already exists")
                    else:
                        users[new_username] = new_password
                        save_users(users)
                        st.success("Registration successful! You can now log in.")

# Dashboard page
def dashboard_page():
    st.title(f"Welcome, {st.session_state.username}!")
    
    # Sidebar with logout button
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.current_space = None
            st.rerun()
    
    # Create a new learning space
    with st.expander("Create a New Learning Space", expanded=True):
        with st.form("create_space_form"):
            topic = st.text_input("What topic would you like to master?")
            submitted = st.form_submit_button("Create Space")
            
            if submitted and topic:
                space_id = create_learning_space(st.session_state.username, topic)
                st.session_state.current_space = space_id
                st.success(f"Created a new learning space for {topic}!")
                st.rerun()
    
    # Display existing spaces
    st.subheader("Your Learning Spaces")
    
    user_spaces = load_user_spaces()
    if st.session_state.username in user_spaces and user_spaces[st.session_state.username]:
        spaces = user_spaces[st.session_state.username]
        
        for space in spaces:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{space['topic']}**")
                st.caption(f"Created: {space['created_at']}")
            
            with col2:
                if st.button("Learn", key=f"learn_{space['id']}"):
                    st.session_state.current_space = space['id']
                    # Update last accessed time
                    for s in user_spaces[st.session_state.username]:
                        if s['id'] == space['id']:
                            s['last_accessed'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_user_spaces(user_spaces)
                    st.rerun()
            
            with col3:
                if st.button("Delete", key=f"delete_{space['id']}"):
                    # Remove the space from user's spaces
                    user_spaces[st.session_state.username] = [s for s in user_spaces[st.session_state.username] if s['id'] != space['id']]
                    save_user_spaces(user_spaces)
                    
                    # Update session state
                    st.session_state.user_spaces = user_spaces
                    if st.session_state.current_space == space['id']:
                        st.session_state.current_space = None
                    
                    st.rerun()
            
            st.divider()
    else:
        st.info("You don't have any learning spaces yet. Create one above to get started!")

# Learning space page
def learning_space_page(space_id):
    user_spaces = load_user_spaces()
    
    # Find the space with the given ID
    space = None
    for s in user_spaces[st.session_state.username]:
        if s['id'] == space_id:
            space = s
            break
    
    if not space:
        st.error("Space not found!")
        st.session_state.current_space = None
        st.rerun()
        return
    
    # Sidebar with customization options and back button
    with st.sidebar:
        st.subheader("Customize Content")
        
        # Customization options
        difficulty_level = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced", "Expert"],
            index=["Beginner", "Intermediate", "Advanced", "Expert"].index(st.session_state.content_customization['difficulty_level'])
        )
        
        content_format = st.selectbox(
            "Content Format",
            ["Text-only", "Mixed (Text, Images, Code)", "Code-focused", "Interactive"],
            index=["Text-only", "Mixed (Text, Images, Code)", "Code-focused", "Interactive"].index(st.session_state.content_customization['content_format'])
        )
        
        learning_style = st.selectbox(
            "Learning Style",
            ["Conceptual", "Practical", "Project-based", "Question-driven"],
            index=["Conceptual", "Practical", "Project-based", "Question-driven"].index(st.session_state.content_customization['learning_style'])
        )
        
        # Apply button for customization
        if st.button("Apply Customization"):
            st.session_state.content_customization = {
                'difficulty_level': difficulty_level,
                'content_format': content_format,
                'learning_style': learning_style
            }
            
            # Regenerate content with new customization
            space['content'] = generate_learning_content(space['topic'], st.session_state.content_customization)
            
            # Save updated space
            for i, s in enumerate(user_spaces[st.session_state.username]):
                if s['id'] == space_id:
                    user_spaces[st.session_state.username][i] = space
                    break
            
            save_user_spaces(user_spaces)
            st.rerun()
        
        if st.button("Back to Dashboard"):
            st.session_state.current_space = None
            st.rerun()
    
    # Main content
    st.title(f"Learning: {space['topic']}")
    
    # Display generated content
    st.markdown(space['content'])
    
    # Chat interface
    st.subheader("Ask Questions")
    
    # Input for user questions
    user_question = st.text_input("Type your question here...", key="user_question")
    
    if st.button("Send"):
        if user_question:
            # Display user question
            with st.chat_message("user"):
                st.write(user_question)
            
            # Get AI response
            ai_response = chat_with_ai(user_question, space['topic'])
            
            # Display AI response
            with st.chat_message("assistant"):
                st.markdown(ai_response)
            
            # Clear the input field
            st.session_state.user_question = ""
    
    # Display chat history
    if space['topic'] in st.session_state.chat_history:
        st.subheader("Chat History")
        
        for message in st.session_state.chat_history[space['topic']]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Main app
def main():
    st.set_page_config(
        page_title="Learning Tool",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        login_page()
    else:
        # Check if a space is selected
        if st.session_state.current_space:
            learning_space_page(st.session_state.current_space)
        else:
            dashboard_page()

if __name__ == "__main__":
    main()
