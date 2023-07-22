import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import re
import seaborn as sns

st.header("Collect ADP's")

cm = sns.diverging_palette(145, 20, center="dark", as_cmap=True)

def scrape_espn_adp():
    url_2 = "https://www.fantasypros.com/nfl/adp/ppr-overall.php"
    response_2 = requests.get(url_2)
    tables = pd.read_html(response_2.content)
    df_2 = tables[0]
    df_2["Player"] = df_2["Player Team (Bye)"].str.split(" ").str[:2].str.join(" ")
    df_2 = df_2.rename(columns={'POS': 'Pos'})
    # Drop the numbers from Pos
    df_2['Pos'] = df_2['Pos'].str.replace('\d+', '')
    df_2 = df_2[["Player", "Pos", "Sleeper"]]
    # Replace None with 250
    df_2 = df_2.fillna(250)
    st.dataframe(df_2)
    
    url = "https://www.4for4.com/adp"
    response = requests.get(url)
    tables = pd.read_html(response.content)
    df = tables[0]
    df = df[['Player', 'Team', 'Position', 'ESPN', 'Y!', 'NFL', 'Underdog']]
    df[['Pos', 'Pos Rank']] = df['Position'].str.split('-', n=1, expand=True)
    # Keep just these columns
    df = df[['Player', 'Team', 'Pos', 'ESPN', 'Y!', 'NFL', 'Underdog']]
    # Rename
    df = df.rename(columns={'Y!': 'Yahoo'})
    # Replace all "-" with 500
    df['ESPN'] = df['ESPN'].replace('-', 250, regex=True).astype(int)
    df['Yahoo'] = df['Yahoo'].replace('-', 250, regex=True).astype(int)
    df['NFL'] = df['NFL'].replace('-', 250, regex=True).astype(int)
    df['Underdog'] = df['Underdog'].replace('-', 250, regex=True).astype(int)
    # If an ADP is > 250, make it 250
    df['ESPN'] = np.where(df['ESPN']>250,250,df['ESPN'])
    df['Yahoo'] = np.where(df['Yahoo']>250,250,df['Yahoo'])
    df['NFL'] = np.where(df['NFL']>250,250,df['NFL'])
    df['Underdog'] = np.where(df['Underdog']>250,250,df['Underdog'])   
    # Make columns numeric
    df['ESPN'] = pd.to_numeric(df['ESPN'])
    df['Yahoo'] = pd.to_numeric(df['Yahoo'])
    df['NFL'] = pd.to_numeric(df['NFL'])
    df['Underdog'] = pd.to_numeric(df['Underdog'])
    # Fill na team with FA
    df['Team'].fillna("FA", inplace=True)
    df['Team'] = df['Team'].replace('-', "FA", regex=True)
    st.dataframe(df)
    # Merge
    df = df.merge(df_2, on = ['Player', 'Pos'])
    df['Sleeper'] = pd.to_numeric(df['Sleeper'])
    # Create Average ADP Column
    df['Average ADP'] = (df['ESPN'] + df['Yahoo'] + df['NFL'] + df['Underdog'] + df['Sleeper'])/5
    # Sort by Average ADP
    df.sort_values(by='Average ADP', inplace=True)
    st.dataframe(df)
    # Best ADP
    df['Best ADP Site'] = np.where((df['ESPN'] >= df['Yahoo']) & (df['ESPN'] >= df['NFL']) & (df['ESPN'] >= df['Underdog']) & (df['ESPN'] >= df['Sleeper']), "ESPN",
                                  (np.where((df['Yahoo'] >= df['ESPN']) & (df['Yahoo'] >= df['NFL']) & (df['Yahoo'] >= df['Underdog']) & (df['Yahoo'] >= df['Sleeper']),'Yahoo',
                                           (np.where((df['NFL'] >= df['ESPN']) & (df['NFL'] >= df['Yahoo']) & (df['NFL'] >= df['Underdog']) & (df['NFL'] >= df['Sleeper']),'NFL',
                                                     (np.where((df['Sleeper'] >= df['ESPN']) & (df['Sleeper'] >= df['Yahoo']) & (df['Sleeper'] >= df['NFL']) & (df['Sleeper'] >= df['Underdog']),'Sleeper', 'Underdog')))))))
    
    
    
    # Worst ADP
    df['Worst ADP Site'] = np.where((df['ESPN'] <= df['Yahoo']) & (df['ESPN'] <= df['NFL']) & (df['ESPN'] <= df['Underdog']) & (df['ESPN'] <= df['Sleeper']), "ESPN",
                                  (np.where((df['Yahoo'] <= df['ESPN']) & (df['Yahoo'] <= df['NFL']) & (df['Yahoo'] <= df['Underdog']) & (df['Yahoo'] <= df['Sleeper']),'Yahoo',
                                           (np.where((df['NFL'] <= df['ESPN']) & (df['NFL'] <= df['Yahoo']) & (df['NFL'] <= df['Underdog']) & (df['NFL'] <= df['Sleeper']),'NFL',
                                                     (np.where((df['Sleeper'] <= df['ESPN']) & (df['Sleeper'] <= df['Yahoo']) & (df['Sleeper'] <= df['NFL']) & (df['Sleeper'] <= df['Underdog']),'Sleeper', 'Underdog')))))))
    
    # Reset Index
    df = df.reset_index(drop=True)
    return df

def highlight_rows(row):
    value = row.loc['Pos']
    if value == 'QB':
        color = '#FFB3BA' # Red
    elif value == 'RB':
        color = '#BAFFC9' # Green
    elif value == 'TE':
        color = '#CF9FFF'  # Purple
    else:
        color = '#BAE1FF' # Blue
    return ['background-color: {}'.format(color) for r in row]

if st.checkbox("Get ADP's"):
    adp_df = scrape_espn_adp()
    all_players = st.checkbox("Keep All Players", value = True)
    if all_players == True:
        filtered = st.multiselect("Show Only Select Positions",
                                  ["QB", "RB", "WR", "TE", "DST"], ["QB", "RB", "WR", "TE"])
        adp_df = adp_df[adp_df['Pos'].isin(filtered)]
        best_values = st.multiselect("Best Values by Site",
                                    ["ESPN", "Yahoo", "NFL", "Underdog", "Sleeper"], ["ESPN", "Yahoo", "NFL", "Underdog", "Sleeper"])
        adp_df = adp_df[adp_df['Best ADP Site'].isin(best_values)]
        worst_values = st.multiselect("Worst Values by Site",
                                    ["ESPN", "Yahoo", "NFL", "Underdog", "Sleeper"], ["ESPN", "Yahoo", "NFL", "Underdog", "Sleeper"])
        adp_df = adp_df[adp_df['Worst ADP Site'].isin(worst_values)]
        adp_df['Average ADP'] = round(adp_df['Average ADP'],2)
        adp_df['Sleeper'] = round(adp_df['Sleeper'],2)
        st.dataframe(adp_df.style.text_gradient(cmap=cm).format({'Average ADP':'{:.1f}',
                                                                'Sleeper':'{:.0f}'}).apply(highlight_rows, axis=1))
    else:
        filtered = st.multiselect("Show Only Select Positions",
                                  ["QB", "RB", "WR", "TE", "DST"], ["QB", "RB", "WR", "TE"])
        adp_df = adp_df[adp_df['Pos'].isin(filtered)]
        players = adp_df['Player']
        player = st.multiselect("Find Players", players)
        adp_df = adp_df[adp_df['Player'].isin(player)]
        st.dataframe(adp_df.style.text_gradient(cmap=cm).format({'Average ADP':'{:.1f}',
                                                                'Sleeper': '{:.0f}'}).apply(highlight_rows, axis=1))
        

### Sidebar ###
st.sidebar.image('ffa_red.png', use_column_width=True)
st.sidebar.markdown(" ## About This App:")
st.sidebar.markdown("This app will scrape the current indusrty ADP's and display them in ways where you can evaluate who the best picks are on each site!")

st.sidebar.markdown("## Steps:")
st.sidebar.markdown("1) Click the checkbox next to: Get ADP's.")
st.sidebar.markdown("2) A table will appear with the results from the scraper!")
st.sidebar.markdown("3) Keep the checkbox 'Keep All Players' checked if you want all players for the filtered positions to display.")
st.sidebar.markdown("4) If you want to show only specific players, uncheck that box and type those players names into the search bar that appears.")
st.sidebar.markdown("5) If you want to see only the best values for a specific site, then X out all the other sites under the 'Best Values by Site' section.")