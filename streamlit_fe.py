import streamlit as st
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000/generate-learning-path"

st.set_page_config(
    page_title="AI University",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------
# Sidebar (Search Panel)
# -----------------------------
st.sidebar.title("🎓 AI University")

query = st.sidebar.text_input(
    "What do you want to learn?",
    "Agentic AI"
)

level = st.sidebar.selectbox(
    "Level",
    ["BEGINNER", "INTERMEDIATE", "ADVANCED"]
)

duration = st.sidebar.selectbox(
    "Duration",
    ["1 Week", "2 Weeks", "4 Weeks", "6 Weeks"]
)

generate = st.sidebar.button("Generate Learning Path")

# -----------------------------
# Header
# -----------------------------
st.title("📚 Learning Dashboard")

# -----------------------------
# Call API
# -----------------------------
if generate:

    payload = {
        "query": query,
        "level": level,
        "duration": duration
    }

    with st.spinner("Building your learning plan..."):

        response = requests.post(API_URL, json=payload)

    data = response.json()

    learning_plan = data["learning_plan"]

    # -----------------------------
    # Render Learning Plan
    # -----------------------------
    for task in learning_plan:

        st.divider()

        st.subheader(f"📅 Week {task['week']} - Day {task['day']}")
        st.markdown(f"### {task['task']}")
        st.write(task["focus"])

        st.write("")

        for video in task["videos"]:

            col1, col2 = st.columns([1,2])

            # -----------------------------
            # Thumbnail
            # -----------------------------
            with col1:

                video_id = video["url"].split("v=")[-1]
                thumbnail = f"https://img.youtube.com/vi/{video_id}/0.jpg"

                st.image(thumbnail)

            # -----------------------------
            # Video Info
            # -----------------------------
            with col2:

                st.markdown(f"### [{video['title']}]({video['url']})")

                st.write(f"📺 Channel: **{video['channel']}**")

                stats = video["authority"]

                st.write(
                    f"""
                    👁 Views: {stats['views']:,}  
                    👍 Likes: {stats['likes']:,}  
                    💬 Comments: {stats['comments']:,}  
                    ⭐ Authority Score: {stats['score']}
                    """
                )

                st.caption(video["recommendation"])
