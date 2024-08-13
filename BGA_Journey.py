import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from dataLoader import loadData_results

import requests
import bs4 as bs


import streamlit as st
import hydralit_components as hc
st.set_page_config(layout='wide')

def get_thumbnail(game):
    """
    Use BGG api to extract the thumbnail for a game
    """
    game = game.replace(' ', '%20')
    url = f'https://boardgamegeek.com/xmlapi2/search?query={game}&type=boardgame&exact=1'

    response = requests.get(url)
    soup = bs.BeautifulSoup(response.text, 'xml')

    game = soup.find_all('items')[0]
    info = []
    game_id = None
    for child in game.children:
        if child != '\n' and child != ' ':
            game_id = child.attrs['id']

    #if game is found, extract the thumbnail
    if game_id is not None:
        url = f"https://boardgamegeek.com/xmlapi/boardgame/{game_id}?stats=1"
        response = requests.get(url)
        soup = bs.BeautifulSoup(response.text, 'xml')
        #extract game info from xml
        game_info = soup.find_all('boardgame')

        #extract the thumbnail
        link = game_info[0].find('thumbnail').text
        im = Image.open(requests.get(link, stream=True).raw)
        return im
    else:
        return None
    
@st.cache_data(ttl=300)
def calculateCumulative(column = 'Who Won'):
    #get number of wins
    plot_data = st.session_state['Results'].copy()
    
    plot_data['value'] = 1
    plot_data = plot_data.groupby([column, 'When finished'])['value'].sum().reset_index()
    plot_data = plot_data.pivot(columns = column, index = 'When finished', values = 'value')
    plot_data = plot_data.replace(np.nan, 0)
    plot_data = plot_data.cumsum()
    plot_data = plot_data[['Sam', 'Gabi']]
    return plot_data

@st.cache_data(ttl=300)
def plotCumulative(figsize = (10,3)):

    #get number of wins and games chosen
    win_data = calculateCumulative(column = 'Who Won')
    chose_data = calculateCumulative(column = 'Who Chose')

        
    fig, ax = plt.subplots(figsize = figsize, nrows = 2, sharex = True, sharey=True)
    fig.subplots_adjust(hspace = 0)
    ax[0].plot(win_data.index.values, win_data['Sam'].values, label = 'Sam', c = 'red')
    ax[0].plot(win_data.index.values, win_data['Gabi'].values, label = 'Gabi', c = 'blue')
    ax[0].tick_params(axis = 'x', rotation = 45)
    ax[0].set_ylabel('Games Won')
    ax[0].set_xlim(win_data.index.values[0], win_data.index.values[-1])
    ax[1].plot(chose_data.index.values, chose_data['Sam'].values, label = 'Sam', c = 'red')
    ax[1].plot(chose_data.index.values, chose_data['Gabi'].values, label = 'Gabi', c = 'blue') 
    ax[0].legend(bbox_to_anchor = (0.55, 1.08), ncol = 2)
    ax[1].set_ylabel('Games Chosen')
    ax[1].tick_params(axis = 'x', rotation = 45)
    return fig

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

    #st.header('Games played each month')

    results = st.session_state['Results'].dropna(subset = 'When finished').copy()
    results['When finished'] = pd.to_datetime(results['When finished'])
    results['Month of Play'] = results['When finished'].dt.month
    month_dict = {1: 'January', 2: 'February', 3: 'March', 4:'April',5:'May',6:'June',7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
    results = results.sort_values('Month of Play')
    results['Month of Play'] = results['Month of Play'].map(month_dict)
    num_per_month = results.groupby('Month of Play').size()
    #reorder
    month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    num_per_month = num_per_month.loc[[m for m in month if m in num_per_month.index]]

    fig, ax = plt.subplots(figsize = (10, 2.5))
    ax.bar(num_per_month.index, num_per_month.values, color = 'gray', edgecolor = 'black', width = 1)
    ax.tick_params(axis = 'x', rotation = 0)
    ax.set_ylabel('Number of\nGames Played')
    ax.set_title('Games Played Each Month')

    #annotate each bar with the games played 
    for i, v in enumerate(num_per_month.index):
        #grab the games played that month
        games_played = results[results['Month of Play'] == v].sort_values('When finished')['Game'].values
        for j, game in enumerate(games_played):
            ax.text(i, num_per_month.values[i] - j-0.1, game, ha = 'center', va = 'top', fontsize = 5)
    ax.set_xlim(-0.5, num_per_month.shape[0]-0.5)
    st.pyplot(fig)

    #add cumulative wins
    fig = plotCumulative(figsize = (10,3))
    st.pyplot(fig)


    #st.bar_chart(num_per_month)
    #st.write(f"Here's what we are playing now: {playing}")


    st.header(f"Our Most Recent Game = {finished['Game']}")
    playing = ';'.join(st.session_state['Results'][st.session_state['Results']['When finished'].isna()]['Game'].values)
    col1, col2, col3 = st.columns(3)

    #get the game id from boardgamegeek to extract the thumbnail
    if 'thumbnail' not in st.session_state:
        st.session_state['thumbnail'] = get_thumbnail(finished['Game'])
    #col1.subheader(f"{finished['Game']}")
    if st.session_state['thumbnail'] is not None:
        col1.image(st.session_state['thumbnail'])
    else:
        col1.write("No Thumbnail Found,\ncheck name to make sure it matches BGG")
    col1.write(f"{finished['Who Won']} Won!")
    col2.subheader("Sam's Review")
    col2.write("Rating = "+ str(finished["Sam's Rating"]))
    col2.write(finished["Sam's Review"])
    col3.subheader("Gabi's Review")
    col3.write("Rating = " + str(finished["Gabi's Rating"]))
    col3.write(finished["Gabi's Review"])

    


if menu == 'Ratings':
    ratings = st.session_state['Results'][['Game', "Sam's Rating", "Gabi's Rating"]].set_index('Game')
    reviews = st.session_state['Results'][['Game', "Sam's Review", "Gabi's Review"]].set_index('Game')
    st.header('Ratings and Reviews')

    ratings_zscored = (ratings - ratings.mean())/ratings.std()
    ratings['Consensus'] = ratings.mean(axis = 1)
    ratings['Consensus Z-Score'] = ratings_zscored.mean(axis = 1)

    sorting_ratings = ratings['Consensus Z-Score'].sort_values(ascending = False)
    ranked_list = ''
    current_rank = 1
    unique_ratings = sorting_ratings.unique()
    for rank, rating in zip(range(1,len(unique_ratings)), unique_ratings):
        games_with_rating = sorting_ratings[sorting_ratings == rating].index.values
        if len(games_with_rating) == 1:
            ranked_list = ranked_list + f'{rank}. ({round(rating,2)}) {games_with_rating[0]}\n'
        else:
            for i, game in enumerate(games_with_rating):
                #st.write(games_with_rating)
                if i == 0:
                    #ranked_list = ranked_list + f'{rank}. {game} ({round(rating,2)}), \n'
                    ranked_list = ranked_list + f'{rank}. ({round(rating,2)}) {game}'
                elif i == len(games_with_rating) - 1:
                    ranked_list = ranked_list + f', and {game}\n'
                else:
                    num_spaces = (3 if i < 10 else 4)
                    ranked_list = ranked_list + f', {game}'
            #ranked_list = ranked_list + f'{rank}. {game} ({round(sorting_ratings.loc[game],2)})\n'
            #prev_rating = sorting_ratings.loc[game]

    #games ranked list
    col1, col2, col3 = st.columns(3)
    col1.subheader('Consensus Ratings')
    col1.write(ranked_list)

    sorting_ratings = ratings["Sam's Rating"].sort_values(ascending = False)
    ranked_list = ''
    current_rank = 1
    unique_ratings = sorting_ratings.unique()
    for rank, rating in zip(range(1,len(unique_ratings)), unique_ratings):
        games_with_rating = sorting_ratings[sorting_ratings == rating].index.values
        if len(games_with_rating) == 1:
            ranked_list = ranked_list + f'{rank}. ({round(rating,2)}) {games_with_rating[0]}\n'
        else:
            for i, game in enumerate(games_with_rating):
                #st.write(games_with_rating)
                if i == 0:
                    #ranked_list = ranked_list + f'{rank}. {game} ({round(rating,2)}), \n'
                    ranked_list = ranked_list + f'{rank}. ({round(rating,2)}) {game}'
                elif i == len(games_with_rating) - 1:
                    ranked_list = ranked_list + f', and {game}\n'
                else:
                    num_spaces = (3 if i < 10 else 4)
                    ranked_list = ranked_list + f', {game}'

    col2.subheader("Sam's Ratings")
    col2.write(ranked_list)

    sorting_ratings = ratings["Gabi's Rating"].sort_values(ascending = False)
    ranked_list = ''
    current_rank = 1
    unique_ratings = sorting_ratings.unique()
    for rank, rating in zip(range(1,len(unique_ratings)), unique_ratings):
        games_with_rating = sorting_ratings[sorting_ratings == rating].index.values
        if len(games_with_rating) == 1:
            ranked_list = ranked_list + f'{rank}. ({round(rating,2)}) {games_with_rating[0]}\n'
        else:
            for i, game in enumerate(games_with_rating):
                #st.write(games_with_rating)
                if i == 0:
                    #ranked_list = ranked_list + f'{rank}. {game} ({round(rating,2)}), \n'
                    ranked_list = ranked_list + f'{rank}. ({round(rating,2)}) {game}'
                elif i == len(games_with_rating) - 1:
                    ranked_list = ranked_list + f', and {game}\n'
                else:
                    num_spaces = (3 if i < 10 else 4)
                    ranked_list = ranked_list + f', {game}'
    
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
    col1.write(f"Rating = " + str(game_data["Sam's Rating"]))
    col1.write(game_data["Sam's Review"])

    col2.subheader("Gabi's Review")
    col2.write(f"Rating = " + str(game_data["Gabi's Rating"]))
    col2.write(game_data["Gabi's Review"])
