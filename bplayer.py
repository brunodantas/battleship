import tkinter as tk
import random
import os.path
import time
import gc
import statistics

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("battleship player")
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

        self.e = tk.Entry(frame, text="500", width=5)
        self.e.grid(row=5,column=0, sticky="w")

        self.e.insert(0, "500")

        label2=tk.Label(frame, text="partidas").grid(row=6,column=0, sticky="w",pady=5)


        self.e2 = tk.Entry(frame, text="", width=5)
        self.e2.grid(row=7,column=0, sticky="w")

        self.e2.insert(0, "1")


        b = tk.Button(frame, text="OK",command=self.run)
        b.grid(row=8,column=0, sticky="w",pady=10)


        self.label3=tk.Label(frame)
        self.label3.grid(row=9,column=0, sticky="w",pady=10)

        self.draw_board()

        #self.redraw(1000)

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
        min = 200
        max = 0
        self.plays = []
        for i in range(matches):
            self.newgame()
            
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


    def newgame(self):
        self.init()
        self.set_pieces()
        self.gameover = 0
        self.nextplay = 1
        self.atk = self.attack
        if self.p1 == 1:
            self.atk = self.firstattack
        self.lastatk = (0,0)
        self.initsearchlist()
        self.hitlist = []
        self.direction = 0
        self.hit = 0
        gc.collect()
        self.gameloop()


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
        self.enemy_board[x][y] = 1
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


    def check_response(self,line):
        if line == '-\n':
            return 0
        if line == 'hit\n':
            self.hit = 1
            self.hitlist.append(self.lastatk)
            return 1
        if line == 'miss\n':
            return 2
        else:
            size = int(line[5])

            del self.hitlist[-(size-1):]
            self.hit = 0

            for i in self.enemy_pieces:
                if i == size:
                    self.enemy_pieces.remove(i)
            return 1


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
        for x in range(10):
            for y in range(10):
                if (x+y)%3 == 1:
                    self.searchlist.append((x,y))
                else:
                    self.searchlist2.append((x,y))


    def search(self):
        if self.searchlist != []:
            a = random.randint(0,len(self.searchlist)-1)
            pos = self.searchlist[a]
            del self.searchlist[a]

        else:
            a = random.randint(0,len(self.searchlist2)-1)
            pos = self.searchlist2[a]
            del self.searchlist2[a]

        x,y = pos
        if self.enemy_board[x][y] == 0 and self.useful(x,y):
            return (x,y)

        return self.search()


    def useful(self,x,y):
        if x+1 < 10:
            if self.enemy_board[x+1][y] != 2:
                return 1
        if x-1 > -1:
            if self.enemy_board[x-1][y] != 2:
                return 1
        if y+1 < 10:
            if self.enemy_board[x][y+1] != 2:
                return 1
        if y-1 > -1:
            if self.enemy_board[x][y-1] != 2:
                return 1
        return 0


    def destrooy(self):
        if self.hit == 1 and len(self.hitlist) == 1:
            self.direction = random.randint(0,1)
        
        self.hit = 0

        options = self.getadjacency()

        pos = self.choose_option(options)

        if pos == (-1,-1):
            self.direction = not self.direction
            
            options = self.getadjacency()

            pos = self.choose_option(options)

            if pos == (-1,-1):
                self.hitlist = []
                return self.search()

        return pos


    def choose_option(self,options):
        choice = (-1,-1)
        size = len(options)
        for i in range(0,size):
            a = random.randint(0,len(options)-1)
            x,y = options[a]
            del options[a]
            if self.enemy_board[x][y] == 0:
                choice = (x,y)
                break

        return choice

        
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
        if self.hitlist == []:
            return self.search()
        else:
            return self.destrooy()


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



class Piece():
    def __init__(self,size):
        self.size = size
        self.squares = []


"""    def redraw(self, delay):
        self.canvas.itemconfig("rect", fill="blue")
        self.canvas.itemconfig("oval", fill="blue")
        for i in range(10):
            row = random.randint(0,9)
            col = random.randint(0,9)
            item_id = self.oval[row,col]
            self.canvas.itemconfig(item_id, fill="green")
        self.after(delay, lambda: self.redraw(delay))
"""
if __name__ == "__main__":
    app = App()
    app.mainloop()
