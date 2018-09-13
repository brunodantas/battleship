import tkinter as tk
import random
import os.path
import time
import sys
import copy
import gc
import statistics
import math


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("greedy")
        self.geometry('{}x{}'.format(330, 500))
        self.resizable(width=False, height=False)
        self.canvas = tk.Canvas(self, width=260, height=500, borderwidth=0, highlightthickness=0)
        self.canvas.grid(row=0,column=0,sticky="w")
        self.rows = 10
        self.columns = 10
        self.cellwidth = 20
        self.cellheight = 20



        self.rect = {}

        frame = tk.Frame(self, width=1000)
        frame.grid(row=0,column=1, sticky="n",pady=50)
        label1=tk.Label(frame, text="jogador").grid(row=1,column=0, sticky="w",pady=10)

        self.p1=1

        rbutton1=tk.Radiobutton(frame, text="P1", variable=self.p1, value=1, command = self.player1)
        rbutton1.grid(row=2,column=0, sticky="w")
        rbutton2=tk.Radiobutton(frame, text="P2", variable=self.p1, value=2, command = self.player2)
        rbutton2.grid(row=3,column=0, sticky="w")
        rbutton1.select()
        rbutton2.deselect()

        label2=tk.Label(frame, text="delay").grid(row=4,column=0, sticky="w",pady=5)

        self.e = tk.Entry(frame, text="100", width=5)
        self.e.grid(row=5,column=0, sticky="w")

        self.e.insert(0, "100")

        label2=tk.Label(frame, text="partidas").grid(row=6,column=0, sticky="w",pady=5)


        self.e2 = tk.Entry(frame, text="", width=5)
        self.e2.grid(row=7,column=0, sticky="w")

        self.e2.insert(0, "1")


        b = tk.Button(frame, text="OK",command=self.run)
        b.grid(row=8,column=0, sticky="w",pady=10)


        self.label3=tk.Label(frame)
        self.label3.grid(row=9,column=0, sticky="w",pady=10)

        self.draw_board()


    def player1(self):
        self.p1 = 1


    def player2(self):
        self.p1 = 2


    def run(self): 
        self.enemy_board = [[0 for x in range(10)] for y in range(10)] 
        self.my_board = [[0 for x in range(10)] for y in range(10)] 
        self.delay = int(self.e.get())
        matches = int(self.e2.get())
        self.draw = 0
        self.wins = 0
        self.loses = 0
        self.occur_matrix = [[0 for x in range(10)] for y in range(10)]
        min = 200
        max = 0
        self.plays = []
        for i in range(matches):
            self.newgame()

            if self.draw:
                self.label3['text'] = '{0} - {1}'.format(self.wins,self.loses)

            if self.wins > 0:
                if self.plays[self.wins-1] < min:
                    min = self.plays[self.wins-1]
                if self.plays[self.wins-1] > max:
                    max = self.plays[self.wins-1]

        self.label3['text'] = '{0} - {1}'.format(self.wins,self.loses)

        print('\n\nmax = '+str(max))
        print('min = '+str(min))
        if self.plays != []:
            print('media = '+str(statistics.mean(self.plays)))
            print('mediana = '+str(statistics.median(self.plays)))
        print(sorted(self.plays))

        f = open('hist.txt', 'w+')
        f.write(str(self.plays))
        f.close()


    def newgame(self):
        self.init()
        self.set_pieces()
        self.gameover = 0
        self.nextplay = 1
        self.atk = self.attack
        if self.p1 == 1:
            self.atk = self.firstattack
        self.lastatk = (0,0)
        self.suggest = (-1,-1)
        self.initsearchlist()
        self.hitlist = []
        self.direction = 0
        self.hit = 0
        self.hits = 0
        #self.missingpieces = []
        self.largest = 5
        self.sinklist = []
        self.searches = 0
        gc.collect()
        self.gameloop()

        # count = 0
        # gc.collect()
        # oo = gc.get_objects()
        # for o in oo:
        #     count += 1
        #     if getattr(o, "__class__", None):
        #         name = o.__class__.__name__

        #         print ("Class  :", name, "...")

        # print("count: ",count)


    def gameloop(self):
        while self.gameover == 0:
            a = 0
            while a == 0:
                self.after(self.delay)
                a = self.check()
            if a == -1:
                break
            self.atk()
            if(self.draw):
                self.update()
        if(self.draw):
            self.update()


    def getplay(self,lines):
        play = lines[0][7]

        for i in range(len(lines[0])-8):        
            if lines[0][i+8] != '\n':
                play += lines[0][i+8]

        try:
            play = int(play)
        except:
            return 0

        return play


    def gg(self):
        self.gameover = 1
        x,y = self.lastatk
        self.enemy_board[x][y] = 3
        if(self.draw):
            self.draw_enemy(x,y)
        self.wins += 1
        self.plays.append(self.nextplay)



    def check(self):
        if self.atk == self.firstattack:
            return 1

        with open('partida.txt') as f:
            lines = f.readlines()

        if not lines:
            return 0

        if lines[0] == 'game over':
            if self.nextplay < 5:
                return 0
            else:
                self.gg()
                return -1

        play = self.getplay(lines)
        if play == 1 and self.nextplay > 5:
            self.gg()
            return -1

        if play == self.nextplay:

            x,y = self.lastatk
            self.enemy_board[x][y] = self.check_response(lines[1])
            if(self.draw):
                self.draw_enemy(x,y)

            cx = lines[2][7]
            cy = lines[2][8]
            if lines[2][9] != '\n':
                cy += lines[2][9]
            y = int(cy) - 1
            x = ord(cx) - 65
            
            self.check_att(x,y)
            if(self.draw):
                self.draw_mine(x,y)
            
            return 1

        else:
            return 0


    def check_att(self,x,y):
        if self.my_board[x][y] == 1:
            self.nextresponse = "hit"
            for p in self.pieces:
                for s in p.squares:
                    if s == (x,y):
                        p.squares.remove(s)
                        if(p.squares == []):
                            self.nextresponse = "sink {0}".format(p.size)
                            self.pieces.remove(p)
            if self.pieces == []:
                self.gameover = 1
                self.loses += 1
                self.send('game over')
                self.after(10)

        else:
            self.nextresponse = "miss"
            self.my_board[x][y] = 2
        self.nextplay += 1


    def send(self,msg):
        f = open('partida.txt', 'w+')
        f.write(msg)
        f.close()


    def draw_mine(self,x,y):
        row = x+10
        col = y+10
        item_id = self.rect[row,col]
        if self.my_board[x][y]==1:
            self.canvas.itemconfig(item_id, fill="red")
        if self.my_board[x][y]==2:
            self.canvas.itemconfig(item_id, fill="blue")


    def draw_enemy(self,x,y):
        item_id = self.rect[x,y]
        if self.enemy_board[x][y]==1:
            self.canvas.itemconfig(item_id, fill="red")
        if self.enemy_board[x][y]==2:
            self.canvas.itemconfig(item_id, fill="blue")
        if self.enemy_board[x][y]==3:
            self.canvas.itemconfig(item_id, fill="black")


    def check_response(self,line):
        if line == '-\n':
            return 0
        if line == 'hit\n':
            self.hits += 1
            self.hit = 1
            self.hitlist.append(self.lastatk)
            
            if self.sinklist != []:
                self.removesink()

            return 1

        if line == 'miss\n':
            return 2

        else:

            size = int(line[5])
            self.hits -= (size - 1)

            self.hit = 1
            self.sinklist.append((size,self.lastatk))

            self.removesink()
            #self.missingpieces.append(size)
            self.enemy_pieces.remove(size)

            if size == self.largest:
                self.largest = self.enemy_pieces[0]
            return 3


    def attack(self):
        if self.gameover == 1:
            return

        (x,y) = self.choose_target()
        position = "{0}{1}".format((chr(65+x)),y+1)
        msg = 'jogada {0}\n{1}\nattack {2}\n'.format(self.nextplay,self.nextresponse,position)
        self.send(msg)
        self.lastatk = (x,y)
        self.nextplay += 1


    def initsearchlist(self):
        self.searchlist = []
        self.searchlist2 = []
        a = random.randint(0,1)
        for x in range(10):
            for y in range(10):
                if (x+y)%2 == a:
                    self.searchlist.append((x,y))
                else:
                    self.searchlist.append((x,y))

        # searchlist3 = []
        # num = random.randint(0,2)
        # for x in range(10):
        #     for y in range(10):
        #         if (x+y)%3 == num:
        #             searchlist3.append((x,y))

        # searchlist4 = []
        # num = random.randint(0,1)
        # for x in range(10):
        #     for y in range(10):
        #         if (x+y)%2 == num:
        #             searchlist4.append((x,y))

        #self.searchlist = [searchlist]


    def search(self,l):
        # if self.searchlist != []:
        #     b = len(self.searchlist)
        #     if b == 1:
        #         a = 0
        #     else:
        #         a = random.randint(0,b-1)
        #     pos = self.searchlist[a]
        #     del self.searchlist[a]

        # elif self.searchlist2 != []:
        #     b = len(self.searchlist2)
        #     if b == 1:
        #         a = 0
        #     else:
        #         a = random.randint(0,b-1)
        #     pos = self.searchlist2[a]
        #     del self.searchlist2[a]

        # else:

        if self.nextplay < 1:
            a = random.randint(0,len(self.searchlist)-1)
            pos = self.searchlist.pop(a)
            return pos

        if len(self.searchlist) == 1:
            pos = self.searchlist.pop(0)
            return pos

        best = -1
        bestuse = -1
        l2 = []
        pieces = len(self.enemy_pieces)
        early = pieces > 1
        count = 0
        average = 0

        if l==[]:
            if early:
                    l = self.probs()
            else:
                    l = self.probs()
        
        if self.searchlist == []:
            self.searchlist = self.searchlist2

        total = 0
        for i in self.enemy_pieces:
            total += i

        total = total//2

        for (x,y) in self.searchlist:
            if self.enemy_board[x][y] == 0 and l[x][y] > 0:
                if l[x][y] > best:
                    best = l[x][y]
                    pos = (x,y)

        #use = 4 #- (self.nextplay//40)
        for x,y in self.searchlist:
            if self.enemy_board[x][y] == 0:
                if l[x][y] > total:
                    l2.append((x,y))

                # try:
                #     self.searchlist.remove((x,y))
                # except ValueError:
                #     pass
            # elif self.nextplay > 50 and u > 2:
            #     l2.append((x,y))
            # elif self.nextplay > 75 and u > 1:
            #     l2.append((x,y))  

        self.searches += 1

        # print(best)
        # print(bestuse)
        # print(l2)

        # print("\n\n")

        

        if l2 == []:
            # print(self.nextplay)
            # print(self.searchlist)
            # for a in l:
            #     print(a)
            # print("\n\n")
            # for a in self.enemy_board:
            #     print(a)
            self.suggest_atk(pos,l)
            return pos

        b = len(l2)
        a = 0
        if b > 1:
            a = random.randint(0,b-1)
        pos = l2[a]

        self.searchlist.remove(pos)

        self.suggest_atk(pos,l)

        return pos

    
    def suggest_atk(self,pos,l):
        options = []

        x,y = pos
        if x+1 < 10:
            options.append((x+1,y))
        if x-1 > -1:
            options.append((x-1,y))
        if y+1 < 10:
            options.append((x,y+1))
        if y-1 > -1:
            options.append((x,y-1))

        best = 0
        for x,y in options:
            if l[x][y] > best:
                best = l[x][y]
                pos = x,y

        self.suggest = pos



        # if self.searchlist != []:
        #     if self.searchlist[0] == []:
        #         self.searchlist.remove(self.searchlist[0])
        #         return self.search(l)
        #     a = random.randint(0,len(self.searchlist[0])-1)
        #     pos = self.searchlist[0][a]
        #     del self.searchlist[0][a]
        #     x,y = pos
        #     if self.enemy_board[x][y] == 0 and l[x][y] > 2:
        #         return x,y
        #     else:
        #         return self.search(l)

        # else:
        #     pos = (-1,-1)
        #     best = 0
        #     for x in range(10):
        #         for y in range(10):
        #             if l[x][y] > best:
        #                 best = l[x][y]
        #                 pos = x,y
        #     return pos




    def usefulness(self,x,y):
        count = 0
        f1 = 0
        f2 = 0
        f3 = 0
        f4 = 0
        if x+1 < 10:
            if self.enemy_board[x+1][y] == 0:
                count+=5
                f1 = 1
        else:
            count+=6

        if x-1 > -1:
            if self.enemy_board[x-1][y] == 0:
                count+=5
                f2 = 1
        else:
            count+=6

        if y+1 < 10:
            if self.enemy_board[x][y+1] == 0:
                count+=5
                f3 = 1
        else:
            count+=6

        if y-1 > -1:
            if self.enemy_board[x][y-1] == 0:
                count+=5
                f4 = 1
        else:
            count+=6

        if f1 and f3 and self.enemy_board[x+1][y+1] == 0:
            count+=1
        if f1 and f4 and self.enemy_board[x+1][y-1] == 0:
            count+=1
        if f2 and f3 and self.enemy_board[x-1][y+1] == 0:
            count+=1
        if f2 and f4 and self.enemy_board[x-1][y-1] == 0:
            count+=1

        return count



    def destrooy(self):
        if self.suggest != (-1,-1):
            pos = self.suggest
            self.suggest = (-1,-1)
            if pos[0] == self.hitlist[0][0]:
                self.direction = 1
            else:
                self.direction = 0
            return pos

        options = self.getadjacency()

        if len(self.hitlist) == 1:
            self.direction = not self.direction
            options = options + self.getadjacency()
        
        self.hit = 0

        pos = self.choose_option(options)

        if pos == (-1,-1):
            self.direction = not self.direction
            
            options = self.getadjacency()

            pos = self.choose_option(options)

            if pos == (-1,-1):
                return self.search([])

        if len(self.hitlist) == 1:
            if pos[0] == self.hitlist[0][0]:
                self.direction = 1
            else:
                self.direction = 0

        try:
            self.searchlist.remove(pos)
        except ValueError:
            pass

        return pos



    # def destrooy(self):
    #     if self.hit == 1 and len(self.hitlist) == 1:
    #         self.direction = random.randint(0,1)

    #     self.hit = 0

    #     l = self.greedy()

    #     # if len(self.enemy_pieces) == 1 and self.hit == 0:
    #     #     best = 0
    #     #     for x in range(10):
    #     #         for y in range(10):
    #     #             if l[x][y] > best:
    #     #                 best = l[x][y]
    #     #                 pos = x,y


    #     options = self.getadjacency()

    #     pos = self.choose_option(options,l)

    #     if pos == (-1,-1):
    #         self.direction = not self.direction
            
    #         options = self.getadjacency()

    #         pos = self.choose_option(options,l)
            
    #         if pos == (-1,-1):
    #             return self.search(l)        
    #     return pos


    def choose_option(self,options):
        # choice = (-1,-1)
        # size = len(options)
        # for i in range(0,size):
        #     a = random.randint(0,len(options)-1)
        #     x,y = options[a]
        #     del options[a]
        #     if self.enemy_board[x][y] == 0 and l[x][y] > 0:
        #         choice = (x,y)
        #         break

        # return choice

        #l2 = []
        choice = (-1,-1)
        best = -1
        for x,y in options:
            v = self.usefulness2(x,y)
            if self.enemy_board[x][y] == 0 and v > best:
                best = v
                choice = x,y

        # if best == -1:
        #     print(self.hits)
        #     print(self.enemy_pieces)
        #     for a in self.enemy_board:
        #         print(a)
        #     self.after(10000)
        #     print("\n\n")

        # for x,y in options:
        #         if self.enemy_board[x][y] == 0 and l[x][y] > 0:
        #             l2.append((x,y))
        #             # if self.usefulness(x,y) > 1:
        #             #     l2.append((x,y))
        #             # elif l[x][y] == best:
        #             #     l2.append((x,y))

        # if l2 != []:
            # b = len(l2)
            # a = 0
            # if b > 1:
            #     a = random.randint(0,b-1)
            # choice = l2[a]

        return choice


    def usefulness2(self,x,y):
        if len(self.hitlist) == 1:
            return self.usef2(x,y,0) + self.usef2(x,y,1)

        return self.usef2(x,y,self.direction)


    def usef2(self,x,y,h):
        value = 0

        if h == 0:
            i = x
            while i < 10 and self.enemy_board[i][y] == 0:
                value += 1
                i += 1

            i = x
            while i >= 0 and self.enemy_board[i][y] == 0:
                value += 1
                i -= 1

        else:
            i = y
            while i < 10 and self.enemy_board[x][i] == 0:
                value += 1
                i += 1

            i = y
            while i >= 0 and self.enemy_board[x][i] == 0:
                value += 1
                i -= 1

        return value

        
    def getadjacency(self):
        options = []
        for pos in self.hitlist:
            x,y = pos
            if self.direction == 0:
                if x+1 < 10:
                    options.append((x+1,y))
                if x-1 > -1:
                    options.append((x-1,y))
            else:
                if y+1 < 10:
                    options.append((x,y+1))
                if y-1 > -1:
                    options.append((x,y-1))

        return options



    def choose_target(self):
        return self.search_and_destroy()




    # def choose_target(self):
    #     if len(self.enemy_pieces) < 3 and self.nextplay > 50 and self.hitlist != []:
    #         return self.killemall()
    #     else:
    #         return self.search_and_destroy()


    def killemall(self):
        l = self.probs2()
        l2 = []
        best = 0
        pos = (-1,-1)
        for x in range(10):
            for y in range(10):
                if l[x][y] > best:
                    best = l[x][y]

        for x in range(10):
            for y in range(10):
                if l[x][y] == best:
                    l2.append((x,y))

        x = random.randint(0,len(l2)-1)
        x,y = l2[x]
        while self.enemy_board[x][y] != 0:
            x = random.randint(0,len(l2)-1)
            x,y = l2[x]
        return x,y


    # def choose_target(self):
    #     if len(self.enemy_pieces) < 3 or self.nextplay > 63:
    #         l = self.greedy()
    #         pos = self.search_and_destroy()
    #         i = 0
    #         while not (pos in l):
    #             pos = self.search_and_destroy()
    #             i += 1
    #             if(i==1000):
    #                 break
    #         return pos

    #     else:
    #         return self.search_and_destroy()


    def search_and_destroy(self):
        if self.hitlist == []:
            return self.search([])
        else:
            return self.destrooy()


    def fitmat(self):
        fitmatrix = [[0 for x in range(10)] for y in range(10)]


    def greedy(self):
        best = 0
        self.occur_matrix = self.probs()
        l = []

        return self.occur_matrix

        # for x in range(10):
        #     for y in range(10):
        #         if occur_matrix[x][y] > 0:
        #             l.append((x,y))

        # l = []
        # occur_matrix = self.probs()

        # for x in range(10):
        #     for y in range(10):
        #         if occur_matrix[x][y] > 1:
        #             l.append((x,y))

        #return l


    def probs(self):
        for x in range(10):
            for y in range(10):
                self.occur_matrix[x][y] = 0
        board = copy.deepcopy(self.enemy_board)      
        #miss = copy.deepcopy(self.missingpieces)
        #self.fitonred(miss,board,occur_matrix,self.runprobs)
        self.runprobs(self.occur_matrix,board)

        return self.occur_matrix


    def probs2(self):
        for x in range(10):
            for y in range(10):
                self.occur_matrix[x][y] = 0
        board = copy.deepcopy(self.enemy_board)      
        #miss = copy.deepcopy(self.missingpieces)
        # self.fitonred(miss,board,occur_matrix,self.runprobs2)
        self.runprobs2(self.occur_matrix,board)

        return self.occur_matrix


    def runprobs(self,occur_matrix,board):
        remaining = list(self.enemy_pieces)
        hits = self.hits
        self.trypieces(remaining,board,hits,[],self.occur_matrix)


    def trypieces(self,remaining,board,h,pieces,occur_matrix):
        hits = h

        for i in remaining:
            p = Piece(i)
            for x in range(10):
                for y in range(10):
                    if(self.canfit(p,1,(x,y),board)):
                        hits = self.fitpiece(p,1,(x,y),board,hits)
                        value = 1
                        if hits == 0:
                            for x,y in p.squares:
                                if board[x][y] == 10:
                                    self.occur_matrix[x][y] += value
                            hits = self.removepiece(p,board,hits)

            for x in range(10):
                for y in range(10):
                    if(self.canfit(p,0,(x,y),board)):
                        hits = self.fitpiece(p,0,(x,y),board,hits)
                        value = 1
                        if hits == 0:
                            for x,y in p.squares:
                                if board[x][y] == 10:
                                    self.occur_matrix[x][y] += value
                            hits = self.removepiece(p,board,hits)     


    def runprobs2(self,occur_matrix,board):
        remaining = list(self.enemy_pieces)
        hits = self.hits
        self.trypieces2(remaining,board,hits,[],self.occur_matrix)


    def removesink(self):
        if self.sinklist == []:
            return 0

        l = []
        l2 = []

        size,(a,b) = self.sinklist.pop(0)

        for x,y in self.hitlist:
            v = abs(a-x)
            if v > 0 and b == y and v < size:
                l.append((x,y))

            v = abs(b-y)
            if v > 0 and a == x and v < size:
                l2.append((x,y))


        if len(l) == size - 1 and len(l2) == size - 1:

            success = self.removesink()
            self.sinklist.append((size,(a,b)))

            if not success:
                return 0
            else:
                return self.removesink()


        if len(l) == size - 1:
            self.enemy_board[a][b] = 3
            for x,y in l:
                self.enemy_board[x][y] = 3
                self.hitlist.remove((x,y))
            return 1


        if len(l2) == size - 1:
            self.enemy_board[a][b] = 3
            for x,y in l2:
                self.enemy_board[x][y] = 3
                self.hitlist.remove((x,y))
            return 1

        self.sinklist.append((size,(a,b)))
        return 0



    def fitonred(self,pieces,board,occur_matrix,function):
        if pieces == []:
            function(self.occur_matrix,board)
            return 0

        p = Piece(pieces[0])
        pieces.pop(0)

        for x in range(10):
            for y in range(10):
                if self.canfitonred(p,1,(x,y),board):
                    self.fitred(p,1,(x,y),board)
                    if self.fitonred(pieces,board,self.occur_matrix,function) == 1:
                        return 1
                    else:
                        self.removered(p,board)

        for x in range(10):
            for y in range(10):
                if self.canfitonred(p,0,(x,y),board):
                    self.fitred(p,0,(x,y),board)
                    if self.fitonred(pieces,board,self.occur_matrix,function) == 1:
                        return 1
                    else:
                        self.removered(p,board)
        return 0


    def removered(self,piece,board):
        for x,y in piece.squares:
            board[x][y] = 1

        piece.squares = []



    def fitred(self,p,hor,pos,board):
        x,y = pos
        if hor:
            for i in range(p.size):
                board[x+i][y] = 3
                p.squares.append((x+i,y))

        else:
            for i in range(p.size):
                board[x][y+i] = 3
                p.squares.append((x,y+i))


    def canfitonred(self,p,hor,pos,board):
        x,y = pos

        if hor:
            if p.size + x > 9:
                return 0

            for i in range(p.size):
                if board[x+i][y] != 1:
                    return 0

        else:
            if p.size + y > 9:
                return 0

            for i in range(p.size):
                if board[x][y+i] != 1:
                    return 0

        return 1




    def trypieces2(self,remaining,board,h,pieces,occur_matrix):
        hits = h
        if remaining == []:
            if hits == 0:
                value = 1

                for p in pieces:
                    for x,y in p.squares:
                        if board[x][y] == 10:
                            self.occur_matrix[x][y] += value
            return

        p = Piece(remaining[0])
        remaining.remove(p.size)
        pieces.append(p)

        for x in range(10):
            for y in range(10):
                if(self.canfit(p,1,(x,y),board)):
                    hits = self.fitpiece(p,1,(x,y),board,hits)
                    self.trypieces2(remaining,board,hits,pieces,self.occur_matrix)
                    hits = self.removepiece(p,board,hits)

        for x in range(10):
            for y in range(10):
                if(self.canfit(p,0,(x,y),board)):
                    hits = self.fitpiece(p,0,(x,y),board,hits)
                    self.trypieces2(remaining,board,hits,pieces,self.occur_matrix)
                    hits = self.removepiece(p,board,hits)      

        pieces.remove(p)
        remaining.append(p.size)


    def removepiece(self,piece,board,h):
        hits = h
        for x,y in piece.squares:
            board[x][y] -= 10

            if board[x][y] == 1:
                    hits += 1

        piece.squares = []
        return hits
    

    def fitpiece(self,p,hor,pos,board,h):
        x,y = pos
        hits = h

        if hor:
            for i in range(p.size):
                p.squares.append((x+i,y))

                if board[x+i][y] == 1:
                    hits -= 1

                board[x+i][y] += 10

        else:
            for i in range(p.size):
                p.squares.append((x,y+i))

                if board[x][y+i] == 1:
                    hits -= 1

                board[x][y+i] += 10

        return hits


    def canfit(self,p,hor,pos,board):
        x,y = pos

        if hor:
            if p.size + x > 9:
                return 0

            for i in range(p.size):
                if board[x+i][y] >= 2:
                    return 0

        else:
            if p.size + y > 9:
                return 0

            for i in range(p.size):
                if board[x][y+i] >= 2:
                    return 0

        return 1


    def firstattack(self):
        self.atk = self.attack

        (x,y) = self.choose_target()
        position = "{0}{1}".format((chr(65+x)),y+1)
        msg = 'jogada 1\n-\nattack {}\n'.format(position)
        f = open('partida.txt', 'w+')
        f.write(msg)
        f.close()
        self.lastatk = (x,y)
        self.nextplay += 1


    def init(self):
        for x in range(0,10):
            for y in range(0,10):
                self.enemy_board[x][y] = 0
                self.my_board[x][y] = 0

        self.pieces = []

        if self.draw:
            self.draw_board()


    def draw_board(self):
        offset1 = 30
        offset2 = 280

        for column in range(10):
            label = self.canvas.create_text(column*self.cellwidth + offset1, 10, anchor="nw")
            self.canvas.itemconfig(label,text=str(column+1))

            label = self.canvas.create_text(10, column*self.cellwidth + offset1, anchor="nw")
            self.canvas.itemconfig(label,text=chr(column+65))
            
            for row in range(10):
                x1 = column*self.cellwidth + offset1
                y1 = row * self.cellheight + offset1
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.rect[row,column] = self.canvas.create_rectangle(x1,y1,x2,y2, fill="white", tags="rect")


        for column in range(10):
            label = self.canvas.create_text(column*self.cellwidth + offset1, 260, anchor="nw")
            self.canvas.itemconfig(label,text=str(column+1))

            label = self.canvas.create_text(10, column*self.cellwidth + offset2, anchor="nw")
            self.canvas.itemconfig(label,text=chr(column+65))

            
            for row in range(10):
                x1 = column*self.cellwidth + offset1
                y1 = row * self.cellheight + offset2
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.rect[row+10,column+10] = self.canvas.create_rectangle(x1,y1,x2,y2, fill="white", tags="rect")


    def set_pieces(self):
        sizes = [5,4,3,3,2]
        self.enemy_pieces = [5,4,3,3,2]

        for i in range(5):
            self.pieces.append(self.set_piece(sizes[i]))

            for j in range(sizes[i]):
                row,col = self.pieces[i].squares[j]
                self.my_board[row][col] = 1
                item_id = self.rect[row+10,col+10]
                if self.draw:
                    self.canvas.itemconfig(item_id, fill="gray")


    # def set_piece(self,size):

    #     p = random.randint(0,1)
    #     x = random.randint(0,9)
    #     y = random.randint(0,9)

    #     piece = Piece(size)

    #     if p:
    #         if (x + size) > 9:
    #             return self.set_piece(size)

    #         for i in range(x,x+size):
    #             piece.squares.append((i,y))

    #             if(self.my_board[i][y]==1):
    #                 return self.set_piece(size)

    #     else:
    #         if (y + size) > 9:
    #             return self.set_piece(size)

    #         for i in range(y,y+size):
    #             piece.squares.append((x,i))

    #             if(self.my_board[x][i]==1):
    #                 return self.set_piece(size)

    #     return piece


    def set_piece(self,size):

        p = random.randint(0,1)
        x = random.randint(0,9)
        y = random.randint(0,9)

        piece = Piece(size)

        if p:
            if (x + size) > 9:
                return self.set_piece(size)

            for i in range(x,x+size):
                piece.squares.append((i,y))

                if(self.my_board[i][y]==1):
                    return self.set_piece(size)

        else:
            if (y + size) > 9:
                return self.set_piece(size)

            for i in range(y,y+size):
                piece.squares.append((x,i))

                if(self.my_board[x][i]==1):
                    return self.set_piece(size)

        if self.adjpieces(piece,p):
            return self.set_piece(size)

        return piece


    def adjpieces(self,piece,hor):
        if hor:
            x,y = piece.squares[0]
            if x-1 > -1:
                if self.my_board[x-1][y] == 1:
                    return 1

            x,y = piece.squares[-1]
            if x+1 < 10:
                if self.my_board[x+1][y] == 1:
                    return 1

            for x,y in piece.squares:
                if y-1 > -1:
                    if self.my_board[x][y-1] == 1:
                        return 1
                if y+1 < 10:
                    if self.my_board[x][y+1] == 1:
                        return 1

        else:
            x,y = piece.squares[0]
            if y-1 > -1:
                if self.my_board[x][y-1] == 1:
                    return 1

            x,y = piece.squares[-1]
            if y+1 < 10:
                if self.my_board[x][y+1] == 1:
                    return 1

            for x,y in piece.squares:
                if x-1 > -1:
                    if self.my_board[x-1][y] == 1:
                        return 1
                if x+1 < 10:
                    if self.my_board[x+1][y] == 1:
                        return 1

        return 0



class Piece():
    def __init__(self,size):
        self.size = size
        self.squares = []


if __name__ == "__main__":
    app = App()
    app.mainloop()
