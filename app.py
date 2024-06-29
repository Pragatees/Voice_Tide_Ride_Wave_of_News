import streamlit as st
import requests
import speech_recognition as sr
import sounddevice as sd
import wavio
import pycountry

# Function to record audio
def record_audio(filename, duration=5, fs=44100):
    st.write("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    wavio.write(filename, recording, fs, sampwidth=2)
    st.write("Recording finished")

# Function to recognize speech
def recognize_speech(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = r.record(source)
    
    try:
        command = r.recognize_google(audio).lower()
        return command
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return None
    except sr.RequestError:
        st.error("Speech recognition service unavailable")
        return None

# Function to fetch news
def fetch_news(country, category):
    country_info = pycountry.countries.get(name=country)
    if not country_info:
        st.error("Country not found. Please enter a valid country name.")
        return
    
    country_code = country_info.alpha_2
    url = f"https://newsapi.org/v2/top-headlines?country={country_code}&category={category.lower()}&apiKey=d771dc26889c458b8a07bd7e261224f6"
    response = requests.get(url)
    
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        
        if articles:
            for article in articles:
                st.header(article.get('title', 'No title'))
                st.write(article.get('publishedAt', 'No publication date'))
                if article.get('author'):
                    st.write(article.get('author', 'No author'))
                st.write(article['source'].get('name', 'No source name'))
                st.write(article.get('description', 'No description'))
                image_url = article.get('urlToImage')
                if image_url:
                    try:
                        st.image(image_url, width=600)  # Adjust width as needed
                    except Exception as e:
                        st.error(f"Failed to load image: {e}")
                        st.image('https://cdn.pixabay.com/photo/2017/06/26/19/03/news-2444778_960_720.jpg', width=600)
                else:
                    st.image('https://cdn.pixabay.com/photo/2017/06/26/19/03/news-2444778_960_720.jpg', width=600)
                st.write(article.get('url', 'No URL'))
                st.write('---')
        else:
            st.error("No articles found.")
    else:
        st.error(f"Failed to fetch news, status code: {response.status_code}")

# Setting up the Streamlit app layout and styles
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5;
        color: #333;
    }
    .main-header {
        text-align: center;
        padding: 20px;
        color: white;
        background-color: #4CAF50;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-content {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stRadio>div>div {
        display: flex;
        justify-content: center;
    }
    .stRadio>div>div>label>div {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 5px;
        background-color: #e7e7e7;
        margin: 0 5px;
    }
    .stRadio>div>div>label>div:hover {
        background-color: #ddd;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Voice Tide: Ride the Wave of News</h1>", unsafe_allow_html=True)

st.markdown("<div class='main-content'>", unsafe_allow_html=True)

st.write("Choose your preferred input method:")

input_method = st.radio("Input Method", ("Voice Command", "Manual Input"))

if input_method == "Voice Command":
    st.write("Press the button and say the command (e.g., 'latest news of India in Technology')")
    if st.button('Record Command'):
        record_audio('command.wav')
        command = recognize_speech('command.wav')
        
        if command:
            st.write(f"Recognized command: {command}")
            parts = command.split(' ')
            
            if len(parts) >= 4 and parts[0] == "latest" and parts[1] == "news" and parts[2] == "of":
                country = parts[3]
                category = ' '.join(parts[5:]) if len(parts) > 5 else "general"
                
                st.write(f"Fetching news for {country} in category {category}")
                fetch_news(country, category)
            else:
                st.error("Command not recognized. Please say 'latest news of <country> in <category>'")

elif input_method == "Manual Input":
    col1, col2 = st.columns([3, 2])
    with col1:
        user = st.text_input("Enter your country")
    with col2:
        cat = st.radio("Select your news Category", ("Technology", "Politics", "Sports", "Business", "General"))
        btn = st.button("Fetch News")

    if btn:
        country = pycountry.countries.get(name=user)
        if country:
            country_code = country.alpha_2
            fetch_news(user, cat)
        else:
            st.error("Country not found. Please enter a valid country name.")

st.markdown("</div>", unsafe_allow_html=True)
