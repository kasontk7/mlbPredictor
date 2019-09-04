import os
from pathlib import Path

fangraph_path = Path("/Users/kasonkang/Downloads/FanGraphs Leaderboard (4).csv")
if fangraph_path.exists():
	os.rename("/Users/kasonkang/Downloads/FanGraphs Leaderboard.csv", "/Users/kasonkang/Documents/Projects/MLBpred/leftops.csv")
	os.rename("/Users/kasonkang/Downloads/FanGraphs Leaderboard (1).csv", "/Users/kasonkang/Documents/Projects/MLBpred/rightops.csv")
	os.rename("/Users/kasonkang/Downloads/FanGraphs Leaderboard (2).csv", "/Users/kasonkang/Documents/Projects/MLBpred/relief.csv")
	os.rename("/Users/kasonkang/Downloads/FanGraphs Leaderboard (3).csv", "/Users/kasonkang/Documents/Projects/MLBpred/wrc.csv")
	os.rename("/Users/kasonkang/Downloads/FanGraphs Leaderboard (4).csv", "/Users/kasonkang/Documents/Projects/MLBpred/last7ops.csv")
else:
	os.rename("/Users/kasonkang/Downloads/FanGraphs Leaderboard.csv", "/Users/kasonkang/Documents/Projects/MLBpred/last7ops.csv")