import csv
import pandas as pd
from datetime import datetime
from typing import Callable
from collections import OrderedDict

from helpers import grouper
 

def gl_initial_load(gl_file:str):
    """Perform initial cleanup of data from nba.com
    TODO: Make call using nba_abi instead of saving file locally"""
    df = pd.read_csv(gl_file)
    # Rename some columns
    df = df.rename(columns={'W/L': 'WL', 'FG%': 'FG_PCT', '3P%': '3P_PCT', 
                            'FT%': 'FT_PCT', '+/-': 'PLUS_MINUS', 'MATCH UP': 'MATCH_UP', 
                            'GAME DATE': 'DATE'})

    # VH indictor based on MATCH_UP string
    df['VH_IND'] = df['MATCH_UP'].apply(lambda x: 'V' if '@' in x else 'H')    
    # Convert to standardized MATCH_UP string
    df['MATCH_UP'] = df['MATCH_UP'].apply(lambda x: f'{x[-3:]}_{x[0:3]}' if '@' in x else f'{x[0:3]}_{x[-3:]}')
    # Convert to datetime column
    df['DATE'] = pd.to_datetime(df['DATE'], format='%m/%d/%Y')
    # Sort the dataframe
    df = df.sort_values(by=['DATE', 'MATCH_UP', 'VH_IND']).reset_index(drop=True)
    return df


def gl_add_rolling_agg_col(
    df: pd.DataFrame, col:str, np_agg:Callable, 
    window:int, window_min:int
    ) -> pd.Series:
    """Returns series with aggregating function applied on rolling windows of team.

    Incoming df must be sorted by team and date to accurately aggregate
    
    Valid numpy function examples: np.mean, np.sum, np.min, np.max"""
    if 'TEAM' not in df.columns:
        return None    
    return df.groupby('TEAM')[col].apply(lambda x: x.rolling(window, window_min).apply(np_agg).shift())


def gl_new_col_prefix(np_agg:Callable, window:int, window_min:int):
    return f'IN_{np_agg.__name__.upper()}_{window}_{window_min}_'


def gl_add_rolling_agg_cols(
    df: pd.DataFrame, np_agg:Callable, 
    window:int, window_min:int
    ) -> pd.DataFrame:
    """Runs aggregation function on every column of dataframe based on 'window' previous games"""
    if 'TEAM' not in df.columns:
        return df
    df_new = df.groupby('TEAM')[df.columns[(df.dtypes == 'int64') | (df.dtypes == 'float64')]]
    df_new = df_new.apply(lambda x: round(x.rolling(window, window_min).apply(np_agg),4).shift())
    df_new = df_new.add_prefix(gl_new_col_prefix(np_agg, window, window_min))
    return df_new


def gl_add_custom_feature() -> pd.DataFrame:
    """TODO"""
    pass


def gl_add_incoming_wins(df: pd.DataFrame) -> None:
    df['IN_WIN'] = df.groupby('TEAM')['WL'].apply(lambda x: (x == 'W').cumsum().shift())
    return None


def gl_convert_to_game_rows(g_list: list) -> OrderedDict:
    """Reshapes games data so each row represents one game"""
    games, game = OrderedDict(), dict()
    for row in grouper(g_list, n = 2):
        game['SEASON_TYPE'] = row[0]['SEASON_TYPE']
        game['DATE'] = row[0]['DATE']
        game['MATCH_UP'] = f"{row[0]['DATE'].strftime('%m%d%Y')}_{row[0]['MATCH_UP']}"

        for idx, team in enumerate(row):
            for key, val in team.items():
                if key in ('VH_IND', 'SEASON_TYPE', 'DATE', 'MATCH_UP'):
                    continue
                if idx == 0:
                    game[f'H_{key}'] = val
                else:
                    game[f'A_{key}'] = val
        # Add game to games
        games[game['MATCH_UP']] = game.copy()
    return games


def o_add_year(day_month:str, year:str) -> str:
    """Identifies year for the game of season for odds dataset
    #### TODO: Make more stable than the logic currently used
    """
    if int(day_month) < 1000:
        return f'0{day_month[0:1]}/{day_month[1:3]}/{str(int(year)+1)}'
    else:
        return f'{day_month[0:2]}/{day_month[2:4]}/{str(year)}'


def o_load_data(o_file:str) -> dict:
    """Reshapes odds data so each row represents 1 game
    #### TODO: Update year to use os path library later
    """
    team_city_acr = {'Atlanta': 'ATL', 'Boston': 'BOS', 'Brooklyn': 'BKN', 'Charlotte': 'CHA', 
                'Chicago': 'CHI', 'Cleveland': 'CLE', 'Dallas': 'DAL', 'Denver': 'DEN', 
                'Detroit': 'DET', 'GoldenState': 'GSW', 'Houston': 'HOU', 'Indiana': 'IND', 
                'LAClippers': 'LAC', 'LALakers': 'LAL', 'Memphis': 'MEM', 'Miami': 'MIA', 
                'Milwaukee': 'MIL', 'Minnesota': 'MIN', 'NewOrleans': 'NOP', 'NewYork': 'NYK', 
                'OklahomaCity': 'OKC', 'Orlando': 'ORL', 'Philadelphia': 'PHI', 'Phoenix': 'PHX', 
                'Portland': 'POR', 'Sacramento': 'SAC', 'SanAntonio': 'SAS', 'Toronto': 'TOR', 
                'Utah': 'UTA', 'Washington': 'WAS'}
    odds = dict()
    with open(o_file, 'r') as f:
        year = o_file[9:13]
        rows = csv.DictReader(f)
        # Original: 2 rows represent 1 game -> New: 1 row represents 1 game
        game = dict()
        for row in grouper(rows, n = 2):
            game['DATE'] = datetime.strptime(o_add_year(row[0]['Date'], year), '%m/%d/%Y')
            game['A_TEAM'] = team_city_acr[row[0]['Team']]
            game['A_TEAM_ML'] = int(row[0]['ML'])
            game['H_TEAM'] = team_city_acr[row[1]['Team']]
            game['H_TEAM_ML'] = int(row[1]['ML'])
            game['MATCH_UP'] = f"{game['DATE'].strftime('%m%d%Y')}_{game['H_TEAM']}_{game['A_TEAM']}"
            odds[game['MATCH_UP']] = game.copy()
    return odds


def gl_add_moneyline(games:dict, odds:dict) -> None:
    """Pulls ML odds from odds dictionary into games dictionary"""
    for key, game in games.items():
        game['H_TEAM_ML'] = odds[key]['H_TEAM_ML']
        game['A_TEAM_ML'] = odds[key]['A_TEAM_ML']
    return None


def load_simulation_data(gl_file:str, o_file:str, np_agg:Callable, window:int, window_min:int) -> dict:
    df = gl_initial_load(gl_file)

    # Sort to get everything grouped by team
    df = df.sort_values(by=['TEAM','DATE']) 

    # Add new columns with aggregating function
    df_new = gl_add_rolling_agg_cols(df=df, np_agg=np_agg, window=window, window_min=window_min)
    df = pd.concat([df, df_new], axis=1)

    # Add in cumulative wins for the season for each group
    gl_add_incoming_wins(df)
    df = df.sort_index()

    # Convert df to list of dictionaries and convert to games
    g_list = df.to_dict('records')
    games = gl_convert_to_game_rows(g_list)

    # Load odds dataset and add moneylines to games dictionary
    odds = o_load_data(o_file)
    gl_add_moneyline(games, odds)
    return games
    
