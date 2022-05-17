# scraping-from-wikipedia
This program is the work created in a university lecture. It gets sources from wikipedia(https://ja.wikipedia.org/wiki/2018_FIFA%E3%83%AF%E3%83%BC%E3%83%AB%E3%83%89%E3%82%AB%E3%83%83%E3%83%97) and makes csv file to insert data into a database.

When you execute this program, it makes files as follows:
- wc_group.csv : group data in world cup (e.g. id, group name(A,B,...),...) 
- wc_team.csv : team data (e.g. id, team name, country,...)
- wc_tournament.csv : tournament data (e.g. id, date,...)
- wc_round.csv : round data (e.g. id, round(round of 16, quarter finals,...), date,...)
- wc_match.csv : match data (e.g. id, date,...)
- wc_result.csv : match result data (e.g. id, match id, date, point,...)

## environment
- Python 3.6.9 [GCC 8.4.0] on linux 
