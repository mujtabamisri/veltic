import json, random, tkinter as tk
from pathlib import Path
import customtkinter as ctk

ctk.set_appearance_mode('dark')
THEMES = {
 'Midnight':('#101827','#1b2940','#53e3c2','#ffbc73','#e8f2ff'),
 'Neon':('#130e24','#25183e','#00f5d4','#ff4fc3','#ffffff'),
 'Ocean':('#092737','#15465a','#5eead4','#fbbf24','#ecfeff'),
 'Sunset':('#302036','#51334d','#ffb86b','#ff719a','#fff2e9'),
 'Light':('#e8edf5','#ffffff','#087e87','#d45c64','#18283a')}
SAVE=Path.home()/'.veltic_settings.json'
LINES=[(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def outcome(b):
 for line in LINES:
  a,c,d=line
  if b[a] and b[a]==b[c]==b[d]: return b[a],line
 return ('Draw',None) if all(b) else (None,None)

def minimax(b,turn,depth=0):
 winner,_=outcome(b)
 if winner: return ({'O':10-depth,'X':depth-10,'Draw':0}[winner],None)
 moves=[]
 for i in range(9):
  if not b[i]:
   b[i]=turn
   score,_=minimax(b,'X' if turn=='O' else 'O',depth+1)
   b[i]=''
   moves.append((score,i))
 return (max(moves) if turn=='O' else min(moves))

class Game(ctk.CTk):
 def __init__(self):
  super().__init__()
  self.title('VELTIC • Tic Tac Toe'); self.geometry('680x820'); self.minsize(560,710)
  try: self.saved=json.loads(SAVE.read_text())
  except Exception: self.saved={}
  self.theme=ctk.StringVar(value=self.saved.get('theme','Midnight'))
  self.mode=ctk.StringVar(value=self.saved.get('mode','Computer'))
  self.level=ctk.StringVar(value=self.saved.get('level','Hard'))
  self.stats=self.saved.get('stats',{'X':0,'O':0,'Draw':0})
  self.board=['']*9; self.turn='X'; self.finished=False; self.history=[]; self.after_id=None
  self.build(); self.new_game()
  self.protocol('WM_DELETE_WINDOW',self.close)
 def palette(self): return THEMES[self.theme.get()]
 def build(self):
  bg,panel,xcol,ocol,fg=self.palette(); self.configure(fg_color=bg)
  for child in self.winfo_children(): child.destroy()
  ctk.CTkLabel(self,text='V E L T I C',font=('Arial',36,'bold'),text_color=xcol).pack(pady=(22,0))
  ctk.CTkLabel(self,text='A LITTLE GAME. A LOT OF STRATEGY.',font=('Arial',11),text_color=fg).pack(pady=(0,18))
  bar=ctk.CTkFrame(self,fg_color=panel,corner_radius=16); bar.pack(fill='x',padx=24,pady=4)
  for label,var,choices,callback in [('MODE',self.mode,['Computer','Local 1v1'],self.new_game),('AI LEVEL',self.level,['Easy','Medium','Hard','Impossible'],self.new_game),('THEME',self.theme,list(THEMES),self.theme_change)]:
   col=ctk.CTkFrame(bar,fg_color='transparent'); col.pack(side='left',expand=True,padx=5,pady=12)
   ctk.CTkLabel(col,text=label,font=('Arial',10,'bold'),text_color=fg).pack()
   ctk.CTkOptionMenu(col,variable=var,values=choices,command=lambda _v,cb=callback:cb(),width=145 if label=='MODE' else 130,fg_color=bg,button_color=xcol,text_color=fg).pack(pady=4)
  self.status=ctk.CTkLabel(self,text='',font=('Arial',22,'bold'),text_color=fg); self.status.pack(pady=(22,12))
  self.canvas=tk.Canvas(self,width=420,height=420,highlightthickness=0,bg=bg,cursor='hand2'); self.canvas.pack()
  self.canvas.bind('<Button-1>',self.click); self.canvas.bind('<Motion>',self.hover)
  self.hovered=-1
  actions=ctk.CTkFrame(self,fg_color='transparent'); actions.pack(pady=18)
  for name,action in [('↻  New Game',self.new_game),('↶  Undo',self.undo),('✦  Hint',self.hint)]:
   ctk.CTkButton(actions,text=name,command=action,width=135,fg_color=panel,hover_color=xcol,text_color=fg).pack(side='left',padx=5)
  self.score=ctk.CTkLabel(self,text='',font=('Arial',15),text_color=fg); self.score.pack(pady=7)
  ctk.CTkLabel(self,text='Click a square to play   •   X always starts',font=('Arial',12),text_color=fg).pack(pady=5)
  self.bind('<Control-n>',lambda _:self.new_game()); self.bind('<Control-z>',lambda _:self.undo())
  self.draw()
 def theme_change(self): self.build(); self.update_status(); self.save()
 def save(self):
  try: SAVE.write_text(json.dumps({'theme':self.theme.get(),'mode':self.mode.get(),'level':self.level.get(),'stats':self.stats}))
  except OSError: pass
 def close(self): self.save(); self.destroy()
 def cancel_ai(self):
  if self.after_id:
   self.after_cancel(self.after_id); self.after_id=None
 def new_game(self):
  self.cancel_ai(); self.board=['']*9; self.turn='X'; self.finished=False; self.history=[]; self.hovered=-1
  self.update_status(); self.draw(); self.save()
 def update_status(self):
  if not self.finished: self.status.configure(text=('Your turn • X' if self.mode.get()=='Computer' and self.turn=='X' else 'Computer thinking…' if self.mode.get()=='Computer' else f'Player {self.turn} to move'))
  self.score.configure(text=f"X wins: {self.stats.get('X',0)}     •     O wins: {self.stats.get('O',0)}     •     Draws: {self.stats.get('Draw',0)}")
 def click(self,event):
  i=self.index(event.x,event.y)
  if i is None or self.finished or self.board[i] or (self.mode.get()=='Computer' and self.turn=='O'): return
  self.move(i)
 def index(self,x,y):
  if not (0<=x<420 and 0<=y<420): return None
  return (y//140)*3+x//140
 def hover(self,event):
  i=self.index(event.x,event.y)
  if i!=self.hovered: self.hovered=i; self.draw()
 def move(self,i):
  if self.finished or self.board[i]: return
  self.history.append((self.board.copy(),self.turn))
  self.board[i]=self.turn
  winner,line=outcome(self.board)
  if winner:
   self.finished=True; self.stats[winner]=self.stats.get(winner,0)+1
   self.status.configure(text='It’s a draw!' if winner=='Draw' else ('You win! 🎉' if winner=='X' and self.mode.get()=='Computer' else 'Computer wins!' if winner=='O' and self.mode.get()=='Computer' else f'Player {winner} wins! 🎉'))
   self.draw(line); self.save(); self.update_score_only(); return
  self.turn='O' if self.turn=='X' else 'X'; self.update_status(); self.draw()
  if self.mode.get()=='Computer' and self.turn=='O': self.after_id=self.after(420,self.ai_move)
 def update_score_only(self): self.score.configure(text=f"X wins: {self.stats.get('X',0)}     •     O wins: {self.stats.get('O',0)}     •     Draws: {self.stats.get('Draw',0)}")
 def ai_move(self):
  self.after_id=None
  if self.finished or self.turn!='O' or self.mode.get()!='Computer': return
  free=[i for i,v in enumerate(self.board) if not v]
  if not free: return
  level=self.level.get()
  if level=='Easy': i=random.choice(free)
  elif level=='Medium' and random.random()<.55: i=random.choice(free)
  elif level=='Hard' and random.random()<.18: i=random.choice(free)
  else: _,i=minimax(self.board.copy(),'O')
  self.move(i)
 def undo(self):
  self.cancel_ai()
  if not self.history: return
  old_winner,_=outcome(self.board)
  steps=2 if self.mode.get()=='Computer' and self.turn=='X' and len(self.history)>=2 else 1
  for _ in range(steps):
   if self.history: self.board,self.turn=self.history.pop()
  if self.finished and old_winner:
   self.stats[old_winner]=max(0,self.stats.get(old_winner,0)-1)
  self.finished=False; self.update_status(); self.draw(); self.save()
  if self.mode.get()=='Computer' and self.turn=='O': self.after_id=self.after(420,self.ai_move)
 def hint(self):
  if self.finished or (self.mode.get()=='Computer' and self.turn=='O'): return
  if self.turn=='O': _,i=minimax(self.board.copy(),'O')
  else:
   # Choose X's best move by reversing the board roles for the O-maximizing solver.
   swapped=['O' if x=='X' else 'X' if x=='O' else '' for x in self.board]
   _,i=minimax(swapped,'O')
  if i is not None:
   self.draw(hint=i); self.after(900,self.draw)
 def draw(self,line=None,hint=None):
  if not hasattr(self,'canvas'): return
  bg,panel,xc,oc,fg=self.palette(); c=self.canvas; c.configure(bg=bg); c.delete('all')
  for i in range(9):
   r,col=divmod(i,3); x=col*140+7; y=r*140+7
   fill=xc if i==hint else panel
   if i==self.hovered and not self.board[i] and not self.finished: fill='#31445c' if self.theme.get()!='Light' else '#cbd8e8'
   c.create_rectangle(x,y,x+126,y+126,fill=fill,outline='',width=0)
   mark=self.board[i]
   if mark=='X':
    c.create_line(x+36,y+36,x+90,y+90,fill=xc,width=10,capstyle='round')
    c.create_line(x+90,y+36,x+36,y+90,fill=xc,width=10,capstyle='round')
   elif mark=='O': c.create_oval(x+36,y+36,x+90,y+90,outline=oc,width=10)
  if line:
   a,_,b=line; x1=(a%3)*140+70; y1=(a//3)*140+70; x2=(b%3)*140+70; y2=(b//3)*140+70
   c.create_line(x1,y1,x2,y2,fill='#ffe66d',width=7,capstyle='round')

if __name__=='__main__': Game().mainloop()
