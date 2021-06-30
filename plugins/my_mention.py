# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 12:01:39 2019 @author: ryo
Updated on Sun Jun 27 14:06:00 2021 @author: taipi

"""
from slackbot.bot import respond_to
import pulp
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


@respond_to('d1')
def d1respond(message):
    text = solver('d1')
    message.send(text)

@respond_to('d2')
def d1respond(message):
    text = solver('d2')
    message.send(text)

@respond_to('d3')
def d1respond(message):
    text = solver('d3')
    message.send(text)

@respond_to('d4')
def d1respond(message):
    text = solver('d4')
    message.send(text)

@respond_to('d5')
def d1respond(message):
    text = solver('d5')
    message.send(text)

@respond_to('d6')
def d1respond(message):
    text = solver('d6')
    message.send(text)

@respond_to('d7')
def d1respond(message):
    text = solver('d7')
    message.send(text)

def solver(id):
    
    spreadsheet_key = ''
    date_id = id
    date_ids = ["d1","d2","d3","d4","d5","d6","d7"]
    bikou = ""

    SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'C:\\Users\\tai\Desktop\\references\\es-spreadsheet-rmsystem-1d49147d5dc7.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE,SCOPES)
    gs = gspread.authorize(credentials)
    workbook = gs.open_by_key(spreadsheet_key)

    worksheet = workbook.worksheet(date_id)
    # print(worksheet.acell("F1").value)
    df_A = pd.DataFrame(worksheet.get_all_values()).dropna(how="all").dropna(how="all",axis=1).fillna(int(0)).replace('',0)
    worksheet = workbook.worksheet('3_need')
    df_N = pd.DataFrame(worksheet.get_all_values()).dropna(how="all").fillna(int(0)).replace('',0)
    # GS採用に際してカラム指定がうまくいかなかったが書き直すの面倒なのでずらす
    for i in df_A.columns:
        df_A = df_A.rename(columns={i: df_A.iat[0,i]})
    df_A = df_A.drop(df_A.index[[0]])
    for i in df_N.columns:
        df_N = df_N.rename(columns={i: df_N.iat[0,i]})
    df_N = df_N.drop(df_N.index[[0]])
    # ここまで入力
    # 各種パラメタの取得、整形
    overlap = int(df_A.iat[2,0])         #被り許容人数
    place = int(df_A.iat[2,1])           #同時練習数
    training = len(df_N.index)               # 全練習メニュー数の定数のつもり
    member = len(df_A.columns)-3               # 全人数
    df_N = df_N.iloc[:,:member+8]        # d2などが空欄だとdropnaで列を消し飛ばされてずれるので調整
    koma_list = list(range(1,len(df_A.index)+1))    # 練習時間のコマ番号をリストとして獲得。times。
    member_num_list = list(range(1,member+1))  # 全メンバーのリストを獲得。りょーさんコードでpeopleに対応。
    name_dic = {}                              # メンバー名と番号の対応辞書。namedic。
    for i in range(member):
        name_dic[i+1] = df_A.columns[i+3]
    train_dic = {}                             # トレーニング名と番号の辞書。traindic
    for i in range(training):
        train_dic[i+1] = df_N.iloc[i][0]

    train_num_list = []                        # Need由来の5。時間を割きたい練習のみの番号リスト。トリッキー。training。
    for i in range(training):
        if int(df_N.iat[i, date_ids.index(date_id)+1]) == 1:
            train_num_list.append(i+1)

    timezone_list = df_A.iloc[0:len(koma_list),2].astype(str).values          #コマ名リスト。timezone
    # Need由来の４。参加者データを0と1で表現してした配列。履修者名簿。N_np。
    arr_N =  df_N.drop(df_N.columns[[0,1,2,3,4,5,6,7]],axis=1).astype("int").values
    # Attend由来。出席データを０と１で表して配列化したもの。出席者名簿。A_np。
    arr_A = df_A.drop(df_A.columns[[0,1,2]],axis=1).astype("int").values


    # ここまでデータ整理
    # ここからPulpによる最適化
    m = pulp.LpProblem("bestpractice", pulp.LpMaximize)
    x = pulp.LpVariable.dicts('X', (member_num_list, train_num_list, koma_list), 0, 1, pulp.LpInteger)#tコマにiさんがj練習をするかどうか
    y = pulp.LpVariable.dicts('Y', (train_num_list, koma_list), 0, 1, pulp.LpInteger)#tコマにj練習をするかどうか
    m += pulp.lpSum(x[i][j][t] for i in member_num_list for j in train_num_list for t in koma_list ), "TotalPoint"
    #制約
    for t in koma_list:             #「１」練習はまとめて4つまで　t期にする練習全部足したらw以下に
        m += pulp.lpSum(y[j][t] for j in train_num_list) <= place              
    for j in train_num_list:        #「２」同じ練習は1回まで　jの練習に対して全期分足したら1以下に    
        m += pulp.lpSum(y[j][t] for t in koma_list) <= 1            
    for i in member_num_list:       #「３」やる練習にしか参加できない　参加しないのはあり    
        for j in train_num_list:
            for t in koma_list:
                m += x[i][j][t] <= y[j][t]
    for i in member_num_list:       #「４」必要な練習しかしない　必要な練習でもやらないのはあり
        for j in train_num_list:
            for t in koma_list:
                m += x[i][j][t] <= arr_N[j-1][i-1]
    for i in member_num_list:       #「５」いる人しか参加しない　いる人で参加しないのはあり
        for j in train_num_list:
            for t in koma_list:
                m += x[i][j][t] <= arr_A[t-1][i-1]
    for i in member_num_list:       #「６」tコマで1人ができる練習は1つまで
        for t in koma_list:
            m += pulp.lpSum(x[i][j][t] for j in train_num_list) <= 1
    for t in koma_list:             #「７」各期の参加人数はいる人でやる練習に参加可の人の合計よりK人少ない人数以上必要
        m += pulp.lpSum(x[i][j][t] for i in member_num_list for j in train_num_list) >= pulp.lpSum(arr_N[j-1][i-1]*arr_A[t-1][i-1]*y[j][t] for i in member_num_list for j in train_num_list) - overlap
    m += pulp.lpSum(y[j][t] for j in train_num_list for t in koma_list) == len(train_num_list)#入れた練習は全て採用する

    m.solve()

    # **出力文**

    msg_list = []
    msg_list.append(str(df_A.iat[0,0])+"\n")
    # msg_list.append(str(pulp.LpStatus[m.solve()]))
    msg_list.append("練習数は"+str(len(train_num_list))+"\n")

    msg_list.append("=============処理結果=============\n")
    if pulp.LpStatus[m.solve()] != "Infeasible":
        msg_list.append("練習は入りきった！\n")
        msg_list.append("総練習人数は"+str(round(pulp.value(m.objective)))+"人"+"\n")
    #結果
        msg_list.append("\n=============メニュー=============\n")
        msg_list.append(str(df_A.iat[0,0])+"\n参加者\n"+str(df_A.iat[0,1])+"\n")
        t1 = 0
        j1 = 0
        for t in koma_list:
            tt = 0
            for j in train_num_list:
                if pulp.value(y[j][t]) == 1:
                    if t1 != t:
                        t1 = t
                    if j1 != j:
                        j1 = j
                        tt += 1
                        if tt == 1:
                            msg_list.append("\n"+str(timezone_list[t-1])+"\n")
                        msg_list.append(str(train_dic[j])+"\n")
        msg_list.append("\n\n==============詳細==============")
        # msg_list.append("【詳細】")
        t1 = 0
        j1 = 0
        for t in koma_list:
            tt = 0
            for j in train_num_list:
                if pulp.value(y[j][t]) == 1:
                    if t1 != t:
                        t1 = t
                    if j1 != j:
                        j1 = j
                        tt += 1
                        if tt == 1:
                            msg_list.append("\n\n"+str(timezone_list[t-1])+"\n")
                        msg_list.append(str(train_dic[j])+"\n")
            msg_list.append("【被り】\n")
            for j in train_num_list:
                for i in member_num_list:
                    if pulp.value(x[i][j][t] ) != pulp.value(arr_N[j-1][i-1]*arr_A[t-1][i-1]*y[j][t]):
                        msg_list.append(str(name_dic[i])+"　")
            msg_list.append("\n【やることない】\n")
            for i in member_num_list:
                if arr_A[t-1][i-1] == 1:
                    #msg_list.append(tr(pulp.value(pulp.lpSum(x[i][j][t] for j in train_num_list)))
                    if pulp.value(pulp.lpSum(x[i][j][t] for j in train_num_list)) == 0:
                        msg_list.append(str(name_dic[i])+"　")

    else:
        msg_list.append("練習は入り切らなかった．被り人数許容上限="+str(overlap)+",同時練習許容上限="+str(place)+"\n")
        msg_list.append("K(被り人数許容上限)やW(同時練習許容上限)を大きくするか，練習するメニュー減らしてみてね")
    # 出力メッセージの結合表示
    msg=str()
    for i in msg_list:
        msg = msg  + i
    message = bikou+"\n" + msg

    return message

