import pandas as pd 
#import dataLoader
from dataLoader import loadData_results

import streamlit as st
import hydralit_components as hc
st.set_page_config(layout='wide')

if 'Results' not in st.session_state:
    st.session_state['Results'] = loadData_results()

st.title('2024 Board Game Arena Journey: Race to 100 games')

st.write("We decided to start trying more games on board game arena and compile our thoughts about each one after we play. For each game, we assign a rating (typically after one play) and provide a concise summary of our thoughts. We also have kept track of who has won which games. Peruse to see what we've been playing!")



menu_data = [
    {'label':"Summary"},
    {'label':"Ratings"},
    {'label':"Reviews"}
]

menu = hc.nav_bar(menu_definition = menu_data, sticky_nav = True, sticky_mode = 'pinned')


if menu == 'Summary':

        #write the overall wins
    col1, col2, col3 = st.columns(3)
    col1.metric("Games Played", st.session_state['Results'].shape[0], st.session_state['Results'].shape[0])
    col2.metric("Sam's Wins", st.session_state['Results'][st.session_state['Results']['Who Won'] == 'Sam'].shape[0], 0)
    col3.metric("Gabi's Wins", st.session_state['Results'][st.session_state['Results']['Who Won'] == 'Gabi'].shape[0], 0)
    finished = st.session_state['Results'].sort_values('When finished', ascending = False).iloc[0]

    st.header('Our Most Recent Game')
    playing = ';'.join(st.session_state['Results'][st.session_state['Results']['When finished'].isna()]['Game'].values)
    col1, col2, col3 = st.columns(3)
    col1.write(f"We most recently finished playing {finished['Game']}")
    col1.write(f"{finished['Who Won']} Won!")
    col2.subheader("Sam's Review")
    col2.write(f"Rating = {finished['Sam\'s Rating']}")
    col2.write(f"{finished["Sam's Review"]}")
    col3.subheader("Gabi's Review")
    col3.write(f"Rating = {finished['Gabi\'s Rating']}")
    col3.write(f"{finished['Gabi\'s Review']}")

    #st.write(f"Here's what we are playing now: {playing}")



if menu == 'Ratings':
    ratings = st.session_state['Results'][['Game', "Sam's Rating", "Gabi's Rating"]].set_index('Game')
    reviews = st.session_state['Results'][['Game', "Sam's Review", "Gabi's Review"]].set_index('Game')
    st.header('Ratings and Reviews')

    ratings['Consensus'] = ratings.mean(axis = 1)

    sorting_ratings = ratings['Consensus'].sort_values(ascending = False)
    ranked_list = ''
    for rank, game in zip(range(1,sorting_ratings.shape[0]), sorting_ratings.index):
        ranked_list = ranked_list + f'{rank}. {game} ({round(sorting_ratings.loc[game],2)})\n'
        prev_rating = sorting_ratings.loc[game]

    #games ranked list
    col1, col2, col3 = st.columns(3)
    col1.subheader('Consensed Ratings')
    col1.write(ranked_list)

    sorting_ratings = ratings["Sam's Rating"].sort_values(ascending = False)
    ranked_list = ''
    for rank, game in zip(range(1,sorting_ratings.shape[0]), sorting_ratings.index):
        ranked_list = ranked_list + f'{rank}. {game} ({round(sorting_ratings.loc[game],2)})\n'
        prev_rating = sorting_ratings.loc[game]

    col2.subheader("Sam's Ratings")
    col2.write(ranked_list)

    sorting_ratings = ratings["Gabi's Rating"].sort_values(ascending = False)
    ranked_list = ''
    for rank, game in zip(range(1,sorting_ratings.shape[0]), sorting_ratings.index):
        ranked_list = ranked_list + f'{rank}. {game} ({round(sorting_ratings.loc[game],2)})\n'
        prev_rating = sorting_ratings.loc[game]
    
    col3.subheader("Gabi's Ratings")
    col3.write(ranked_list)

if menu == 'Reviews':
    st.header('Reviews')
    games_with_reviews = st.session_state['Results'][~st.session_state['Results']["Sam's Review"].isna()]
    game_to_explore = st.selectbox('Pick a game to see our reviews!', games_with_reviews['Game'].unique())

    game_data = games_with_reviews[games_with_reviews['Game'] == game_to_explore].iloc[0]
    st.subheader(game_to_explore)
    st.write('Data played:', game_data['When finished'])

    consensus = (game_data["Sam's Rating"] + game_data["Gabi's Rating"])/2
    st.write(f"Consensus Rating = {consensus}")
    col1, col2 = st.columns(2)
    col1.subheader("Sam's Review")
    col1.write(f"Rating = {game_data['Sam\'s Rating']}")
    col1.write(game_data["Sam's Review"])

    col2.subheader("Gabi's Review")
    col2.write(f"Rating = {game_data['Gabi\'s Rating']}")
    col2.write(game_data["Gabi's Review"])