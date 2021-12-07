from slackbot.bot import respond_to
import plugins.my_input as ip
import plugins.my_calc as cl
# __init__のディレクトリにテストファイルでインポートしたものが放置されているとモジュールエラーが出るので注意

def solver(id):
    k = cl.Param(*ip.readsheet(id))
    # 一回目の計算
    message, failed = k.Calc()

    # 計算不可の場合に優先度の低いメニューを一つ削って再計算する
    cnt = 0                 # 繰り返し計算カウント
    limit = 5               # 繰り返し計算回数の上限
    rejectedlessons = []    # 計算から爪弾きにしたメニュー名のインデックス
    if failed:
        while failed and cnt < limit:
            cnt += 1
            mx = max(k.need_train)
            for i, v in enumerate(k.need_train):
                if v == mx:
                    k.need_train[i] = 0
                    rejectedlessons.append(i)
                    break
            message, failed = k.Calc()  # 再計算

    # 再計算のログを追加する
    if cnt == 0:
        message += "\n練習は入りきった!　\nメニュー棄却（再計算）回数：0"
    elif 0 < cnt and not(failed):
        message += "\nメニュー棄却（再計算）回数："+str(cnt) + "\n"
        message += str(cnt) + "つの練習は入り切らなかった．被り人数許容上限=" + \
            str(k.overlap)+",同時練習許容上限="+str(k.place)+"\n"
        message += "やり直すならばK(被り人数許容上限)やW(同時練習許容上限)を大きくするか，練習するメニューを減らしてみてね"
        for i in range(cnt):
            nn = rejectedlessons[i]
            message += "\n棄却メニュー" + str(i+1)+"：" + k.lessons[nn]
    elif cnt == limit and failed:
        message += "\nメニュー棄却（再計算）回数："+str(cnt)
        message += "\n計算回数の上限に達した."
        for i in range(cnt):
            nn = rejectedlessons[i]
            message += "\n棄却メニュー" + str(i+1)+"：" + k.lessons[nn]
    else:
        message += "\nバグってるよ.システム担当者に連絡してね."
    return message


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
