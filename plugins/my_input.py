'''Googleスプレッドシートからのインプット'''
import pandas as pd
import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials

date_ids = ["d1","d2","d3","d4","d5","d6","d7"]

spreadsheet_key = '1Z5bLTtsBsRnhIKBMXxkk29UPWNBkxElp7HLe5omZ4fI'
SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'plugins/es-spreadsheet-rmsystem-1d49147d5dc7.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE,SCOPES)
gs = gspread.authorize(credentials)
workbook = gs.open_by_key(spreadsheet_key)

def readsheet(id):
  worksheet = workbook.worksheet('df_up')
  df_origin = pd.DataFrame(worksheet.get_all_values())

  date_id = id
  date_index = date_ids.index(date_id)
  # 生のデータからd1(-7)に関するデータ整理のための整形
  # 0全練習　1全名前　2＋index(2)クラス名　9＋index各(3)パラミタ　16+index(4)need
  df_up = df_origin[[0,1,2+date_index, 9+date_index, 16+date_index]]
  df_up = df_up.rename(columns={2+date_index:2, 9+date_index:3, 16+date_index:4})
  df_up = df_up.drop(df_up.index[[0]])
  # 人、レッスン、授業コマの3軸のイメージ
  lessons = df_up.iloc[:,0].values.tolist()
  lessons = [i for i in lessons if i !=""]
  members = df_up.iloc[:,1].values.tolist()
  members = [i for i in members if i !=""]
  class_list = df_up[2].tolist()
  class_list = [i for i in class_list if i != ""] # str型として先にリストにしておく。コマの名前
  need_train = []                        # 時間を割きたい練習のみの番号リスト。ナップザック問題の石id
  for i in range(len(lessons)):
    need_train.append(int(df_up.replace('',0).iat[i, 4]))
  # 香盤表配列arr_N
  df_need = df_origin.drop(df_origin.columns[[range(23)]],axis=1)
  df_need = df_need.drop(df_need.index[[0]])
  arr_N = df_need.drop(df_need.index[range ( len(lessons), len(df_need.index)) ]).replace("",0).astype("int").values
  
  lesson_time = int(df_up.iat[0,3])   # 1コマ当たりの時間（分）.データ整理用
  overlap = int(df_up.iat[1,3])   # かぶり許容人数.
  place = int(df_up.iat[2,3])   # 同時練習数
  datedata = df_up.iat[3,3]   # 日付と場所情報.出力用
  participant = df_up.iat[4,3]   # 参加者列挙.出力用


  df_up[2] = pd.to_datetime(df_up[2])     # 先にclass_listを取得してから型を変換

  # フォーム回答シートを読み込み、出席簿配列arr_Aをまとめる
  
  sheet_name = df_up.iat[5,3]+"_"         # シート名の末尾が数字だとエラー.w01_等にアクセス
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
  return members,class_list,lessons,need_train,arr_N,arr_A,overlap,place,datedata,participant