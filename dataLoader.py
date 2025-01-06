import pandas as pd 
import numpy as np
import streamlit as st
#from shillelagh.backends.apsw.db import connect
import gspread

#@st.cache_data(ttl = 600)
#def runQuery(sheets_link):

#    connection = connect(":memory:", adapters = 'gsheetsapi')
#    cursor = connection.cursor()
    
#    query = f'SELECT * FROM "{sheets_link}"'

#    query_results = []
#    for row in cursor.execute(query):
#        query_results.append(row)
#    return query_results


@st.cache_data(ttl = 600)
def runQuery(api_key, sheets_key, sheet_name = 'Sheet1', expected_headers = ['Game', 'When started']):
    gc = gspread.api_key(api_key)
    sh = gc.open_by_key(sheets_key)
    results = pd.DataFrame(sh.worksheet(sheet_name).get_all_records(expected_headers = expected_headers))
    return results

def loadData_results(year):
    #sheets_query = runQuery(st.secrets['results_url'])
    if year != '2025':
        sheet_name = f'{year}_BGA_Journey [Archived]'
    else:
        sheet_name = f'{year}_BGA_Journey'
    results = runQuery(st.secrets['api_key'], st.secrets['results_key'], sheet_name = sheet_name)
    #only grab entries related to games
    for i, val in enumerate(results['Game'] == ''):
        if val:
            game_end = i
            break
    results = results.iloc[:game_end]
    results = results.astype({'When finished': 'datetime64[ns]', 'When started': 'datetime64[ns]'})
    #results = results.dropna(subset = 'Are they the same')
    return results
 

