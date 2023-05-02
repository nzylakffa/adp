import streamlit as st
import pandas as pd
import requests
import time
import re
import lxml

st.header("Collect ESPN and Underdog ADP's")

def scrape_espn_adp():
    url = "https://www.fantasypros.com/nfl/adp/ppr-overall.php"
    response = requests.get(url)
    tables = pd.read_html(response.content)
    df = tables[0]
    df = df[['Player Team (Bye)', 'POS', 'ESPN']]
    df = df.rename(columns={'ESPN': 'ESPN ADP', 'Player Team (Bye)': 'Player'})
    df[['Player', 'Team']] = df['Player'].str.split('(', n=1, expand=True)
    df['Team'] = df['Team'].str.replace(')', '')
    df['Team'] = df['Team'].str.split(' ', n=1, expand=True)[0]
    df['Player'] = df['Player'].str.strip()

    # extract team name from player name if it ends with two or more capital letters
    pattern = r'\b[A-Z]{2,}\b'
    df['Team'] = df['Player'].str.extract(f'({pattern})$')
    df.loc[df['Team'].notnull(), 'Team'] = df.loc[df['Team'].notnull(), 'Team'].apply(lambda x: x.strip())
    df.loc[df['Team'].notnull(), 'Player'] = df.loc[df['Team'].notnull(), 'Player'].apply(lambda x: re.sub(f' {pattern}$', '', x).strip())

    # extract only alphabetic characters from the "POS" column
    df['POS'] = df['POS'].str.extract(r'([a-zA-Z]+)')

    df = df[['Player', 'Team', 'POS', 'ESPN ADP']]
    return df


def scrape_underdog_adp():
    url = "https://www.fantasypros.com/nfl/adp/best-ball-overall.php"
    response = requests.get(url)
    tables = pd.read_html(response.content)
    df = tables[0]
    df = df[['Player Team (Bye)', 'POS', 'Underdog']]
    df = df.rename(columns={'Underdog': 'Underdog ADP', 'Player Team (Bye)': 'Player'})
    df[['Player', 'Team']] = df['Player'].str.split('(', n=1, expand=True)
    df['Team'] = df['Team'].str.replace(')', '')
    df['Team'] = df['Team'].str.split(' ', n=1, expand=True)[0]
    df['Player'] = df['Player'].str.strip()

    # extract team name from player name if it ends with two or more capital letters
    pattern = r'\b[A-Z]{2,}\b'
    df['Team'] = df['Player'].str.extract(f'({pattern})$')
    df.loc[df['Team'].notnull(), 'Team'] = df.loc[df['Team'].notnull(), 'Team'].apply(lambda x: x.strip())
    df.loc[df['Team'].notnull(), 'Player'] = df.loc[df['Team'].notnull(), 'Player'].apply(lambda x: re.sub(f' {pattern}$', '', x).strip())

    # extract only alphabetic characters from the "POS" column
    df['POS'] = df['POS'].str.extract(r'([a-zA-Z]+)')

    df = df[['Player', 'Team', 'POS', 'Underdog ADP']]
    return df



if st.checkbox("Get ESPN and Underdog ADP's"):
    espn_adp_df = scrape_espn_adp()
    espn_adp_df['ESPN ADP'].fillna(500, inplace=True)
    espn_adp_df['Team'].fillna("FA", inplace=True)
    espn_adp_df.sort_values(by='ESPN ADP', inplace=True)
    espn_adp_df = espn_adp_df.rename(columns={'POS': 'Pos'})
    # create a new column "Underdog Pos Rank"
    espn_adp_df['ESPN Pos Rank'] = (
    espn_adp_df.groupby('Pos')['ESPN ADP']
    .rank(method='dense', ascending=True)
    .astype(int))
    espn_adp_df['ESPN Pos Rank'] = espn_adp_df['Pos'] + ' ' + espn_adp_df['ESPN Pos Rank'].astype(str)
    espn_adp_df = espn_adp_df[['Player', 'Team', 'Pos', 'ESPN Pos Rank', 'ESPN ADP']]
    
    # Scrape Underdog
    underdog_adp_df = scrape_underdog_adp()
    underdog_adp_df['Underdog ADP'].fillna(500, inplace=True)
    underdog_adp_df['Team'].fillna("FA", inplace=True)
    underdog_adp_df.sort_values(by='Underdog ADP', inplace=True)
    underdog_adp_df = underdog_adp_df.rename(columns={'POS': 'Pos'})
    # create a new column "Underdog Pos Rank"
    underdog_adp_df['Underdog Pos Rank'] = (
    underdog_adp_df.groupby('Pos')['Underdog ADP']
    .rank(method='dense', ascending=True)
    .astype(int))
    underdog_adp_df['Underdog Pos Rank'] = underdog_adp_df['Pos'] + ' ' + underdog_adp_df['Underdog Pos Rank'].astype(str)
    underdog_adp_df = underdog_adp_df[['Player', 'Team', 'Pos', 'Underdog Pos Rank', 'Underdog ADP']]
    final_df = underdog_adp_df.merge(espn_adp_df, on = ['Player', 'Team', 'Pos'], how = "left")
    all_players = st.checkbox("Keep All Players", value = True)
    if all_players == True:
        filtered = st.multiselect("Show Only Select Positions",
                                  ["QB", "RB", "WR", "TE", "DST"], ["QB", "RB", "WR", "TE"])
        final_df = final_df[final_df['Pos'].isin(filtered)]
        st.dataframe(final_df.set_index('Player'))
    else:
        final_df = underdog_adp_df.merge(espn_adp_df, on = ['Player', 'Team', 'Pos'], how = "left")
        filtered = st.multiselect("Show Only Select Positions",
                                  ["QB", "RB", "WR", "TE", "DST"], ["QB", "RB", "WR", "TE"])
        final_df = final_df[final_df['Pos'].isin(filtered)]
        players = final_df['Player']
        player = st.multiselect("Find Players", players)
        final_df = final_df[final_df['Player'].isin(player)]
        final_df = final_df[['Player', 'Team', 'Pos', 'Underdog Pos Rank', 'Underdog ADP', 'ESPN Pos Rank', 'ESPN ADP']]
        st.dataframe(final_df.set_index('Player'))

### Sidebar ###
st.sidebar.image('ffa_red.png', use_column_width=True)
st.sidebar.markdown(" ## About This App:")
st.sidebar.markdown("This app will scrape the current ADP's on ESPN and Underdog and display them as a table for you to look at! You can also download the data to use however you want!")

st.sidebar.markdown("## Steps:")
st.sidebar.markdown("1) Click the checkbox next to: Get ESPN and Underdog ADP's.")
st.sidebar.markdown("2) A table will appear with the results from the scraper!")
st.sidebar.markdown("3) Keep the checkbox 'Keep All Players' checked if you want all players for the filtered positions to display.")
st.sidebar.markdown("4) If you want to show only specific players, uncheck that box and type those players names into the search bar that appears.")




# select all option
# if not all, you can type names in and see those names
