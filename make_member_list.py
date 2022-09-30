import requests
import pymysql.cursors
from bs4 import BeautifulSoup
import csv
import re
import datetime
import sys
import os
import gc


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
    for i in range(len(data_list[0][0])):
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


def get_source(url): # urlに指定されたWebページのhtmlを取得
    req = requests.get(url)
    source = req.text

    return source


def get_data_from_db(sql): # 指定されたsqlを実行して,データベースからの結果を返す関数
    conn = pymysql.connect (
        user='', # データベースに登録したユーザネーム
        passwd='', # 当該ユーザのパスワード
        host='127.0.0.1', # データベースのアドレス
        db='' # 配布されたdumpファイル(worldcup_data.dump)を読み込んだデータベース名
    )

    cur = conn.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def write_into_csv(data_list, file_name): # data_list(リスト型)の要素を指定された,CSVファイルへ書きだす
    file_object = open(file_name, 'w')
    writer = csv.writer(file_object)

    """
    for i in range(len(data_list)):
        writer.writerow(data_list[i])
    """

    for i in data_list:
        for j in i:
            writer.writerow(j)

    file_object.close()


def make_team_id_dict():
    sql = 'SELECT id, name FROM wc_team'
    team_data = get_data_from_db(sql)
    
    team_id_dict = {}
    for i in team_data:
        team_id_dict[i[1]] = i[0]

    return team_id_dict


def get_player_info(player_id, tournament_id, source):
    soup = BeautifulSoup(source, 'html.parser')
    player_info_tables = soup.find_all('table', {'class': 'sortable wikitable plainrowheaders'})
    total_team_num = len(player_info_tables)
    if tournament_id == 14:
        total_team_num -= 2

    soup = BeautifulSoup(source, 'html.parser')
    team_name_source = soup.find_all('li')
    team_name_list = []
    for i in range(len(team_name_source)):
        tmp = team_name_source[i].get_text()
        if not 'Group' in tmp:
            # team_name_list.append(re.sub('\[.+\]', '', team_name_source[i].get_text()))
            team_name_list.append(re.sub('([0-9].*[0-9] )|([0-9] )', '', tmp, 1))
        
    team_name_list = team_name_list[:total_team_num]
    team_id_dict = make_team_id_dict()

    player_info_source = []
    player_info = []
    for i in range(total_team_num):
        player_info_tables[i] = str(player_info_tables[i]).replace('\n', '').replace('<tr class="nat-fs-player">', '\n<tr class="nat-fs-player">')
        player_info_source.append(player_info_tables[i].splitlines())

        for j in player_info_source[i]:
            soup = BeautifulSoup(j, 'html.parser')
            tmp_list = [k.get_text() for k in soup.find_all('a')]
            if not tmp_list == []:
                if team_name_list[i] == 'Dutch East Indies':
                    team_name_list[i] += ' (-1945)'
                elif team_name_list[i] == 'Republic of Ireland':
                    team_name_list[i] = 'Ireland'
                elif team_name_list[i] == 'China PR':
                    team_name_list[i] = 'China'
                elif team_name_list[i] == 'Ivory Coast':
                    team_name_list[i] = 'C?te d\'Ivoire'
                elif team_name_list[i] == 'Serbia and Montenegro':
                    team_name_list[i] = 'Serbia'
                elif team_name_list[i] == 'Bosnia and Herzegovina':
                    team_name_list[i] = 'Bosnia-Herzegovina'
                player_info.append([player_id, tournament_id, team_id_dict[team_name_list[i]], tmp_list[1], tmp_list[0]])
                player_id += 1

            del tmp_list
            gc.collect()
   
    return player_info


def make_player_data():
    new_player_data = []

    player_id = 1
    tournament_year_data = get_data_from_db('SELECT id, year FROM wc_tournament') # tuple型 : ((year, ''), ...)
    tournament_id_list = []
    all_tournament_year = []

    for i in tournament_year_data:
        tournament_id_list.append(i[0])
        all_tournament_year.append(i[1].replace('年', ''))

    url_1 = 'https://en.wikipedia.org/wiki/'
    url_2 = '_FIFA_World_Cup_squads'

    for i in range(len(all_tournament_year)):
        url = url_1 + all_tournament_year[i] + url_2

        # req = requests.get(url)
        # source = req.text
        source = get_source(url)

        tmp_list = get_player_info(player_id, tournament_id_list[i], source)
        player_id = tmp_list[-1][0] + 1
        new_player_data.append(tmp_list)
        del tmp_list
        gc.collect()
        
        # soup = BeautifulSoup(source, 'html.parser')

    write_into_csv(new_player_data, 'wc_player.csv')
    make_record('player_record.txt', str(player_id))
    insert_into_db(new_player_data, 'wc_player.csv')


def main():
    make_player_data()
    # get_player_info(1, 21, get_source('https://en.wikipedia.org/wiki/2018_FIFA_World_Cup_squads'))
    # make_team_id_dict()

main()
