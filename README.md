# sports_better
Simulate a betting strategy on each game of a given sports season and calculate a return for the strategy.

Current scope of the application
NBA
- Type of bet to simulate
	- Moneyline
- Seasons
	- 2017/18, 2018/19
- Feature engineering
	- Create team "incoming" game features built from an aggregating function like np.mean, np.median, np.sum, etc...
		- Example: np.mean of previous 10 games (window) with a minimum of 2 games (window_min)
- Bet Strategy
	- Higher of: Bet on team with higher value in a feature
		

NBA Datasets used
- https://www.sportsbookreviewsonline.com/scoresoddsarchives/nba/nbaoddsarchives.htm
	- Moneylines for each game
- https://nba.com
	- Team statistics for each game


Future
	- Add more NBA seasons
	- Add differential features
	- Add capabilities to have user pass in multiple conditions for a strategy
	
	