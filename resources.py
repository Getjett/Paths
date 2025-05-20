import streamlit as st
from utils import get_space_by_id, update_space, generate_learning_resources

def resources_view(space_id):
    """Display learning resources for the given space"""
    space = get_space_by_id(space_id)
    
    if not space:
        st.error("Space not found!")
        st.session_state.current_space = None
        st.session_state.space_view = None
        st.rerun()
        return
    
    st.title(f"Learning Resources: {space['topic']}")
    
    # Sidebar with navigation
    with st.sidebar:
        if st.button("Back to Learning Content"):
            st.session_state.space_view = "content"
            st.rerun()
        
        if st.button("Back to Dashboard"):
            st.session_state.current_space = None
            st.session_state.space_view = None
            st.rerun()
    
    # Check if resources exist or need to be generated
    if not space.get('resources'):
        with st.spinner("Gathering learning resources..."):
            st.info("Finding the best learning resources for this topic.")
            
            # Generate resources
            resources = generate_learning_resources(space['topic'])
            
            # Update space with resources
            space['resources'] = resources
            update_space(space)
    
    resources = space.get('resources', {})
    
    if not resources:
        st.error("Failed to generate learning resources. Please try again later.")
        return
    
    # Display resources
    display_resources(resources)

def display_resources(resources):
    """Display formatted learning resources"""
    
    # Books section
    if 'books' in resources and resources['books']:
        st.header("📚 Recommended Books")
        for book in resources['books']:
            with st.container():
                st.subheader(book['title'])
                st.caption(f"by {book['author']}")
                st.write(book['description'])
                st.divider()
    
    # Courses section
    if 'courses' in resources and resources['courses']:
        st.header("🎓 Online Courses")
        for course in resources['courses']:
            with st.container():
                st.subheader(course['title'])
                st.caption(f"Platform: {course['platform']}")
                st.write(course['description'])
                st.divider()
    
    # Videos section
    if 'videos' in resources and resources['videos']:
        st.header("🎬 Video Resources")
        for video in resources['videos']:
            with st.container():
                st.subheader(video['title'])
                st.caption(f"Channel: {video['channel']}")
                st.write(video['description'])
                st.divider()
    
    # Websites section
    if 'websites' in resources and resources['websites']:
        st.header("🌐 Helpful Websites")
        for website in resources['websites']:
            with st.container():
                st.subheader(website['name'])
                st.write(website['description'])
                st.divider()
    
    # Communities section
    if 'communities' in resources and resources['communities']:
        st.header("👥 Communities & Forums")
        for community in resources['communities']:
            with st.container():
                st.subheader(community['name'])
                st.write(community['description'])
                st.divider()
    
    # Note about links
    st.info("Note: Due to security constraints, actual URLs are not provided. You can search for these resources using your preferred search engine.")
