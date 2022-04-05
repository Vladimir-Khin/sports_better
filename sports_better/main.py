import numpy as np
import pandas as pd
from features import load_simulation_data, gl_new_col_prefix
from simulate import simulate_strategy


def main():
    # TODO allow command line argument for which nba season to use.
    gl_file = 'nba_data/2018_19_game_logs.csv'
    o_file = 'nba_data/2018_19_game_odds.csv'
    np_agg = np.mean
    window = 10
    window_min = 2
    wager = 100
    bet_vars = ['PTS', 'FGM', 'FGA', 'FG_PCT', '3PM', '3PA', '3P_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 
                'TOV', 'STL', 'BLK', 'IN_WIN']

    games = load_simulation_data(gl_file, o_file, np_agg, window, window_min)
    results = []
    for bet_var in bet_vars:
        if bet_var == 'IN_WIN':
            pass
        else:
            bet_var = f'{gl_new_col_prefix(np_agg, window, window_min)}{bet_var}'
        simulation_result, bets_won, bets_lost, bets_skipped, win_underdog, win_favorite, lose_underdog, lose_favorite = simulate_strategy(games, bet_var, wager=wager)
        results.append([bet_var, simulation_result, bets_won, bets_lost, bets_skipped, win_underdog, win_favorite, lose_underdog, lose_favorite])

    results_df = pd.DataFrame(results, columns=['BET VAR', 'RETURN', 'BETS WON', 'BETS LOST', 'BETS SKIPPED', 'WIN UNDERDOGS', 'WIN FAVORITE', 'LOSE UNDERDOGS', 'LOSE FAVORITE'])
    print(results_df.sort_values(by='RETURN', ascending=False))

if __name__ == '__main__':
    main()