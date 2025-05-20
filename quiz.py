import streamlit as st
from utils import get_space_by_id, update_space, generate_quiz_questions

def quiz_view(space_id):
    """Display a quiz view for the given space"""
    space = get_space_by_id(space_id)
    
    if not space:
        st.error("Space not found!")
        st.session_state.current_space = None
        st.session_state.space_view = None
        st.rerun()
        return
    
    st.title(f"Quiz: {space['topic']}")
    
    # Sidebar with back button
    with st.sidebar:
        if st.button("Back to Learning Content"):
            st.session_state.space_view = "content"
            st.rerun()
        
        if st.button("Back to Dashboard"):
            st.session_state.current_space = None
            st.session_state.space_view = None
            st.rerun()
    
    # Initialize quiz state if needed
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'submitted_answers' not in st.session_state:
        st.session_state.submitted_answers = {}
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    
    # Check if quiz questions exist or need to be generated
    if not space.get('has_quiz', False) or not space.get('quiz_questions'):
        with st.spinner("Generating quiz questions..."):
            st.info("Creating a quiz to test your knowledge on this topic.")
            
            # Generate quiz questions
            difficulty = st.session_state.content_customization['difficulty_level'].lower()
            questions = generate_quiz_questions(space['topic'], difficulty)
            
            # Update space with quiz questions
            space['has_quiz'] = True
            space['quiz_questions'] = questions
            update_space(space)
    
    questions = space.get('quiz_questions', [])
    
    if not questions:
        st.error("Failed to generate quiz questions. Please try again later.")
        return
    
    # Display quiz
    if st.session_state.quiz_completed:
        display_quiz_results(questions)
    else:
        display_quiz_questions(questions)

def display_quiz_questions(questions):
    """Display the current quiz question"""
    if not questions:
        return
    
    # Show progress
    total_questions = len(questions)
    current_q = st.session_state.current_question
    
    st.progress(current_q / total_questions)
    st.write(f"Question {current_q + 1} of {total_questions}")
    
    # Display current question
    if current_q < total_questions:
        question = questions[current_q]
        
        st.subheader(question['question'])
        
        # Display options
        option = st.radio("Select your answer:", question['options'], key=f"q{current_q}")
        
        # Navigation buttons
        cols = st.columns([1, 1, 4])
        
        with cols[0]:
            if current_q > 0 and st.button("Previous"):
                st.session_state.current_question -= 1
                st.rerun()
        
        with cols[1]:
            if st.button("Submit Answer"):
                # Record answer
                selected_option = option[0]  # Get the letter (A, B, C, D)
                st.session_state.submitted_answers[current_q] = selected_option
                
                # Move to next question or complete quiz
                if current_q < total_questions - 1:
                    st.session_state.current_question += 1
                    st.rerun()
                else:
                    st.session_state.quiz_completed = True
                    calculate_score(questions)
                    st.rerun()

def calculate_score(questions):
    """Calculate the quiz score"""
    score = 0
    total = len(questions)
    
    for i, question in enumerate(questions):
        if i in st.session_state.submitted_answers:
            user_answer = st.session_state.submitted_answers[i]
            correct_answer = question['answer']
            
            if user_answer == correct_answer:
                score += 1
    
    st.session_state.score = score
    st.session_state.total_questions = total

def display_quiz_results(questions):
    """Display the quiz results"""
    score = st.session_state.score
    total = st.session_state.total_questions
    
    # Display score
    st.subheader("Quiz Results")
    
    # Create a progress bar for the score
    score_percentage = (score / total) * 100
    st.progress(score / total)
    
    # Display score text with appropriate color and message
    if score_percentage >= 80:
        st.success(f"Great job! You scored {score}/{total} ({score_percentage:.1f}%)")
    elif score_percentage >= 60:
        st.info(f"Good effort! You scored {score}/{total} ({score_percentage:.1f}%)")
    else:
        st.warning(f"You scored {score}/{total} ({score_percentage:.1f}%). Keep studying!")
    
    # Review answers
    st.subheader("Review Your Answers")
    
    for i, question in enumerate(questions):
        with st.expander(f"Question {i+1}: {question['question']}"):
            user_answer = st.session_state.submitted_answers.get(i, "Not answered")
            correct_answer = question['answer']
            
            # Display all options
            for option in question['options']:
                option_letter = option[0]
                
                if option_letter == user_answer and option_letter == correct_answer:
                    st.markdown(f"✅ **{option}** (Your answer, Correct)")
                elif option_letter == user_answer:
                    st.markdown(f"❌ **{option}** (Your answer)")
                elif option_letter == correct_answer:
                    st.markdown(f"✅ {option} (Correct answer)")
                else:
                    st.markdown(f"  {option}")
            
            # Display explanation
            st.markdown("**Explanation:**")
            st.markdown(question['explanation'])
    
    # Option to retry
    if st.button("Retry Quiz"):
        # Reset quiz state
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.submitted_answers = {}
        st.session_state.quiz_completed = False
        st.rerun()
