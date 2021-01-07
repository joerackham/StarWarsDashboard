import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

FILMS = ["A New Hope", "The Empire Strikes Back", "Return of the Jedi"]
FILM_OFFSET = 4

@st.cache(persist=True)
def load_data(film_num):
    data = pd.read_csv('./Episode' + str(film_num) + '.txt', sep=" ", header=None)
    return data

st.title("Analysing who says what in the first three Star Wars films 🚀")
st.sidebar.title("Who says what in the first three Star Wars films?")
st.sidebar.write("By Joe Rackham")
flim_choice = st.sidebar.multiselect('Which films do you want to show data for?', FILMS)

if(len(flim_choice) != 0):
    data = [(load_data(FILMS.index(film) + 4), film) for film in flim_choice]

    # Lines by speaker
    st.markdown("### How many lines does each character say?")
    st.markdown("Only actual dialogue counts. Sorry Chewy and R2...")
    lines_by_speaker = None
    for d, f in data:
        lines = d[1].value_counts()
        lines = pd.DataFrame({'Character': lines.index, 'Lines': lines.values, 'Film': f})
        lines_by_speaker = lines if lines_by_speaker is None else lines_by_speaker.append(lines)

    lines_by_speaker_trimmed = lines_by_speaker[lines_by_speaker['Lines'] > 10]
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

    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', height=640, width=800).generate(all_lines)
    fig, ax = plt.subplots()
    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot(fig)

    st.markdown("### And just the character you're focussing on")
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', height=640, width=800).generate(char_lines)
    fig, ax = plt.subplots()
    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot(fig)

    
    # How positive
    st.markdown('### How positive are the characters?')
    st.markdown('Based on the sentiment of what they say')
    sid = SentimentIntensityAnalyzer()
    
    char_sent = []
    for c in characters:
        sentiment = 0.0
        num_lines = 0
        for d, f in data:
            d_char = d[d[1] == c]
            for line in d_char[2]:
                i = sid.polarity_scores(line)
                sentiment += i['compound']
                num_lines += 1

        char_sent.append(sentiment / num_lines)
    
    sentiment_data = pd.DataFrame({'Character': characters, 'Sentiment': char_sent})
    fig = px.bar(sentiment_data, height=750, width=800, x='Character', y='Sentiment', color='Sentiment')
    st.write(fig)

