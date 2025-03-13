import streamlit as st
import pandas as pd
import requests
import pickle
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("api_key") 

current_dir = os.path.dirname(os.path.abspath(__file__))                          
file_path = os.path.join(current_dir, 'movie_data.sav')                                

if os.path.exists(file_path):
    with open(file_path, 'rb') as f:
        movies, cosine_sim = pickle.load(f)
    print("Movie data loaded successfully!")
else:
    st.error(f"Error: The file 'movie_data.sav' was not found in {current_dir}")
    st.stop()

# Function to get movie recommendations
def get_recommendations(title, cosine_sim=cosine_sim):                                                                                                      
    try:
        idx = movies[movies['title'] == title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]  # Exclude the first (same movie)
        movie_indices = [x[0] for x in sim_scores]
        return movies.iloc[movie_indices][['title', 'id']]
    except IndexError:
        st.error("Error: Movie not found in dataset.")
        return pd.DataFrame() 

# Fetch movie poster from TMDB API
def fetch_poster(movie_id):  
    api_key = API_KEY  # Fetch API key from environment variables
    if not api_key:
        st.error("API key is missing. Check your .env file.")
        return "https://via.placeholder.com/150"  # Default placeholder

    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()

    if 'poster_path' in data and data['poster_path']:
        return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    else:
        return "https://via.placeholder.com/150"  # Default placeholder

st.title("BingeGuide")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.write("Top 10 recommended movies:")

    # Create a 2x5 grid layout
    for i in range(0, min(10, len(recommendations)), 5):  
        cols = st.columns(5)  # Create 5 columns per row
        for j in range(min(5, len(recommendations) - i)):  # Ensure no out-of-bounds
            movie = recommendations.iloc[i + j]
            poster_url = fetch_poster(movie['id'])
            with cols[j]:  # Use 'cols' instead of 'col'
                st.image(poster_url, width=130)
                st.write(movie['title'])
