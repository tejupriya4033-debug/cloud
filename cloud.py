import streamlit as st
import wikipedia
import speech_recognition as sr
from googlesearch import search
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Chatbot with Mic at Bottom", layout="wide")

# Title at top
st.title("🧠 Enhanced Python Chatbot with Wikipedia, Google & Microphone")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Functions
def get_wikipedia_image(query):
    try:
        page = wikipedia.page(query)
        images = page.images
        for img_url in images:
            if img_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return img_url
        return None
    except Exception:
        return None

def get_snippet_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        description = soup.find('meta', attrs={'name':'description'})
        if description and description.get('content'):
            return description['content']
        p = soup.find('p')
        if p:
            return p.get_text()
        return "No snippet available."
    except Exception:
        return "Failed to fetch snippet."

def chatbot_response(user_input):
    user_input_lower = user_input.lower()
    if "hello" in user_input_lower or "hi" in user_input_lower:
        return "Hello! How can I help you today?"
    elif "your name" in user_input_lower:
        return "I'm a Streamlit Chatbot created in Python!"
    elif "bye" in user_input_lower:
        return "Goodbye! Have a great day."
    elif "image of" in user_input_lower:
        query = user_input_lower.split("image of")[-1].strip()
        img_url = get_wikipedia_image(query)
        if img_url:
            return f"🖼️ Here's an image from Wikipedia for '{query}':\n{img_url}"
        else:
            return f"❌ Sorry, I couldn't find an image for '{query}' on Wikipedia."
    else:
        try:
            summary = wikipedia.summary(user_input, sentences=2)
            return f"📖 From Wikipedia:\n\n{summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            options = ', '.join(e.options[:5])
            return f"⚠ That query is too broad. Did you mean: {options}?"
        except wikipedia.exceptions.PageError:
            try:
                results = list(search(user_input, num_results=3))
                if not results:
                    return "❌ Sorry, I couldn't find anything on Wikipedia or Google for that."
                response = "🔎 From Google search results:\n"
                for url in results:
                    snippet = get_snippet_from_url(url)
                    response += f"\n- {url}\n  Snippet: {snippet}\n"
                return response
            except Exception as e:
                return f"⚠ An error occurred during Google search: {e}"
        except Exception as e:
            return f"⚠ An error occurred: {e}"

# Display conversation messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "bot" and "🖼️ Here's an image from Wikipedia" in msg["content"]:
            lines = msg["content"].split('\n')
            img_url = lines[-1].strip()
            st.write(lines[0])
            st.image(img_url)
        else:
            st.write(msg["content"])

# Input and mic button at bottom
input_container = st.empty()

with input_container.container():
    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.chat_input("Type your message...")
    with col2:
        mic_clicked = st.button("🎤")

    if mic_clicked:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Please speak now.")
            audio = recognizer.listen(source, phrase_time_limit=5)
        try:
            user_input = recognizer.recognize_google(audio)
            st.success(f"You said: {user_input}")
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
            user_input = None
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
            user_input = None

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = chatbot_response(user_input)
        st.session_state.messages.append({"role": "bot", "content": response})
        st.session_state.search_history.append((user_input, response))
        st.rerun()   # ✅ modern replacement

# Sidebar with updated header
with st.sidebar:
    st.header("📜 History")
    if st.session_state.search_history:
        for i, (query, answer) in enumerate(reversed(st.session_state.search_history), 1):
            st.markdown(f"**{i}. You:** {query}")
            short_answer = answer if len(answer) < 200 else answer[:200] + "..."
            st.markdown(f"**Bot:** {short_answer}")
            st.markdown("---")
    else:
        st.write("No search history yet.")
