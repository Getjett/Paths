# Personalized Learning Tool Dashboard

A Streamlit-based dashboard for creating personalized learning spaces with AI-powered content generation.

## Features

- **User Authentication**: Secure login and registration system
- **Learning Space Creation**: Create custom learning spaces for any topic
- **Personalized Content**: AI-generated educational content tailored to your preferences
- **Content Customization**: Adjust difficulty, format, and learning style
- **Interactive Chat**: Ask questions and get AI-powered responses
- **Chat History**: Keep track of your learning conversations

## Setup and Installation

1. Clone this repository or download the files
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Usage

1. **Login or Register**: Start by creating an account or logging in
2. **Create a Learning Space**: Enter a topic you want to learn about
3. **Access Learning Content**: Click "Learn" to access your personalized learning space
4. **Customize Content**: Use the sidebar to adjust content to your preferences
5. **Ask Questions**: Use the chat interface at the bottom to ask questions

## Default Login

- **Username**: admin
- **Password**: password

## Customization Options

- **Difficulty Level**: Beginner, Intermediate, Advanced, Expert
- **Content Format**: Text-only, Mixed, Code-focused, Interactive
- **Learning Style**: Conceptual, Practical, Project-based, Question-driven

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection
