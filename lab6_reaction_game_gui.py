
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import queue
import time
import csv
import os
from datetime import datetime
from collections import Counter
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


WINS_NEEDED = 3
DATA_FOLDER = "player_data"
BAUD_RATE   = 9600


C_BG    = '#1a1a2e'
C_PANEL = '#16213e'
C_RED   = '#e94560'
C_TEAL  = '#00d4aa'
C_YELL  = '#ffdd57'
C_WHITE = '#ffffff'
C_GREY  = '#a0a0cc'


def ensure_folder():
    os.makedirs(DATA_FOLDER, exist_ok=True)

def get_filepath(name):
    ensure_folder()
    safe = "".join(c for c in name if c.isalnum() or c in(' ','_')).strip()
    return os.path.join(DATA_FOLDER, f"{safe}.csv")

def save_result(player, opponent, result, reaction_ms, date_str):
    """
    Saves one round result to the player's CSV file.
    Creates the file with a header if it does not exist yet.
    Appends a new row if the player has played before.
    """
    filepath   = get_filepath(player)
    file_exists = os.path.exists(filepath)

    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:                          # new player
            writer.writerow(['Date','Opponent','Result','ReactionTime_ms'])
        writer.writerow([date_str, opponent, result, reaction_ms])

def load_player_data(name):
    filepath = get_filepath(name)
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return list(csv.DictReader(f))

def list_all_players():
    ensure_folder()
    return [f.replace('.csv','') for f in os.listdir(DATA_FOLDER)
            if f.endswith('.csv')]


class ReactionGameApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Reaction Game — ADA University")
        self.root.geometry("950x720")
        self.root.configure(bg=C_BG)

        self.ser           = None
        self.serial_queue  = queue.Queue()

        self.player_names  = ["", ""]
        self.scores        = [0, 0]
        self.game_active   = False
        self.waiting_motors = False

        self._build_ui()
        self._poll_queue()   # start 50ms queue check loop

    
    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook',     background=C_BG, borderwidth=0)
        style.configure('TNotebook.Tab', background=C_PANEL, foreground=C_GREY,
                         padding=[12,5], font=('Arial',11,'bold'))
        style.map('TNotebook.Tab',
                  background=[('selected', C_RED)],
                  foreground=[('selected', C_WHITE)])

        nb = ttk.Notebook(self.root)
        nb.pack(fill='both', expand=True, padx=12, pady=12)

        self.game_frame  = tk.Frame(nb, bg=C_BG)
        self.stats_frame = tk.Frame(nb, bg=C_BG)
        nb.add(self.game_frame,  text='Game')
        nb.add(self.stats_frame, text='Statistics')

        self._build_game_tab()
        self._build_stats_tab()

    def _build_game_tab(self):
        f = self.game_frame

        tk.Label(f, text="REACTION GAME", font=('Arial',24,'bold'),
                 bg=C_BG, fg=C_RED).pack(pady=10)

        
        conn = tk.Frame(f, bg=C_BG)
        conn.pack(pady=4)
        tk.Label(conn, text="COM Port:", bg=C_BG, fg=C_WHITE,
                 font=('Arial',11)).pack(side='left')
        self.port_var = tk.StringVar()
        ports = [p.device for p in serial.tools.list_ports.comports()]
        cb = ttk.Combobox(conn, textvariable=self.port_var,
                          values=ports, width=10)
        if ports:
            cb.set(ports[0])
        cb.pack(side='left', padx=5)
        tk.Button(conn, text="Connect", command=self._connect,
                  bg=C_PANEL, fg=C_TEAL, font=('Arial',10,'bold'),
                  relief='flat', padx=10).pack(side='left', padx=5)
        self.conn_lbl = tk.Label(conn, text="Disconnected",
                                  bg=C_BG, fg='#ff4444', font=('Arial',10))
        self.conn_lbl.pack(side='left', padx=5)

        
        entry_row = tk.Frame(f, bg=C_BG)
        entry_row.pack(pady=12)
        self.name_entries = []
        for i, lbl in enumerate(['Player 1 (Left Button)', 'Player 2 (Right Button)']):
            col = tk.Frame(entry_row, bg=C_BG)
            col.pack(side='left', padx=25)
            tk.Label(col, text=lbl, bg=C_BG, fg=C_GREY,
                     font=('Arial',11)).pack()
            e = tk.Entry(col, font=('Arial',14), width=14,
                         bg=C_PANEL, fg=C_WHITE, insertbackground=C_WHITE,
                         relief='flat', highlightthickness=2,
                         highlightbackground=C_PANEL, highlightcolor=C_RED)
            e.pack(pady=4)
            self.name_entries.append(e)

        
        score_row = tk.Frame(f, bg=C_PANEL, pady=8)
        score_row.pack(fill='x', padx=40, pady=6)
        self.score_labels = []
        for i in range(2):
            lbl = tk.Label(score_row, text=f"P{i+1}: 0",
                           font=('Arial',22,'bold'), bg=C_PANEL, fg=C_RED)
            lbl.pack(side='left', expand=True)
            self.score_labels.append(lbl)

        
        self.status_lbl = tk.Label(f, text="Enter names and press START",
                                    font=('Arial',15), bg=C_BG, fg=C_TEAL,
                                    wraplength=800)
        self.status_lbl.pack(pady=18)

        self.time_lbl = tk.Label(f, text="", font=('Arial',13),
                                  bg=C_BG, fg=C_YELL)
        self.time_lbl.pack()

        
        self.start_btn = tk.Button(f, text="START GAME",
                                    command=self._start_game,
                                    font=('Arial',14,'bold'),
                                    bg=C_RED, fg=C_WHITE,
                                    relief='flat', padx=24, pady=10,
                                    state='disabled')
        self.start_btn.pack(pady=14)

        
        tk.Label(f, text="Round History", bg=C_BG, fg=C_GREY,
                 font=('Arial',11,'bold')).pack(anchor='w', padx=40)
        self.history = tk.Text(f, height=7, bg=C_PANEL, fg=C_WHITE,
                                font=('Consolas',10), relief='flat',
                                state='disabled', padx=8, pady=4)
        self.history.pack(fill='x', padx=40, pady=(2,10))

    def _build_stats_tab(self):
        f = self.stats_frame
        tk.Label(f, text="Player Statistics", font=('Arial',18,'bold'),
                 bg=C_BG, fg=C_RED).pack(pady=10)

        ctrl = tk.Frame(f, bg=C_BG)
        ctrl.pack(pady=6)
        tk.Label(ctrl, text="Player:", bg=C_BG, fg=C_WHITE,
                 font=('Arial',11)).pack(side='left')
        self.stats_player_var = tk.StringVar()
        self.stats_cb = ttk.Combobox(ctrl, textvariable=self.stats_player_var,
                                      width=18)
        self.stats_cb.pack(side='left', padx=6)
        tk.Label(ctrl, text="Chart:", bg=C_BG, fg=C_WHITE,
                 font=('Arial',11)).pack(side='left', padx=(12,0))
        self.chart_var = tk.StringVar(value='Reaction Times')
        ttk.Combobox(ctrl, textvariable=self.chart_var,
                     values=['Reaction Times','Win/Loss Ratio','Wins vs Opponents'],
                     width=18).pack(side='left', padx=6)
        tk.Button(ctrl, text="Load", command=self._draw_chart,
                  bg=C_RED, fg=C_WHITE, relief='flat', padx=14).pack(side='left', padx=6)
        tk.Button(ctrl, text="Refresh", command=self._refresh_players,
                  bg=C_PANEL, fg=C_TEAL, relief='flat', padx=10).pack(side='left', padx=4)

        self.fig, self.ax = plt.subplots(figsize=(8, 4.2))
        self.fig.patch.set_facecolor(C_PANEL)
        self.ax.set_facecolor(C_BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=f)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=10)
        self._refresh_players()


    def _connect(self):
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "Select a COM port.")
            return
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)          # wait for Arduino reboot
            self.conn_lbl.config(text="Connected", fg='#00ff88')
            self.start_btn.config(state='normal')
            threading.Thread(target=self._serial_reader,
                             daemon=True).start()
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", str(e))

    def _serial_reader(self):
        """Background thread — reads serial continuously"""
        while self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8',
                                                      errors='ignore').strip()
                    if line:
                        self.serial_queue.put(line)
            except Exception:
                break

    def _send(self, cmd):
        if self.ser and self.ser.is_open:
            self.ser.write((cmd + '\n').encode())

  
    def _poll_queue(self):
        try:
            while True:
                msg = self.serial_queue.get_nowait()
                self._handle_msg(msg)
        except queue.Empty:
            pass
        self.root.after(50, self._poll_queue)

    def _handle_msg(self, msg):
        """Process every message received from Arduino"""
        if msg.startswith("COUNTDOWN:"):
            secs = msg.split(":")[1]
            self._status(f"Get ready...  {secs}s", C_YELL)

        elif msg == "BUZZER":
            self._status("PRESS NOW!!!", C_RED)

        elif msg.startswith("FALSE:"):
            false_idx = int(msg.split(":")[1]) - 1    # 0-indexed
            win_idx   = 1 - false_idx
            self._status(
                f"FALSE START — {self.player_names[false_idx]}!\n"
                f"Point to {self.player_names[win_idx]}.", '#ff8800')
            self._award_point(win_idx, wt=-1, lt=-1, false_start=True)

        elif msg.startswith("RESULT:"):
            _, s1, s2 = msg.split(":")
            self._process_result(int(s1), int(s2))

        elif msg == "MOTORS_OK":
            self.waiting_motors = False
            if self.game_active:
                self.root.after(2000, self._start_round)

        elif msg == "VICTORY_OK":
            self.waiting_motors = False
            self._show_winner()

  
    def _start_game(self):
        p1 = self.name_entries[0].get().strip()
        p2 = self.name_entries[1].get().strip()
        if not p1 or not p2:
            messagebox.showwarning("Missing Names", "Enter both player names.")
            return
        if not (self.ser and self.ser.is_open):
            messagebox.showerror("Not Connected", "Connect to Arduino first.")
            return
        self.player_names = [p1, p2]
        self.scores       = [0, 0]
        self.game_active  = True
        self._update_scores()
        self._clear_history()
        self.time_lbl.config(text="")
        self.start_btn.config(state='disabled')
        self._start_round()

    def _start_round(self):
        self._status("Waiting for random countdown...", C_TEAL)
        self.time_lbl.config(text="")
        self._send("START")

    def _process_result(self, t1, t2):
        """Determine winner from reaction times"""
        if t1 == -1 and t2 == -1:
            self._status("Nobody pressed! Round skipped.", '#ff8800')
            self.root.after(2000, self._start_round)
            return
        elif t1 == -1:
            win_idx, lose_idx, wt, lt = 1, 0, t2, t1
        elif t2 == -1:
            win_idx, lose_idx, wt, lt = 0, 1, t1, t2
        else:
            if t1 <= t2:
                win_idx, lose_idx, wt, lt = 0, 1, t1, t2
            else:
                win_idx, lose_idx, wt, lt = 1, 0, t2, t1

        wname = self.player_names[win_idx]
        self._status(
            f"{wname} wins the round!\n"
            f"{self.player_names[0]}: {t1 if t1!=-1 else 'N/A'}ms"
            f"   |   "
            f"{self.player_names[1]}: {t2 if t2!=-1 else 'N/A'}ms",
            '#00ff88')
        self.time_lbl.config(
            text=f"{self.player_names[0]}: {t1 if t1!=-1 else 'N/A'} ms"
                 f"   |   "
                 f"{self.player_names[1]}: {t2 if t2!=-1 else 'N/A'} ms")

        self._award_point(win_idx, wt=wt, lt=lt)

    def _award_point(self, win_idx, wt, lt, false_start=False):
        lose_idx = 1 - win_idx
        wname    = self.player_names[win_idx]
        lname    = self.player_names[lose_idx]
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.scores[win_idx] += 1
        self._update_scores()

       
        if wt != -1:
            save_result(wname, lname, 'WIN',  wt, date_str)
        if lt != -1:
            save_result(lname, wname, 'LOSS', lt, date_str)

        
        rnd = self.scores[0] + self.scores[1]
        tag = " [FALSE START]" if false_start else ""
        self._log(
            f"Round {rnd}{tag}: {wname} won "
            f"({wt if wt!=-1 else 'N/A'}ms vs {lt if lt!=-1 else 'N/A'}ms)")

        
        if self.scores[win_idx] >= WINS_NEEDED:
            self._send(f"VICTORY:{win_idx + 1}")
        else:
            self._send(f"WINNER:{win_idx + 1}")
        self.waiting_motors = True

    def _show_winner(self):
        wi = 0 if self.scores[0] >= WINS_NEEDED else 1
        self._status(f"{self.player_names[wi]} WINS THE GAME!", C_RED)
        self.game_active = False
        self.start_btn.config(state='normal', text="NEW GAME")
        self._refresh_players()

   
    def _status(self, text, color=C_TEAL):
        self.status_lbl.config(text=text, fg=color)

    def _update_scores(self):
        for i in range(2):
            n = self.player_names[i] if self.player_names[i] else f"P{i+1}"
            self.score_labels[i].config(text=f"{n}:  {self.scores[i]}")

    def _log(self, text):
        self.history.config(state='normal')
        self.history.insert('end', text + '\n')
        self.history.see('end')
        self.history.config(state='disabled')

    def _clear_history(self):
        self.history.config(state='normal')
        self.history.delete('1.0', 'end')
        self.history.config(state='disabled')

    
    def _refresh_players(self):
        players = list_all_players()
        self.stats_cb['values'] = players
        if players:
            self.stats_player_var.set(players[0])

    def _draw_chart(self):
        player     = self.stats_player_var.get()
        chart_type = self.chart_var.get()
        if not player:
            return
        data = load_player_data(player)
        if not data:
            messagebox.showinfo("No Data", f"No saved data for {player}")
            return

        self.ax.clear()
        self.ax.set_facecolor(C_BG)
        self.fig.patch.set_facecolor(C_PANEL)

        def style():
            self.ax.tick_params(colors=C_WHITE)
            for s in ['top','right']:
                self.ax.spines[s].set_visible(False)
            for s in ['bottom','left']:
                self.ax.spines[s].set_color(C_GREY)
            self.ax.xaxis.label.set_color(C_WHITE)
            self.ax.yaxis.label.set_color(C_WHITE)
            self.ax.title.set_color(C_WHITE)

        if chart_type == 'Reaction Times':
            times = [float(r['ReactionTime_ms']) for r in data
                     if r['ReactionTime_ms'] not in ('-1','')]
            self.ax.plot(range(1, len(times)+1), times,
                         color=C_RED, marker='o', linewidth=2)
            if times:
                avg = sum(times)/len(times)
                self.ax.axhline(avg, color=C_TEAL, linestyle='--',
                                 label=f'Avg: {avg:.0f}ms')
                self.ax.legend(facecolor=C_PANEL, labelcolor=C_WHITE)
            self.ax.set_xlabel('Round #')
            self.ax.set_ylabel('Reaction Time (ms)')
            self.ax.set_title(f'{player} — Reaction Times')
            style()

        elif chart_type == 'Win/Loss Ratio':
            wins   = sum(1 for r in data if r['Result']=='WIN')
            losses = len(data) - wins
            if wins + losses > 0:
                w, t, a = self.ax.pie(
                    [wins, losses],
                    labels=[f'Wins ({wins})', f'Losses ({losses})'],
                    colors=[C_TEAL, C_RED], autopct='%1.0f%%',
                    startangle=90)
                for x in t + a:
                    x.set_color(C_WHITE)
            self.ax.set_title(f'{player} — Win / Loss Ratio')
            self.ax.title.set_color(C_WHITE)

        elif chart_type == 'Wins vs Opponents':
            wc = Counter(r['Opponent'] for r in data if r['Result']=='WIN')
            if wc:
                self.ax.bar(list(wc.keys()), list(wc.values()), color=C_RED)
                self.ax.set_xlabel('Opponent')
                self.ax.set_ylabel('Wins')
                self.ax.set_title(f'{player} — Wins vs Opponents')
                style()

        self.canvas.draw()



if __name__ == "__main__":
    root = tk.Tk()
    app  = ReactionGameApp(root)
    root.mainloop()
