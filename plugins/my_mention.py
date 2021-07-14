# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 12:01:39 2019 @author: ryo
Updated on Sun Jun 27 14:06:00 2021 @author: taipi

"""
from slackbot.bot import respond_to

import pulp
import pandas as pd
import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials


@respond_to('d1')
def d1respond(message):
    text = solver('d1')
    message.send(text)

@respond_to('d2')
def d2respond(message):
    text = solver('d2')
    message.send(text)

@respond_to('d3')
def d3respond(message):
    text = solver('d3')
    message.send(text)

@respond_to('d4')
def d4respond(message):
    text = solver('d4')
    message.send(text)

@respond_to('d5')
def d5respond(message):
    text = solver('d5')
    message.send(text)

@respond_to('d6')
def d6respond(message):
    text = solver('d6')
    message.send(text)

@respond_to('d7')
def d7respond(message):
    text = solver('d7')
    message.send(text)

def solver(id):
    # 大筋は、シート2枚入力、データ整理、最適化計算、出力処理の流れ

    spreadsheet_key = '1Z5bLTtsBsRnhIKBMXxkk29UPWNBkxElp7HLe5omZ4fI'

    sheet_name ='df_up'
    SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    SERVICE_ACCOUNT_FILE = 'plugins/es-spreadsheet-rmsystem-1d49147d5dc7.json'
    # SERVICE_ACCOUNT_FILE ='C:\\Users\\tai\\Desktop\\references\\es-spreadsheet-rmsystem-1d49147d5dc7.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE,SCOPES)
    gs = gspread.authorize(credentials)
    workbook = gs.open_by_key(spreadsheet_key)
    worksheet = workbook.worksheet(sheet_name)

    date_id = id
    date_ids = ["d1","d2","d3","d4","d5","d6","d7"]
    date_index = date_ids.index(date_id)

    df_origin = pd.DataFrame(worksheet.get_all_values())

    # 生のデータからd1(-7)に関するデータ整理のための整形
    # 0全練習　1全名前　2＋index(2)クラス名　9＋index各(3)パラミタ　16+index(4)need
    df_up = df_origin[[0,1,2+date_index, 9+date_index, 16+date_index]]
    df_up = df_up.rename(columns={2+date_index:2, 9+date_index:3, 16+date_index:4})
    df_up = df_up.drop(df_up.index[[0]])


    # df_upシートから加工不要のデータを変数に格納
    # データは人、レッスン、授業コマの3軸のイメージ
    lessons = df_up.iloc[:,0].values.tolist()
    lessons = [i for i in lessons if i !=""]
    members = df_up.iloc[:,1].values.tolist()
    members = [i for i in members if i !=""]
    class_list = df_up[2].tolist()
    class_list = [i for i in class_list if i != ""] # str型として先にリストにしておく。コマの名前

    member_num_list = list(range(1,len(members)+1))     # メンバーのキー番号リスト。Pulpは1から参照することが多いため。
    class_num_list = list(range(1,len(class_list)+1)) # コマのインデックスのリスト。1~
    train_num_list = []                        # 時間を割きたい練習のみの番号リスト。ナップザック問題の石id
    for i in range(len(lessons)):
        if int(df_up.replace('',0).iat[i, 4]) == 1:
            train_num_list.append(i+1)

    lesson_time = int(df_up.iat[0,3])   # 1コマ当たりの時間（分）.データ整理用
    overlap = int(df_up.iat[1,3])   # かぶり許容人数.
    place = int(df_up.iat[2,3])   # 同時練習数
    datedata = df_up.iat[3,3]   # 日付と場所情報.出力用
    participant = df_up.iat[4,3]   # 参加者列挙.出力用

    # 香盤表配列arr_N
    df_need = df_origin.drop(df_origin.columns[[range(23)]],axis=1)
    df_need = df_need.drop(df_need.index[[0]])
    arr_N = df_need.drop(df_need.index[range ( len(lessons), len(df_need.index)) ]).replace("",0).astype("int").values

    df_up[2] = pd.to_datetime(df_up[2])     # 先にclass_listを取得してから型を変換


    # もう一枚のシートの読み込み。フォーム回答シートを読み取る
    # 出席簿配列arr_Aをまとめる。ver4.1まではスプレッドシート側で行っていた処理
    sheet_name = df_up.iat[5,3]+"_"         # シート名の末尾が数字だとエラー
    worksheet = workbook.worksheet(sheet_name)
    df_down = pd.DataFrame(worksheet.get_all_values())

    # 該当日を切り出し
    df_res = df_down[[0,1,3*date_index+2, 3*date_index+3, 3*date_index+4]]
    df_res = df_res.rename(columns={3*date_index+2:2, 3*date_index+3:3, 3*date_index+4:4})
    df_res = df_res.drop(df_res.index[[0]])

    # 参加早退の空欄を適切に埋める（00:00を基準時間とする）
    df_res = df_res.replace("","00:00:00")
    for i in range(len(df_res.index)):
      if df_res.iat[i,2] != "欠席 or 未定" and df_res.iat[i,4] == "00:00:00":
        df_res.iat[i,4] = "23:59:59"

    # タイムスタンプが最新のものから1ヶ月前のものは棄却
    for i in [0,3,4]:
      df_res[i] = pd.to_datetime(df_res[i])
    lastans = df_res.iat[len(df_res.index)-1,0]
    df_res = df_res.set_index(0)[lastans - datetime.timedelta(days=30):lastans]

    # 重複した古いデータを削除し、名前列[1]でjoin(vlookup)する
    df_res = df_res.drop_duplicates(subset=1,keep="last")
    df_res = pd.merge(df_up[[1]], df_res, on=1,how="left")

    # 行：練習コマ、列：メンバーで出席１、欠席０の配列にする
    df_lesson = pd.DataFrame(df_up[2].dropna())
    df_attend = pd.DataFrame(columns=range(len(df_res.index)),index=range(len(df_lesson.index)))
    for i in range(len(df_lesson.index)):
      for j in range(len(df_res.index)):
        if df_res.iat[j,2] <= df_lesson.iat[i,0] and df_lesson.iat[i,0] + datetime.timedelta(minutes=lesson_time) <= df_res.iat[j,3]:
          df_attend.iat[i,j] = 1
        else:
          df_attend.iat[i,j] = 0
    arr_A = df_attend.values   # 出席簿配列


    # ここまでデータ整理
    # ここからPulpによる最適化


    m = pulp.LpProblem("bestpractice", pulp.LpMaximize)
    x = pulp.LpVariable.dicts('X', (member_num_list, train_num_list, class_num_list), 0, 1, pulp.LpInteger)#tコマにiさんがj練習をするかどうか
    y = pulp.LpVariable.dicts('Y', (train_num_list, class_num_list), 0, 1, pulp.LpInteger)#tコマにj練習をするかどうか
    m += pulp.lpSum(x[i][j][t] for i in member_num_list for j in train_num_list for t in class_num_list ), "TotalPoint"
    #制約
    for t in class_num_list:             #「１」練習はまとめて4つまで　t期にする練習全部足したらw以下に
        m += pulp.lpSum(y[j][t] for j in train_num_list) <= place              
    for j in train_num_list:        #「２」同じ練習は1回まで　jの練習に対して全期分足したら1以下に    
        m += pulp.lpSum(y[j][t] for t in class_num_list) <= 1            
    for i in member_num_list:       #「３」やる練習にしか参加できない　参加しないのはあり    
        for j in train_num_list:
            for t in class_num_list:
                m += x[i][j][t] <= y[j][t]
    for i in member_num_list:       #「４」必要な練習しかしない　必要な練習でもやらないのはあり
        for j in train_num_list:
            for t in class_num_list:
                m += x[i][j][t] <= arr_N[j-1][i-1]
    for i in member_num_list:       #「５」いる人しか参加しない　いる人で参加しないのはあり
        for j in train_num_list:
            for t in class_num_list:
                m += x[i][j][t] <= arr_A[t-1][i-1]
    for i in member_num_list:       #「６」tコマで1人ができる練習は1つまで
        for t in class_num_list:
            m += pulp.lpSum(x[i][j][t] for j in train_num_list) <= 1
    for t in class_num_list:             #「７」各期の参加人数はいる人でやる練習に参加可の人の合計よりK人少ない人数以上必要
        m += pulp.lpSum(x[i][j][t] for i in member_num_list for j in train_num_list) >= pulp.lpSum(arr_N[j-1][i-1]*arr_A[t-1][i-1]*y[j][t] for i in member_num_list for j in train_num_list) - overlap
    m += pulp.lpSum(y[j][t] for j in train_num_list for t in class_num_list) == len(train_num_list)#入れた練習は全て採用する
    m.solve()


    # **出力文**

    msg_list = []
    msg_list.append(datedata+"\n")
    # msg_list.append(str(pulp.LpStatus[m.solve()]))
    msg_list.append("練習数は"+str(len(train_num_list))+"\n")
    msg_list.append("=============処理結果=============\n")
    if pulp.LpStatus[m.solve()] != "Infeasible":
        msg_list.append("練習は入りきった！\n")
        msg_list.append("総練習人数は"+str(round(pulp.value(m.objective)))+"人"+"\n")
    #結果
        msg_list.append("\n=============メニュー=============\n")
        msg_list.append(datedata+"\n参加者\n"+participant+"\n")
        t1 = 0
        j1 = 0
        for t in class_num_list:
            tt = 0
            for j in train_num_list:
                if pulp.value(y[j][t]) == 1:
                    if t1 != t:
                        t1 = t
                    if j1 != j:
                        j1 = j
                        tt += 1
                        if tt == 1:
                            msg_list.append("\n"+class_list[t-1]+"\n")
                        msg_list.append(lessons[j-1]+"\n")
        msg_list.append("\n\n==============詳細==============")
        t1 = 0
        j1 = 0
        for t in class_num_list:
            tt = 0
            for j in train_num_list:
                if pulp.value(y[j][t]) == 1:
                    if t1 != t:
                        t1 = t
                    if j1 != j:
                        j1 = j
                        tt += 1
                        if tt == 1:
                            msg_list.append("\n\n"+class_list[t-1]+"\n")
                        msg_list.append(lessons[j-1]+"\n")
            msg_list.append("【被り】\n")
            for j in train_num_list:
                for i in member_num_list:
                    if pulp.value(x[i][j][t] ) != pulp.value(arr_N[j-1][i-1]*arr_A[t-1][i-1]*y[j][t]):
                        msg_list.append(members[i-1]+"　")
            msg_list.append("\n【やることない】\n")
            for i in member_num_list:
                if arr_A[t-1][i-1] == 1:
                    if pulp.value(pulp.lpSum(x[i][j][t] for j in train_num_list)) == 0:
                        msg_list.append(members[i-1]+"　")
    else:
        msg_list.append("練習は入り切らなかった．被り人数許容上限="+str(overlap)+",同時練習許容上限="+str(place)+"\n")
        msg_list.append("K(被り人数許容上限)やW(同時練習許容上限)を大きくするか，練習するメニュー減らしてみてね")

    msg = str()
    for i in msg_list:
        msg = msg + i
    return msg
