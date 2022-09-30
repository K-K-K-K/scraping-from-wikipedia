import requests
import pymysql.cursors
from bs4 import BeautifulSoup
import csv
import re
import datetime
import sys
import os


def make_record(file_name, data):
    file_object = open(file_name, 'w')
    file_object.write(data)
    file_object.close()


def insert_into_db(data_list, csv_file):
    conn = pymysql.connect (
        user='', # データベースに登録したユーザネーム
        passwd='', # 当該ユーザのパスワード
        host='127.0.0.1', # データベースのアドレス
        db='' # 配布されたdumpファイル(worldcup_data.dump)を読み込んだデータベース名
    )

    cur = conn.cursor()
    sql = 'INSERT INTO ' + csv_file[:len(csv_file)-4] + ' VALUES ('
    for i in range(len(data_list[0])):
        sql += '%s,'
    sql = sql[:len(sql)-1] + ');'

    file_object = open(csv_file, 'r')
    reader = csv.reader(file_object)

    for row in reader:
        cur.execute(sql, row)
    conn.commit()

    file_object.close()
    cur.close()
    conn.close()


def get_source(url): # get source data from web page of url. 
    req = requests.get(url)
    source = req.text

    return source


def get_data_from_db(sql): # get data from db with executing sql
    conn = pymysql.connect (
        user='', # データベースに登録したユーザネーム
        passwd='', # 当該ユーザのパスワード
        host='127.0.0.1',
        db='' # 配布されたdumpファイル(worldcup_data.dump)を読み込んだデータベース名
    )

    cur = conn.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def write_into_csv(data_array, file_name): # write data_rows in array into csv file
    file_object = open(file_name, 'w')
    writer = csv.writer(file_object)

    for i in range(len(data_array)):
        writer.writerow(data_array[i])

    file_object.close()


def get_group_data(source):
    new_group_data = []

    last_group_id = get_data_from_db('SELECT id FROM wc_group ORDER BY id DESC LIMIT 1;')[0][0]

    if os.path.isfile('group_record.txt'):
        print('data was already inserted')
        sys.exit()

    group_id = last_group_id + 1

    regex = re.compile(r'title=\"2018 FIFAワールドカップ・グループ.{1,2}">グループ.{1,2}</a>')
    text_list = regex.findall(source)
    group_name_list = []

    for i in range(len(text_list)):
        group_name = re.search(r'title=\"2018 FIFAワールドカップ・グループ(.{1,2})\">グループ.*</a>', text_list[i]).group(1)

        group_name = 'グループ ' + group_name

        if not group_name in group_name_list:
            group_name_list.append(group_name)

    ordering = 1
    for i in range(len(group_name_list)):
        new_group_data.append([group_id, group_name_list[i], ordering])
        group_id += 1
        ordering += 1

    write_into_csv(new_group_data, 'wc_group.csv')
    # insert_into_db(new_group_data, 'wc_group.csv')
    # make_record('group_record.txt', group_id - 1)

    return new_group_data


def get_team_id(source): # get team_id from wc_team
    regex_new_country_count = re.compile('初出場')
    new_team_count = len(regex_new_country_count.findall(source)) - 1

    if new_team_count > 0:
        new_team_data = []

        sql = 'SELECT id FROM wc_team ORDER BY id DESC LIMIT 1'
        team_id = get_data_from_db(sql)[0][0] + 1
        # print(last_team_id)

        regex_new_country = '<p>初出場は'
        new_country_name = []
        for i in range(new_team_count):
            regex_new_country += '<a href=\".+\" title=\"サッカー.+代表\">(.*)</a>、'

        regex_new_country = regex_new_country[:len(regex_new_country)-1] 
        regex_new_country += 'で'
        country_searched = re.search(regex_new_country, source)
        for i in range(new_team_count):
            new_country_name.append(country_searched.group(i+1))

        # print(new_country_name)
        url = 'https://www.google.com/search'
        url_set = []
        for i in new_country_name:
            req = requests.get(url, params={'q': i+'外務省', 'ie': 'utf-8', 'hl': 'ja', 'lr': 'lang_ja'})
            soup = BeautifulSoup(req.text, 'html.parser')
            links = [url.get('href') for url in soup.find_all('a')]

            for j in links:
                if 'mofa.go.jp/mofaj/area/' in j and 'index' in j:
                    url_set.append(re.sub('&.*', '', j.replace('/url?q=', ''))) 

        # print(url_set)

        new_country_area = []
        new_team_name = []
        for i in url_set:
            req = requests.get(i)
            req.encoding = req.apparent_encoding
            soup = BeautifulSoup(req.text, 'html.parser')
            new_country_area.append(soup.find_all('h1', {'class': 'title1'})[0].get_text())

            new_team_name.append(i.replace('https://www.mofa.go.jp/mofaj/area/', '').replace('/index.html', ''))

        # print(new_team_name) 

        new_country_latitude = []
        new_country_longitude = []

        del url_set
        # gc.collect()

        target_page_code = '' # 検索するwebページのurlに指定される番号(ex : https://www.~/4321.aspx)
        for i in new_country_name:
            print(i)
            req = requests.get(url, params={'q': i+'緯度', 'ie': 'utf-8', 'hl': 'ja', 'lr': 'lang_ja'})
            target_page_code = re.search('<a href="/url\?q=https://www.kyorikeisan.com/ido-keido-kensaku/idotokeidonorekishi/([0-9]+).aspx\&amp;', req.text).group(1)

            target_url = 'https://www.kyorikeisan.com/ido-keido-kensaku/idotokeidonorekishi/' + target_page_code + '.aspx' #緯度,経度の取得には,kyorikeisan.comというサイトを利用

            req = requests.get(target_url)
            new_country_latitude.append(re.search('<span id="MC_GMD_lblLatitude" class="fntBold" itemprop="Latitude">\&nbsp;(.+)</span>', req.text).group(1))
            new_country_longitude.append(re.search('<span id=\"MC_GMD_lblLongitude\" class=\"fntBold\" itemprop=\"Longitude\">\&nbsp;(.+)</span>', req.text).group(1))
            print(new_country_latitude)
            print(new_country_longitude)

        for i in range(new_team_count):
            new_team_data.append([team_id, new_team_name[i], new_country_name[i], new_country_name[i], new_country_area[i], new_country_latitude[i], new_country_longitude[i]])
            team_id += 1

        write_into_csv(new_team_data, 'wc_team.csv')
        insert_into_db(new_team_data, 'wc_team.csv')

    regex = re.compile(r'<a href=.*#.*_vs_.*" .*')
    matched_text = regex.findall(source)

    team_list = [] # タプル: team1, team2
    for l in matched_text:
        team_names = re.search(r'#(.*)_vs_(.*)\" title=\".* FIFA(.*)', l).group(1, 2)
        team_list.append(team_names) 

    regex = re.compile(r'<p><span class=\".*\" style="display: none;"><a href=\".*\" title=\"サッカー.*代表\">.*</a> <a .*><img .*/></a> v <a .*><img .*/></a> <a href=\".*\" title=\"サッカー.*代表\">.*</a></span>')

    matched_text = regex.findall(source)
    for l in matched_text:
        team_names = re.search(r'<p><span class=\".*\" style="display: none;"><a href=\".*\" title=\"サッカー.*代表\">(.*)</a> <a .*><img .*/></a> v <a .*><img .*/></a> <a href=\".*\" title=\"サッカー.*代表\">(.*)</a></span>', l).group(1, 2)

        if not team_names in team_list:
            team_list.append(team_names)

    tmp_list = [[0] * 2 for i in range(len(team_list))]

    for i in range(len(team_list)):
        sql = 'SELECT id FROM wc_team WHERE country LIKE \''
        if team_list[i][0] == '韓国':
            sql += '大韓民国'
        else :
            sql += team_list[i][0]
        sql += '%\';'
        tmp_list[i][0] = get_data_from_db(sql)

        sql = 'SELECT id FROM wc_team WHERE country LIKE \''
        if team_list[i][1] == '韓国':
            sql += '大韓民国'
        else :
            sql += team_list[i][1]
        sql += '%\';'
        tmp_list[i][1] = get_data_from_db(sql)

    team_id_list = [[0] * 2 for i in range(len(team_list))]

    for i in range(len(team_list)):
        team_id_list[i][0] = tmp_list[i][0][0][0]
        team_id_list[i][1] = tmp_list[i][1][0][0]

    return team_id_list # team_id_list : 2-dimension array [i][0] : team_id1 // [i][1] : team_id2


def get_tournament_id(source):
    new_tournament_data = []

    regex = re.compile(r'開催国.*\s<a href=".*:Flag_of_.*\.svg" class="image" title=".*"><img alt=".*" src=".*\.svg\.png" decoding="async" width=".*" height=".*" class="thumbborder" srcset=".*" data-file-width=".*" data-file-height=".*" /></a> <a href=".*" title=".*">.*</a></td></tr>')
    found_text = regex.findall(source)
    country = re.search(r'<a href=\".*\" title=\".*\">(.*)</a>.*', found_text[0]).group(1)

    regex = re.compile(r'日程</th><td .*>\s<a .*title=".*">.*</a><a .*title=".*">.*</a> - ')
    found_text = regex.findall(source)
    date = re.search(r'\s<a .*title=".*">(.*)</a><a .*title=".*">(.*)</a> - ', found_text[0]).group(1, 2)
    year = re.search(r'(.*)年', date[0]).group(1)
    day = re.search(r'(.*)月(.*)日', date[1]).group(1,2)

    sql = 'SELECT id, year FROM wc_tournament ORDER BY id DESC LIMIT 1;'
    result = get_data_from_db(sql)
    last_tournament_id = result[0][0]
    
    if result[0][1] == (str(year) + '年'):
        print('data was already inserted')
        return last_tournament_id

    tournament_id = int(last_tournament_id) + 1

    new_tournament_data.append([tournament_id, str(year)+'年 '+country, datetime.date(int(year),int(day[0]),int(day[1])), str(year)+'年', country])

    write_into_csv(new_tournament_data, 'wc_tournament.csv')

    return tournament_id
    

def get_round_id(source):
    tournament_id = get_tournament_id(source)
    
    sql = "SELECT id FROM wc_round ORDER BY id DESC LIMIT 1 ;"
    last_round_id = get_data_from_db(sql)[0][0] # クエリの処理の結果はタプル
    if last_round_id == 310:
        return last_round_id

    round_id = last_round_id + 1

    regex = re.compile(r'<td><div style=\".*\">[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日<br />.*')
    group_stage_date_text = regex.findall(source)
    
    regex = re.compile(r'<td><div style=\".*\"><a href=\".*\" title=\".*\">[0-9]{4}年</a><a href=\".*\" title=\".*\">[0-9]{1,2}月[0-9]{1,2}日</a><br />.*')
    knockout_stage_date_text = regex.findall(source)

    group_stage_date = []
    knockout_stage_date = []
    index = 0

    for i in group_stage_date_text:
        date_match_object = re.search(r'<td><div style=\".*\">([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日<br />.*', i)
        date = datetime.date(int(date_match_object.group(1)), int(date_match_object.group(2)), int(date_match_object.group(3)))

        if not date in group_stage_date:
            group_stage_date.append(date)

    for i in knockout_stage_date_text:
        date_match_object = re.search(r'<td><div style=\".*\"><a href=\".*\" title=\".*\">([0-9]{4})年.*([0-9]{1,2})月([0-9]{1,2})日.*', i)
        date = datetime.date(int(date_match_object.group(1)), int(date_match_object.group(2)), int(date_match_object.group(3)))
        knockout_stage_date.append(date)

    ordering = 101
    knockout = 2
    new_round_data = []

    group_stage_date.sort()
    for i in range(len(group_stage_date)):
        new_round_data.append([round_id, tournament_id, '第' + str(i + 1) + '試合', ordering, knockout, group_stage_date[i], group_stage_date[i]])
        round_id += 1
        ordering += 1

    knockout = 1

    new_round_data.append([round_id, tournament_id, 'ベスト16(決勝トーナメント1回戦)', 5, knockout, knockout_stage_date[0], knockout_stage_date[7]])
    round_id += 1
    new_round_data.append([round_id, tournament_id, '準々決勝', 3, knockout, knockout_stage_date[8], knockout_stage_date[11]])
    round_id += 1
    new_round_data.append([round_id, tournament_id, '準決勝', 2, knockout, knockout_stage_date[12], knockout_stage_date[13]])
    round_id += 1
    new_round_data.append([round_id, tournament_id, '3位決定戦', 4, knockout, knockout_stage_date[14], knockout_stage_date[14]])
    round_id += 1
    new_round_data.append([round_id, tournament_id, '決勝', 1, knockout, knockout_stage_date[15], knockout_stage_date[15]])

    write_into_csv(new_round_data, 'wc_round.csv')

    return new_round_data # new_round_data is list which has round_id, tournament_id, name, ordering, knockout_code, start_date, end_date


def get_match_id(source):
    sql = "SELECT id FROM wc_match ORDER BY id DESC LIMIT 1;"
    last_match_id = get_data_from_db(sql)[0][0]
    match_id = last_match_id + 1

    round_data = get_round_id(source)
    regex = re.compile(r'<td><div style=\".*\">[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日<br />[0-9]{1,2}:[0-9]{1,2}.*')
    group_stage_time_text = regex.findall(source)

    regex = re.compile(r'<td><div style=\".*\"><a href=\".*\" title=\".*\">[0-9]{4}年</a><a href=\".*\" title=\".*\">[0-9]{1,2}月[0-9]{1,2}日</a><br />[0-9]{1,2}:[0-9]{1,2}.*')
    knockout_stage_time_text = regex.findall(source)

    match_time = []
    for i in range(len(group_stage_time_text)):
        group_stage_time = re.search(r'<td><div style=\".*\">([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日<br />([0-9]{1,2}:[0-9]{1,2}) <a href=.*', group_stage_time_text[i])
        match_time.append([group_stage_time.group(1), group_stage_time.group(2), group_stage_time.group(3), group_stage_time.group(4)])

    for i in range(len(knockout_stage_time_text)):
        knockout_stage_time = re.search(r'<td><div style=\".*\"><a href=\".*\" title=\".*\">([0-9]{4})年</a><a href=\".*\" title=\".*\">([0-9]{1,2})月([0-9]{1,2})日</a><br />([0-9]{1,2}:[0-9]{1,2}).*', knockout_stage_time_text[i])
        match_time.append([knockout_stage_time.group(1), knockout_stage_time.group(2), knockout_stage_time.group(3), knockout_stage_time.group(4)])

    group_data = get_group_data(source) # list
    new_match_data = []
    knockout = 0

    round_dict = {}
    for i in range(len(match_time)):
        for j in range(len(round_data)):
            date = datetime.date(int(match_time[i][0]), int(match_time[i][1]), int(match_time[i][2]))
            if round_data[j][5] <= date <= round_data[j][6]:
                round_dict[date.strftime('%Y-%m-%d')] = round_data[j][0]
                break

    time_list_for_order = []
    for i in range(len(match_time)):
        time_list_for_order.append(datetime.datetime(int(match_time[i][0]), int(match_time[i][1]), int(match_time[i][2]), int(match_time[i][3][0:match_time[i][3].find(':')]), int(match_time[i][3][match_time[i][3].find(':')+1:])))

    order_dict = {}
    time_list_for_order.sort()
    for i in range(len(time_list_for_order)):
        order_dict[time_list_for_order[i]] = i+1
    
    count = 0
    for i in range(len(group_data)):
        for j in range(6): # Combination(4,2) = 6, in 1 group, there are 4 teams so match has 6-times 
            round_id = round_dict[datetime.date(int(match_time[count][0]), int(match_time[count][1]), int(match_time[count][2])).strftime('%Y-%m-%d')]
            new_match_data.append([match_id, round_id, group_data[i][0], datetime.datetime(int(match_time[count][0]), int(match_time[count][1]), int(match_time[count][2]), int(match_time[count][3][0:match_time[count][3].find(':')]), int(match_time[count][3][match_time[count][3].find(':')+1:])), order_dict[datetime.datetime(int(match_time[count][0]), int(match_time[count][1]), int(match_time[count][2]), int(match_time[count][3][0:match_time[count][3].find(':')]), int(match_time[count][3][match_time[count][3].find(':')+1:]))], knockout])
            count += 1
            match_id += 1

    knockout = 1
    for i in range(len(match_time)-len(group_data)*6):
        
        round_id = round_dict[datetime.date(int(match_time[count][0]), int(match_time[count][1]), int(match_time[count][2])).strftime('%Y-%m-%d')]
        new_match_data.append([match_id, round_id, 0, datetime.datetime(int(match_time[count][0]), int(match_time[count][1]), int(match_time[count][2]), int(match_time[count][3][0:match_time[count][3].find(':')]), int(match_time[count][3][match_time[count][3].find(':')+1:])), order_dict[datetime.datetime(int(match_time[count][0]), int(match_time[count][1]), int(match_time[count][2]), int(match_time[count][3][0:match_time[count][3].find(':')]), int(match_time[count][3][match_time[count][3].find(':')+1:]))], knockout])
        count += 1
        match_id += 1

    write_into_csv(new_match_data, 'wc_match.csv')
    return new_match_data

    
def make_result_data(source):
    new_result_data = []
    duplicate = '重複を省く'

    last_result_id = get_data_from_db('SELECT id FROM wc_result ORDER BY id DESC LIMIT 1;')[0][0]
    if last_result_id == 1763:
        return
    result_id = last_result_id + 2
    team_id_set = get_team_id(source)
    match_data = get_match_id(source)

    bs_object = BeautifulSoup(source, 'html.parser')
    div_elems = bs_object.find_all('div', {'class': 'vevent'})
    texts_in_div = []
    for i in div_elems:
        texts_in_div.append((re.sub('[0-9]\+', '', re.sub(',+', ',', i.get_text().replace('\n', ',').replace(u'\xa0', u',')))).replace(',', ', '))
    
    regex_for_extra = re.compile('.{3}分')

    rs = 0
    rs_extra = ''
    rs_pk = ''
    ra = '' 
    ra_extra = ''
    ra_pk = ''
    difference = ''
    outcome = ''
    outcome_90 = ''
    count_win = ''
    count_lose = ''
    count_stillmate = ''
    point = ''
    extra = ''
    pk = 0

    count = 0
    for i in texts_in_div:
        if not '延長' in i:
            score = re.search('([0-9]+) (-|−) ([0-9]+)', i)
            rs = int(score.group(1))
            ra = int(score.group(3))
            difference = rs - ra

            if difference > 0:
                outcome = '勝利'
                outcome_90 = '勝利'
                count_win = '1'
                count_lose = '0'
                count_stillmate = '0'
                point = '3'
                extra = '0'
                pk = 0

            elif difference == 0:
                outcome = '引き分け'
                outcome_90 = '引き分け'
                count_win = '0'
                count_lose = '0'
                count_stillmate = '1'
                point = '1'
                extra = '0'
                pk = 0

            else:
                outcome = '敗北'
                outcome_90 = '敗北'
                count_win = '0'
                count_lose = '1'
                count_stillmate = '0'
                point = '0'
                extra = '0'
                pk = 0

        else:
            if not 'PK' in i:
                score = re.search('([0-9]+) (-|−) ([0-9]+)', i)
                # print(score.group(1), score.group(3))
                rs_total = int(score.group(1))
                ra_total = int(score.group(3))

                goal_time = regex_for_extra.findall(i)
                count_goal_extra = 0
                # print(goal_time)
                for j in goal_time:
                    if int(j.replace(',', '').replace(' ', '').replace('分', '')) >= 96:
                        count_goal_extra += 1

                rs = (rs_total + ra_total - count_goal_extra) // 2
                ra = rs
                rs_extra = str(rs_total - rs)
                ra_extra = str(ra_total - ra)

                difference = '0'
                difference_extra = rs_total - ra_total
                if difference_extra > 0:
                    outcome = '勝利'
                    outcome_90 = '引き分け'
                    count_win = '0'
                    count_lose = '0'
                    count_stillmate = '1'
                    point = '3'
                    extra = '1'
                    pk = 0

                else:
                    outcome = '敗北'
                    outcome_90 = '引き分け'
                    count_win = '0'
                    count_lose = '0'
                    count_stillmate = '1'
                    point = '0'
                    extra = '1'
                    pk = 0   

            else:
                score = re.search('([0-9]+) (-|−) ([0-9]+) \(延長\)', i)
                rs_total = int(score.group(1))
                ra_total = int(score.group(3))

                goal_time = regex_for_extra.findall(i)
                count_goal_extra = 0
                # print(goal_time)
                for j in goal_time:
                    if int(j.replace(',', '').replace(' ', '').replace('分', '')) >= 96:
                        count_goal_extra += 1

                rs = (rs_total + ra_total - count_goal_extra) // 2
                ra = rs
                rs_extra = str(rs_total - rs)
                ra_extra = str(ra_total - ra)

                difference = '0'

                pk_score = re.search('PK.*([0-9]+) (-|–) ([0-9]+)', i)
                rs_pk = int(pk_score.group(1))
                ra_pk = int(pk_score.group(3))

                if rs_pk > ra_pk:
                    outcome = '勝利'
                    outcome_90 = '引き分け'
                    count_win = '0'
                    count_lose = '0'
                    count_stillmate = '1'
                    point = '3'
                    extra = '1'
                    pk = 1 

                else:
                    outcome = '敗北'
                    outcome_90 = '引き分け'
                    count_win = '0'
                    count_lose = '0'
                    count_stillmate = '1'
                    point = '0'
                    extra = '1'
                    pk = 1

        difference = str(difference)
        ra = str(ra)

        new_result_data.append([result_id, match_data[count][0], team_id_set[count][0], team_id_set[count][1], rs, rs_extra, rs_pk, ra, ra_extra, ra_pk, difference, outcome, outcome_90, count_win, count_lose, count_stillmate, point, extra, pk, duplicate])

        result_id += 2
        rs = 0
        rs_extra = ''
        rs_pk = ''
        ra = '' 
        ra_extra = ''
        ra_pk = ''
        difference = ''
        outcome = ''
        outcome_90 = ''
        count_win = ''
        count_lose = ''
        count_stillmate = ''
        point = ''
        extra = ''
        pk = 0

        count += 1

    write_into_csv(new_result_data, 'wc_result.csv')


def main():
    url = 'https://ja.wikipedia.org/wiki/2018_FIFA%E3%83%AF%E3%83%BC%E3%83%AB%E3%83%89%E3%82%AB%E3%83%83%E3%83%97' # 検索対象のWebページのURL
    # make_result_data(get_source(url))
    get_team_id(get_source(url))


main()
