'''bestpractice組合せ最適化'''

import pulp

class Param:
    def __init__(self,members,class_list,lessons,need_train,arr_N,arr_A,overlap,place,datedata,participant):
        self.members    = members       # 全現場関係者のstrリスト。
        self.class_list = class_list    # その日のコマの開始時刻のstrリスト。
        self.lessons    = lessons       # 全メニュー名のstrリスト。
        self.need_train = need_train    # 要求メニューのintリスト。要求されるメニューのフィルタ。
        self.arr_N      = arr_N         # 香盤表の2次元numpy配列。indexはメニュー名（lessons）、columnは人(members)。
        self.arr_A      = arr_A         # 出席簿の2次元numpy配列。indexはコマ（class_list）、columunは人(members)。
        self.overlap    = overlap       # 制約式用のかぶり人数上限int。
        self.place      = place         # 制約式用の同時練習数int。
        self.datedata   = datedata      # 日付と場所str。出力用雑データ。
        self.participant= participant   # 参加者名簿str。出力用雑データ。

    def Calc(self):
        # 前処理 

        member_num_list = list(range(1,len(self.members)+1))     # メンバーのキー番号リスト。Pulpは1から参照することが多いため。
        class_num_list = list(range(1,len(self.class_list)+1)) # コマのインデックスのリスト。1~
        train_num_list = []                        # 時間を割きたい練習のフィルタリング。ナップザック問題の石
        for i in range(len(self.lessons)):
            if self.need_train[i] != 0:
                train_num_list.append(i+1)

        # 最適化
        
        m = pulp.LpProblem("bestpractice", pulp.LpMaximize)
        x = pulp.LpVariable.dicts('X', (member_num_list, train_num_list, class_num_list), 0, 1, pulp.LpInteger)#tコマにiさんがj練習をするかどうか
        y = pulp.LpVariable.dicts('Y', (train_num_list, class_num_list), 0, 1, pulp.LpInteger)#tコマにj練習をするかどうか
        m += pulp.lpSum(x[i][j][t] for i in member_num_list for j in train_num_list for t in class_num_list ), "TotalPoint"
        #制約
        for t in class_num_list:            #「１」練習はまとめて4つまで　t期にする練習全部足したらw以下に
            m += pulp.lpSum(y[j][t] for j in train_num_list) <= self.place              
        for j in train_num_list:            #「２」同じ練習は1回まで　jの練習に対して全期分足したら1以下に    
            m += pulp.lpSum(y[j][t] for t in class_num_list) <= 1            
        for i in member_num_list:           #「３」やる練習にしか参加できない　参加しないのはあり    
            for j in train_num_list:
                for t in class_num_list:
                    m += x[i][j][t] <= y[j][t]
        for i in member_num_list:           #「４」必要な練習しかしない　必要な練習でもやらないのはあり
            for j in train_num_list:
                for t in class_num_list:
                    m += x[i][j][t] <= self.arr_N[j-1][i-1]
        for i in member_num_list:           #「５」いる人しか参加しない　いる人で参加しないのはあり
            for j in train_num_list:
                for t in class_num_list:
                    m += x[i][j][t] <= self.arr_A[t-1][i-1]
        for i in member_num_list:           #「６」tコマで1人ができる練習は1つまで
            for t in class_num_list:
                m += pulp.lpSum(x[i][j][t] for j in train_num_list) <= 1
        for t in class_num_list:            #「７」各期の参加人数はいる人でやる練習に参加可の人の合計よりK人少ない人数以上必要
            m += pulp.lpSum(x[i][j][t] for i in member_num_list for j in train_num_list) >= pulp.lpSum(self.arr_N[j-1][i-1]*self.arr_A[t-1][i-1]*y[j][t] for i in member_num_list for j in train_num_list) - self.overlap
        m += pulp.lpSum(y[j][t] for j in train_num_list for t in class_num_list) == len(train_num_list)#入れた練習は全て採用する
        # 演算
        m.solve()

        # **出力文**
        msg = str()
        # msg += (str(pulp.LpStatus[m.solve()])+"\n")
        msg += (self.datedata+"\n")
        msg += ("入った練習数は"+str(len(train_num_list))+"\n")
        msg += ("===========処理結果===========\n")
        infeasible = (pulp.LpStatus[m.solve()] == "Infeasible")
        if infeasible:    # Infeasibleは実行不可能の意。パラメタ調整のため抜ける
            msg += ("練習は入り切らなかった．被り人数許容上限="+str(self.overlap)+",同時練習許容上限="+str(self.place)+"\n")
            msg += ("K(被り人数許容上限)やW(同時練習許容上限)を大きくするか，練習するメニュー減らしてみてね")
            return msg,infeasible
           
        
        # msg += ("練習は入りきった！\n")
        msg += ("総練習人数は"+str(round(pulp.value(m.objective)))+"人"+"\n\n")
        msg += ("===========メニュー===========\n")
        msg += (self.datedata+"\n"+ "参加者\n"+self.participant+"\n")
        t1 = 0
        j1 = 0
        for t in class_num_list:
            msg += "\n"
            tt = 0
            for j in train_num_list:
                if pulp.value(y[j][t]) == 1:
                    if t1 != t:
                        t1 = t
                    if j1 != j:
                        j1 = j
                        tt += 1
                        if tt == 1:
                            msg += (self.class_list[t-1]+"\n")
                        msg += (self.lessons[j-1]+"\n")
        
        msg +="\n" + ("============詳細============\n")
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
                            msg += (self.class_list[t-1]+"\n")
                        msg += (self.lessons[j-1]+"\n")
            msg += ("【被り】\n")
            for j in train_num_list:
                for i in member_num_list:
                    if pulp.value(x[i][j][t] ) != pulp.value(self.arr_N[j-1][i-1]*self.arr_A[t-1][i-1]*y[j][t]):
                        msg += (self.members[i-1]+"　")
            msg += ("\n")
            msg += ("【やることない】\n")
            for i in member_num_list:
                if self.arr_A[t-1][i-1] == 1:
                    if pulp.value(pulp.lpSum(x[i][j][t] for j in train_num_list)) == 0:
                        msg += (self.members[i-1]+"　")
            msg += ("\n\n")

        return msg,infeasible
