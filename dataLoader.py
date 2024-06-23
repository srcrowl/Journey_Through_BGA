import pandas as pd 
import numpy as np
import streamlit as st
from shillelagh.backends.apsw.db import connect

@st.cache_data(ttl = 600)
def runQuery(sheets_link):

    connection = connect(":memory:", adapters = 'gsheetsapi')
    cursor = connection.cursor()
    
    query = f'SELECT * FROM "{sheets_link}"'

    query_results = []
    for row in cursor.execute(query):
        query_results.append(row)
    return query_results

def loadData_results():
    sheets_query = runQuery(st.secrets['results_url'])
    results = pd.DataFrame(sheets_query, columns = ['Game', 'When started', 'When finished', 'Type of Game', "Sam's Rating", "Sam's Review", "Gabi's Rating", "Gabi's Review", 'Who Won', 'Who Chose', 'Are they the same', 'Variants'])
    results = results.dropna(subset = 'Are they the same')
    return results
 

