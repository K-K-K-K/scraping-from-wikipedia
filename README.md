# scraping-from-wikipedia
This program is the work created in a university lecture. It gets sources from wikipedia(https://ja.wikipedia.org/wiki/2018_FIFA%E3%83%AF%E3%83%BC%E3%83%AB%E3%83%89%E3%82%AB%E3%83%83%E3%83%97) and makes csv file to insert data into a database.

When you execute this program, it makes files as follows:
- wc_group.csv : group data in world cup (e.g. id, group name(A,B,...),...) 
- wc_team.csv : team data (e.g. id, team name, country,...)
- wc_tournament.csv : tournament data (e.g. id, date,...)
- wc_round.csv : round data (e.g. id, round(round of 16, quarter finals,...), date,...)
- wc_match.csv : match data (e.g. id, date,...)
- wc_result.csv : match result data (e.g. id, match id, date, point,...)
- wc_player.csv : player data (e.g. player id, name, positon, team,...)

## environment
- Python 3.6.9 [GCC 8.4.0] on linux 

## reference
- 鎖プログラム  (2018) 「Python Beautiful Soupをインストールする方法」 <https://pg-chain.com/python-beautiful-soup4>
- @mitch0807 (2018) 「Python3からMySQL繋ぐ時は、いろいろあるけどとりあえずPyMySQLにしとこうや」 Qiita <https://qiita.com/mitch0807/items/f9f6efd4e65a022a8ab9>
- @johndoe1022 (2018) 「pythonでmariaDB(mysql)を操作する方法」 Qiita <https://qiita.com/johndoe1022/items/0c704a64a38d876e8bdf>
- 鎖プログラム (2018) 「Python requestsを使ってグーグル検索をする」 <https://pg-chain.com/python-requests-google>
- あずみ.net (2015) 「【Python】 CSVファイルを読みこんでMySQLでデータベースに保存」<https://a-zumi.net/python-insert-csv/>
- 宗定洋平 (2015) 「YoheiM.NET-プログラミングで困ったその時に、役立つネタを発信!- [Python] MySQLに接続してデータ操作を行う」 <https://www.yoheim.net/blog.php?q=20151102>
- @Chanmoro (2019) 「10分で理解するBeautifulSoup」Qiita <https://qiita.com/Chanmoro/items/db51658b073acddea4ac>
- @nittyan (2017) 「Requestsで日本語を扱う時の文字化けを直す」 Qiita <https://qiita.com/nittyan/items/d3f49a7699296a58605b>
- Python Software Foundation. 「re --- 正規表現操作」 <https://docs.python.org/ja/3/library/re.html>
- @ryosuketter (2018) 「テーブルの作成手順(MySQL)」 Qiita <https://qiita.com/ryosuketter/items/713c7046314ecdf1a4a9>
- たきもと.com (2020) 「MySQL Cannot add foreign key constraint で怒られた」 <https://kengotakimoto.com/post-2152/>

