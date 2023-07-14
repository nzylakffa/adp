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
    url = "https://www.4for4.com/adp"
    response = requests.get(url)
    tables = pd.read_html(response.content)
    df = tables[0]
    df = df[['Player', 'Team', 'Position', 'ESPN', 'Y!']]
    df[['Pos', 'Pos Rank']] = df['Position'].str.split('-', n=1, expand=True)
    # Keep just these columns
    df = df[['Player', 'Team', 'Pos', 'ESPN', 'Y!']]
    # Rename
    df = df.rename(columns={'Y!': 'Yahoo'})
    # Replace all "-" with 500
    df['ESPN'] = df['ESPN'].replace('-', 250, regex=True).astype(int)
    df['Yahoo'] = df['Yahoo'].replace('-', 250, regex=True).astype(int)
    # If an ADP is > 250, make it 250
    df['ESPN'] = np.where(df['ESPN']>250,250,df['ESPN'])
    df['Yahoo'] = np.where(df['Yahoo']>250,250,df['Yahoo'])
    # Make columns numeric
    df['ESPN'] = pd.to_numeric(df['ESPN'])
    df['Yahoo'] = pd.to_numeric(df['Yahoo'])
    # Fill na team with FA
    df['Team'].fillna("FA", inplace=True)
    df['Team'] = df['Team'].replace('-', "FA", regex=True)
    # Create Average ADP Column
    df['Average ADP'] = (df['ESPN'] + df['Yahoo'])/2
    # Sort by Average ADP
    df.sort_values(by='Average ADP', inplace=True)
    # Best ADP
    df['Best ADP Site'] = np.where(df['ESPN'] > df['Yahoo'], "ESPN", "Yahoo")
    # Worst ADP
    df['Worst ADP Site'] = np.where(df['ESPN'] < df['Yahoo'], "ESPN", "Yahoo")
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
                                    ["ESPN", "Yahoo"], ["ESPN", "Yahoo"])
        adp_df = adp_df[adp_df['Best ADP Site'].isin(best_values)]
        worst_values = st.multiselect("Worst Values by Site",
                                    ["ESPN", "Yahoo"], ["ESPN", "Yahoo"])
        adp_df = adp_df[adp_df['Worst ADP Site'].isin(worst_values)]
        adp_df['Average ADP'] = round(adp_df['Average ADP'],2)
        st.dataframe(adp_df.style.text_gradient(cmap=cm).format({'Average ADP':'{:.1f}'}).apply(highlight_rows, axis=1))
    else:
        filtered = st.multiselect("Show Only Select Positions",
                                  ["QB", "RB", "WR", "TE", "DST"], ["QB", "RB", "WR", "TE"])
        adp_df = adp_df[adp_df['Pos'].isin(filtered)]
        players = adp_df['Player']
        player = st.multiselect("Find Players", players)
        adp_df = adp_df[adp_df['Player'].isin(player)]
        st.dataframe(adp_df.style.text_gradient(cmap=cm).format({'Average ADP':'{:.1f}'}).apply(highlight_rows, axis=1))
        

### Sidebar ###
st.sidebar.image('ffa_red.png', use_column_width=True)
st.sidebar.markdown(" ## About This App:")
st.sidebar.markdown("This app will scrape the current indusrty ADP's and display them in ways where you can evaluate who the best picks are on each site!")

st.sidebar.markdown("## Note:")
st.sidebar.markdown("My goal is to have Sleeper, CBS and NFL all on this table as well. Just going to take some time to get the data for those running properly. I'm also going to record a video soon going over how to best use this app. I'll post that as a link here when I have that done. I'll probably wait until I finish getting the ADP data from the other sites though.")

st.sidebar.markdown("## Steps:")
st.sidebar.markdown("1) Click the checkbox next to: Get ADP's.")
st.sidebar.markdown("2) A table will appear with the results from the scraper!")
st.sidebar.markdown("3) Keep the checkbox 'Keep All Players' checked if you want all players for the filtered positions to display.")
st.sidebar.markdown("4) If you want to show only specific players, uncheck that box and type those players names into the search bar that appears.")
st.sidebar.markdown("5) If you want to see only the best values for a specific site, then X out all the other sites under the 'Best Values by Site' section.")
