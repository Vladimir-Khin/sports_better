import math


def valid_odds(odds:int) -> bool:
    """ American odds must be greater than 1000 or less than -100"""
    return abs(odds) >= 100


def strategy_conditions(conditions:list, resultTrue:str, resultFalse:str) -> str:
    pass


def evaluate_bet_ml(game:dict, wager_on:str, ml_odds:int, wager:int) -> int:
    outcome = 0
    winner = ''
    if game['H_PTS'] > game['A_PTS']:
        winner = game['H_TEAM']
    else:
        winner = game['A_TEAM']
    # Bet won
    if wager_on == winner:
        # Negative odds payout
        if ml_odds < 0:
            outcome = round((100 / abs(ml_odds)) * wager,2)
        # Postive odds payout
        if ml_odds > 0:
            outcome = round((ml_odds / 100) * wager, 2)
    # Bet lost
    else:
        outcome = -wager
    return outcome


def simulate_strategy(games:dict, bet_var:str, start:int=0, wager:int=100) -> tuple:
    """TODO: Add process parameter to hold values like 'higherof', 'lowerof'
             Add weights when multiple parameters passed in"""
    money = start
    bets_won, bets_lost, bets_skipped, win_underdog, win_favorite, lose_underdog, lose_favorite= 0, 0, 0, 0, 0, 0, 0
    away_var = f'A_{bet_var}'
    home_var = f'H_{bet_var}'
    for game in games.values():
        ml_odds = 0
        wager_on = ''
        if math.isnan(game[home_var]) or math.isnan(game[away_var]) or game[home_var] == game[away_var]:
            bets_skipped += 1
            continue
        if game[home_var] > game[away_var]:
            ml_odds = game['H_TEAM_ML']
            wager_on = game['H_TEAM']
        else:
            ml_odds = game['A_TEAM_ML']
            wager_on = game['A_TEAM']
        if not valid_odds(ml_odds):
            continue
        money_return = evaluate_bet_ml(game, wager_on, ml_odds, wager)
        money = round(money + money_return, 2)
        if money_return > 0:
            bets_won += 1
            if ml_odds > 0:
                win_underdog +=1
            else:
                win_favorite +=1
        else:
            bets_lost += 1
            if ml_odds > 0:
                lose_underdog +=1
            else:
                lose_favorite +=1
    return money, bets_won, bets_lost, bets_skipped, win_underdog, win_favorite, lose_underdog, lose_favorite

