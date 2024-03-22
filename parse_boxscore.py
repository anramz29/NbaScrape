import os 

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime


def parse_html(box_score):
    with open(box_score) as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    [s.decompose() for s in soup.select("tr.over_header")]
    [s.decompose() for s in soup.select("tr.thead")]
    return soup

def get_line_score(soup):
    df = pd.read_html(str(soup), attrs={'id': 'line_score'})[0]
    col_list = list(df.columns)
    col_list[0] = "team"
    col_list[-1] = "score"
    df.columns = col_list
    return df[["team","score"]]

def get_stats(soup, team, stat):
    df = pd.read_html(str(soup), attrs={"id":f"box-{team}-game-{stat}"})[0]
    # df["MP"] = df["MP"].apply(lambda x: x.split(":")[0])
    # df.iloc[:, 1:] = df.iloc[:, 1:].apply(lambda x: pd.to_numeric(x, errors="coerce"))
    # df = df.dropna(subset=df.columns[1])
    return df

def read_season(soup):
    nav = soup.select("#bottom_nav_container")[0]
    hrefs = [a["href"] for a in nav.find_all("a")]
    season = os.path.basename(hrefs[1]).split("_")[0]
    return season

def get_date(box_score):
    date = os.path.basename(box_score)[:8]
    date = pd.to_datetime(date, format="%Y%m%d")
    return date

def parse_box_score(box_score):

    soup = parse_html(box_score)
    
    line_score = get_line_score(soup)
    teams = list(line_score["team"])

    team_totals = []
    player_totals = []

    for team in teams:
        basic = get_stats(soup, team, "basic")
        advanced = get_stats(soup, team, "advanced")

        # Concatenate the last row of basic and advanced stats for team totals
        summaries_per_game_df = pd.concat([basic.iloc[-1:], advanced.iloc[-1:]], axis=1)
        # Concatenate all but the last row for player stats
        players_per_game_df = pd.concat([basic.iloc[:-1], advanced.iloc[:-1]], axis=1)

        # Assign team name to each player
        players_per_game_df["team"] = team


        # Append the DataFrames to the respective lists
        team_totals.append(summaries_per_game_df)
        player_totals.append(players_per_game_df)

    try:
        summary = pd.concat([x.reset_index(drop=True) for x in team_totals], ignore_index=True)
        # Set a unique index with offset for each team
        for i, team_df in enumerate(team_totals):
            offset = i * len(team_df)  # Offset based on team index and DataFrame length
            summary.iloc[offset:offset + len(team_df)].index = range(offset, offset + len(team_df))

            player_stats = pd.concat(player_totals, axis=0, ignore_index=True)

            # Add season and date information
            summary["season"] = read_season(soup)
            player_stats["season"] = read_season(soup)
            summary["date"] = get_date(box_score)
            player_stats["date"] = get_date(box_score)

    except pd.errors.InvalidIndexError as e:
        print(f"Error processing box score: {box_score}")
        print(e)
        return None, None  # Return None to indicate failure

    




    return summary, player_stats