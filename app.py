import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from PIL import Image

FILMS = ["A New Hope", "The Empire Strikes Back", "Return of the Jedi"]
FILM_OFFSET = 4

@st.cache(persist=True)
def load_data(film_num):
    data = pd.read_csv('./Data/Episode' + str(film_num) + '.txt', sep=" ", header=None)
    return data

def write_wordcloud(data):
    wordcloud = WordCloud(stopwords=STOPWORDS, font_path='./StarJedi.ttf', background_color='white', height=640, width=800).generate(data)
    fig, ax = plt.subplots()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    st.pyplot(fig)

st.title("Analysing who says what in the first three Star Wars films 🚀")
st.sidebar.title("Who says what in the first three Star Wars films?")
st.sidebar.markdown("By [Joe Rackham](https://joealexanderrackham.co.uk/)")
flim_choice = st.sidebar.multiselect('Which films do you want to show data for?', FILMS)

if(len(flim_choice) != 0):
    data = [(load_data(FILMS.index(film) + 4), film) for film in flim_choice]

    min_lines = st.sidebar.slider("Minimum number of lines to be considered", 10, 100)

    # Lines by speaker
    st.markdown("### How many lines does each character say?")
    st.markdown("Only actual dialogue counts. Sorry Chewy and Artoo...")
    lines_by_speaker = None
    for d, f in data:
        lines = d[1].value_counts()
        lines = pd.DataFrame({'Character': lines.index, 'Lines': lines.values, 'Film': f})
        lines_by_speaker = lines if lines_by_speaker is None else lines_by_speaker.append(lines)

    lines_by_speaker_trimmed = lines_by_speaker[lines_by_speaker['Lines'] > min_lines]
    fig = px.bar(lines_by_speaker_trimmed, height=750, width=800, x='Character', y='Lines', color='Film')
    st.write(fig)

    characters = list(set(lines_by_speaker_trimmed["Character"]))
    char_choice = st.sidebar.selectbox('Which character do you want to focus on?', characters)

    #Word Cloud for a speaker
    st.markdown("### Here's what they say in a Word Cloud")

    all_lines = ''
    char_lines = ''
    for d, f in data:
        d_char = d[d[1] == char_choice]
        all_lines += ' '.join(d[2])
        char_lines += ' '.join(d_char[2])

    write_wordcloud(all_lines)

    st.markdown("### And just the character you're focussing on")
    write_wordcloud(char_lines)
    
    # How positive
    st.markdown('### How positive are the characters?')
    st.markdown('Based on the sentiment of what they say')
    sid = SentimentIntensityAnalyzer()
    
    char_sent = []
    char_line_length = []
    for c in characters:
        sentiment = 0.0
        length = 0
        num_lines = 0
        for d, f in data:
            d_char = d[d[1] == c]
            for line in d_char[2]:
                i = sid.polarity_scores(line)
                sentiment += i['compound']
                length += len(line.split())
                num_lines += 1

        char_sent.append(sentiment / num_lines)
        char_line_length.append(length / num_lines)
    
    sentiment_data = pd.DataFrame({'Character': characters, 'Sentiment': char_sent})
    fig = px.bar(sentiment_data, height=750, width=800, x='Character', y='Sentiment', color='Sentiment')
    st.write(fig)


    # Longest lines
    st.markdown("### Whose the monologuer?")
    st.markdown("Which character has the longest lines?")

    sentiment_data = pd.DataFrame({'Character': characters, 'Average Line Length': char_line_length})
    fig = px.bar(sentiment_data, height=750, width=800, x='Character', y='Average Line Length')
    st.write(fig)
else:
    st.markdown("## Pick a film on the sidebar to get started...")
    image = Image.open('./red-dotted-left-arrow.png')
    st.image(image, width=250)