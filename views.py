import customtkinter as ctk
import tkinter.messagebox as messagebox
import subprocess
import threading
import webbrowser
from datetime import datetime
import requests
import config

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Advanced Stat Calculator", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(card, text="⚠️ DISCLAIMER: This calculator uses META (Min-Max) percentage distribution\nfor maximum farming efficiency, completely ignoring useless stats.", 
                     text_color="#FF5252", font=ctk.CTkFont(size=12, slant="italic")).pack(pady=10)
        
        settings_frame = ctk.CTkFrame(card, fg_color="transparent")
        settings_frame.pack(fill="x", padx=30, pady=10)
        
        last_build = self.controller.vault.get("last_build", "Fruit Main (Logia)")
        self.build_var = ctk.StringVar(value=last_build)
        self.opt_build = ctk.CTkOptionMenu(settings_frame, values=["Fruit Main (Logia)", "Buddha (Melee)", "Sword Main"], variable=self.build_var)
        self.opt_build.pack(side="left", padx=10)
        
        self.entry_lvl = ctk.CTkEntry(settings_frame, placeholder_text="Enter Level (Max 2550)", width=200)
        self.entry_lvl.pack(side="left", padx=10, fill="x", expand=True)
        
        last_lvl = self.controller.vault.get("last_level", "")
        if last_lvl:
            self.entry_lvl.insert(0, last_lvl)
            
        ctk.CTkButton(settings_frame, text="Generate Build", command=self.calc, fg_color="#1976D2").pack(side="right", padx=10)
        
        self.res_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.res_frame.pack(pady=25)
        
        self.lbl_m = ctk.CTkLabel(self.res_frame, text="Melee: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF5252", width=120)
        self.lbl_m.grid(row=0, column=0, padx=10, pady=5)
        self.lbl_d = ctk.CTkLabel(self.res_frame, text="Defense: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#448AFF", width=120)
        self.lbl_d.grid(row=0, column=1, padx=10, pady=5)
        self.lbl_s = ctk.CTkLabel(self.res_frame, text="Sword: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#9E9E9E", width=120)
        self.lbl_s.grid(row=0, column=2, padx=10, pady=5)
        self.lbl_g = ctk.CTkLabel(self.res_frame, text="Gun: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFEB3B", width=120)
        self.lbl_g.grid(row=1, column=0, padx=10, pady=5)
        self.lbl_f = ctk.CTkLabel(self.res_frame, text="Blox Fruit: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#E040FB", width=120)
        self.lbl_f.grid(row=1, column=1, padx=10, pady=5)

    def calc(self):
        try:
            lvl_text = self.entry_lvl.get().strip()
            if not lvl_text: return
            lvl = int(lvl_text)
            if lvl > 2550: lvl = 2550
            if lvl < 1: lvl = 1
            pts = (lvl - 1) * 3
            
            s_melee, s_def, s_sword, s_gun, s_fruit = 1, 1, 1, 1, 1
            
            build = self.build_var.get()
            
            if build == "Fruit Main (Logia)":
                p_fruit = int(pts * 0.65)
                p_melee = int(pts * 0.21)
                p_def = pts - p_fruit - p_melee
                s_fruit += p_fruit
                s_melee += p_melee
                s_def += p_def
                
            elif build == "Buddha (Melee)":
                p_melee = int(pts * 0.60)
                p_def = pts - p_melee
                s_melee += p_melee
                s_def += p_def
                
            elif build == "Sword Main":
                p_sword = int(pts * 0.60)
                p_melee = int(pts * 0.20)
                p_def = pts - p_sword - p_melee
                s_sword += p_sword
                s_melee += p_melee
                s_def += p_def
                
            self.lbl_m.configure(text=f"Melee: {s_melee}")
            self.lbl_d.configure(text=f"Defense: {s_def}")
            self.lbl_s.configure(text=f"Sword: {s_sword}")
            self.lbl_g.configure(text=f"Gun: {s_gun}")
            self.lbl_f.configure(text=f"Blox Fruit: {s_fruit}")
            
            self.controller.vault["last_level"] = str(lvl)
            self.controller.vault["last_build"] = build
            self.controller.save_vault()
            
            self.controller.log_event("STATS", f"Generated {build} build for level {lvl}")
        except ValueError:
            pass

class PvpFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.start_bounty = 0
        self.current_bounty = 0
        self.wins = 0
        self.losses = 0
        
        ctk.CTkLabel(self, text="PvP Session Tracker", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        setup_card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        setup_card.pack(fill="x", pady=10)
        
        row_setup = ctk.CTkFrame(setup_card, fg_color="transparent")
        row_setup.pack(pady=15, padx=20, fill="x")
        self.entry_start = ctk.CTkEntry(row_setup, placeholder_text="Enter starting Bounty (e.g. 2500000)")
        self.entry_start.pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkButton(row_setup, text="Set Starting Bounty", command=self.set_bounty, fg_color="#1976D2").pack(side="right", padx=10)
        
        self.stats_card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        self.stats_card.pack(fill="both", expand=True, pady=10)
        
        self.lbl_current = ctk.CTkLabel(self.stats_card, text="Current Bounty: ---", font=ctk.CTkFont(size=28, weight="bold"), text_color="#FFD740")
        self.lbl_current.pack(pady=25)
        
        row_actions = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        row_actions.pack(pady=10)
        
        self.entry_change = ctk.CTkEntry(row_actions, placeholder_text="Bounty Change (e.g. 15000)")
        self.entry_change.pack(side="left", padx=15)
        ctk.CTkButton(row_actions, text="+ Win", fg_color="#00C853", hover_color="#00E676", command=lambda: self.record_match("win")).pack(side="left", padx=10)
        ctk.CTkButton(row_actions, text="- Loss", fg_color="#D50000", hover_color="#FF1744", command=lambda: self.record_match("loss")).pack(side="left", padx=10)
        
        self.lbl_stats = ctk.CTkLabel(self.stats_card, text="Wins: 0 | Losses: 0 | Win Rate: 0% | Net: 0", font=ctk.CTkFont(size=16))
        self.lbl_stats.pack(pady=25)

    def set_bounty(self):
        try:
            val = int(self.entry_start.get().strip())
            self.start_bounty = val
            self.current_bounty = val
            self.wins = 0
            self.losses = 0
            self.update_display()
            self.controller.log_event("PVP", f"Started session with {val} bounty.")
        except ValueError:
            messagebox.showerror("Error", "Bounty must be a valid number.")

    def record_match(self, result):
        if self.start_bounty == 0:
            return messagebox.showerror("Error", "Please set starting bounty first.")
        try:
            change = int(self.entry_change.get().strip())
            if result == "win":
                self.current_bounty += change
                self.wins += 1
            else:
                self.current_bounty -= change
                self.losses += 1
            self.update_display()
        except ValueError:
            messagebox.showerror("Error", "Change amount must be a number.")

    def update_display(self):
        self.lbl_current.configure(text=f"Current Bounty: {self.current_bounty:,}")
        total_matches = self.wins + self.losses
        winrate = (self.wins / total_matches * 100) if total_matches > 0 else 0
        net_change = self.current_bounty - self.start_bounty
        sign = "+" if net_change >= 0 else ""
        self.lbl_stats.configure(text=f"Wins: {self.wins} | Losses: {self.losses} | Win Rate: {winrate:.1f}% | Net: {sign}{net_change:,}")

class TodoFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Crew To-Do List", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        add_card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        add_card.pack(fill="x", pady=10)
        
        row_add = ctk.CTkFrame(add_card, fg_color="transparent")
        row_add.pack(pady=15, padx=20, fill="x")
        self.entry_task = ctk.CTkEntry(row_add, placeholder_text="Enter task (e.g. Help Gosho get V4)")
        self.entry_task.pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkButton(row_add, text="Add Task", command=self.add_task, fg_color="#1976D2").pack(side="right", padx=10)
        
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, pady=10)
        
        self.refresh_tasks()

    def add_task(self):
        task = self.entry_task.get().strip()
        if task:
            tasks = self.controller.vault.get("todo_list", [])
            tasks.append(task)
            self.controller.vault["todo_list"] = tasks
            self.controller.save_vault()
            self.entry_task.delete(0, "end")
            self.refresh_tasks()
            self.controller.log_event("TODO", "Task added.")

    def delete_task(self, index):
        tasks = self.controller.vault.get("todo_list", [])
        if 0 <= index < len(tasks):
            tasks.pop(index)
            self.controller.vault["todo_list"] = tasks
            self.controller.save_vault()
            self.refresh_tasks()

    def refresh_tasks(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        tasks = self.controller.vault.get("todo_list", [])
        if not tasks:
            ctk.CTkLabel(self.list_frame, text="No tasks yet. You're all caught up!", font=ctk.CTkFont(slant="italic")).pack(pady=20)
            return
            
        for i, task in enumerate(tasks):
            row = ctk.CTkFrame(self.list_frame, corner_radius=10, fg_color="#1E1E1E")
            row.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(row, text=f"• {task}", font=ctk.CTkFont(size=14), anchor="w").pack(side="left", padx=15, pady=10, fill="x", expand=True)
            ctk.CTkButton(row, text="Complete", width=80, fg_color="#00695C", hover_color="#004D40", command=lambda idx=i: self.delete_task(idx)).pack(side="right", padx=10)

class TradeFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Trade Ledger", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        input_card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        input_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(input_card, text="Record a New Trade", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        row_input = ctk.CTkFrame(input_card, fg_color="transparent")
        row_input.pack(pady=10, padx=20, fill="x")
        self.entry_gave = ctk.CTkEntry(row_input, placeholder_text="I gave (e.g. Dough)")
        self.entry_gave.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_got = ctk.CTkEntry(row_input, placeholder_text="I got (e.g. T-Rex + Adds)")
        self.entry_got.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(row_input, text="Log Trade", command=self.log_trade, fg_color="#1976D2").pack(side="right", padx=5)
        
        ctk.CTkLabel(self, text="Trade History", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        self.history_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.history_frame.pack(fill="both", expand=True)
        self.refresh_history()

    def log_trade(self):
        gave = self.entry_gave.get().strip()
        got = self.entry_got.get().strip()
        if gave and got:
            history = self.controller.vault.get("trade_history", [])
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            history.insert(0, {"date": date_str, "gave": gave, "got": got})
            self.controller.vault["trade_history"] = history
            self.controller.save_vault()
            self.entry_gave.delete(0, "end")
            self.entry_got.delete(0, "end")
            self.refresh_history()
            self.controller.log_event("TRADE", "New trade logged successfully.")

    def delete_trade(self, index):
        history = self.controller.vault.get("trade_history", [])
        if 0 <= index < len(history):
            history.pop(index)
            self.controller.vault["trade_history"] = history
            self.controller.save_vault()
            self.refresh_history()

    def refresh_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
            
        history = self.controller.vault.get("trade_history", [])
        if not history:
            ctk.CTkLabel(self.history_frame, text="No trades recorded yet.", font=ctk.CTkFont(slant="italic")).pack(pady=10)
            return
            
        for i, trade in enumerate(history):
            card = ctk.CTkFrame(self.history_frame, corner_radius=10, fg_color="#1E1E1E")
            card.pack(fill="x", pady=5)
            
            info_text = f"[{trade['date']}] Gave: {trade['gave']}  |  Got: {trade['got']}"
            ctk.CTkLabel(card, text=info_text, font=ctk.CTkFont(size=14), anchor="w").pack(side="left", padx=15, pady=10, fill="x", expand=True)
            ctk.CTkButton(card, text="Delete", width=60, fg_color="#D50000", hover_color="#FF1744", command=lambda idx=i: self.delete_trade(idx)).pack(side="right", padx=10)

class ServersFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Private Server Manager", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        add_card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        add_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(add_card, text="Add New Private Server", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        row_add = ctk.CTkFrame(add_card, fg_color="transparent")
        row_add.pack(pady=10, padx=20, fill="x")
        self.entry_name = ctk.CTkEntry(row_add, placeholder_text="Server Name (e.g. Crew Server)")
        self.entry_name.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_link = ctk.CTkEntry(row_add, placeholder_text="VIP Server Link (roblox.com/...)")
        self.entry_link.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(row_add, text="Save Server", command=self.add_server, fg_color="#00695C").pack(side="right", padx=5)
        
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_servers()

    def add_server(self):
        name = self.entry_name.get().strip()
        link = self.entry_link.get().strip()
        if name and link:
            servers = self.controller.vault.get("private_servers", [])
            servers.append({"name": name, "link": link})
            self.controller.vault["private_servers"] = servers
            self.controller.save_vault()
            self.entry_name.delete(0, "end")
            self.entry_link.delete(0, "end")
            self.refresh_servers()
            self.controller.log_event("SERVER", f"Added private server: {name}")

    def delete_server(self, index):
        servers = self.controller.vault.get("private_servers", [])
        if 0 <= index < len(servers):
            servers.pop(index)
            self.controller.vault["private_servers"] = servers
            self.controller.save_vault()
            self.refresh_servers()

    def join_server(self, link):
        webbrowser.open(link)
        self.controller.log_event("SERVER", "Launching Roblox VIP Server...")

    def refresh_servers(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        servers = self.controller.vault.get("private_servers", [])
        if not servers:
            ctk.CTkLabel(self.list_frame, text="No private servers saved.", font=ctk.CTkFont(slant="italic")).pack(pady=20)
            return
            
        for i, srv in enumerate(servers):
            card = ctk.CTkFrame(self.list_frame, corner_radius=10, fg_color="#1E1E1E")
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=srv['name'], font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(side="left", padx=15, pady=15)
            ctk.CTkButton(card, text="Delete", width=60, fg_color="#D50000", hover_color="#FF1744", command=lambda idx=i: self.delete_server(idx)).pack(side="right", padx=10)
            ctk.CTkButton(card, text="Join Server", width=100, fg_color="#1976D2", hover_color="#115293", command=lambda l=srv['link']: self.join_server(l)).pack(side="right", padx=10)

class TimersFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.boss_lbls = {}
        
        ctk.CTkLabel(self, text="Timers & Alarms", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        card_hop = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        card_hop.pack(fill="x", pady=10)
        self.lbl_hop = ctk.CTkLabel(card_hop, text="Server Hop Cooldown: Ready", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_hop.pack(pady=10)
        ctk.CTkButton(card_hop, text="Start Hop Timer (2 min)", command=lambda: self.start_timer("hop", 120)).pack(pady=10)
        
        events_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        events_frame.pack(fill="x", pady=10)
        self.lbl_fac = ctk.CTkLabel(events_frame, text="Factory/Pirate Raid: 00:00", font=ctk.CTkFont(size=16))
        self.lbl_fac.pack(pady=10)
        ctk.CTkButton(events_frame, text="Start Factory (90m)", command=lambda: self.start_timer("factory", 5400)).pack(pady=5)
        self.lbl_fruit = ctk.CTkLabel(events_frame, text="Fruit Spawn: 00:00", font=ctk.CTkFont(size=16))
        self.lbl_fruit.pack(pady=10)
        ctk.CTkButton(events_frame, text="Start Fruit (60m)", command=lambda: self.start_timer("fruit", 3600)).pack(pady=10)
        
        boss_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        boss_frame.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(boss_frame, text="Boss Respawn Manager", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        for boss, time_m in config.BOSS_RESPAWNS.items():
            row = ctk.CTkFrame(boss_frame, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=5)
            lbl = ctk.CTkLabel(row, text=f"{boss}: Ready", width=250, anchor="w", font=ctk.CTkFont(size=14))
            lbl.pack(side="left")
            self.boss_lbls[boss] = lbl
            ctk.CTkButton(row, text="Killed", width=80, fg_color="#FF5252", command=lambda b=boss, t=time_m: self.start_timer(b, t*60)).pack(side="right")

    def start_timer(self, target, secs):
        if target in ["factory", "fruit", "hop"]:
            self.controller.timers[target] = secs
        else:
            self.controller.timers["bosses"][target] = secs
        self.controller.log_event("TIMER", f"Timer started for {target}.")

    def refresh_ui(self):
        t = self.controller.timers
        if t['hop'] > 0: self.lbl_hop.configure(text=f"Server Hop Cooldown: {t['hop']//60:02d}:{t['hop']%60:02d}", text_color="#FFD740")
        else: self.lbl_hop.configure(text="Server Hop Cooldown: Ready", text_color="#69F0AE")
            
        self.lbl_fac.configure(text=f"Factory: {t['factory']//60:02d}:{t['factory']%60:02d}")
        self.lbl_fruit.configure(text=f"Fruit: {t['fruit']//60:02d}:{t['fruit']%60:02d}")
        for b, time_left in t["bosses"].items():
            if time_left > 0: self.boss_lbls[b].configure(text=f"{b}: {time_left//60:02d}:{time_left%60:02d}", text_color="#FFD740")
            else: self.boss_lbls[b].configure(text=f"{b}: Ready", text_color="#69F0AE")

class RouteFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Visual Island Tracker", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        self.prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.prog_frame.pack(fill="x", pady=10, padx=20)
        self.lbl_prog = ctk.CTkLabel(self.prog_frame, text="Max Level Progress: 0%", font=ctk.CTkFont(weight="bold"))
        self.lbl_prog.pack()
        self.prog_bar = ctk.CTkProgressBar(self.prog_frame, height=15, progress_color="#69F0AE")
        self.prog_bar.pack(fill="x", pady=5)
        self.prog_bar.set(0)
        
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=10, padx=20)
        self.route_lvl = ctk.CTkEntry(row, placeholder_text="Enter Current Level")
        self.route_lvl.pack(side="left", fill="x", expand=True)
        
        last_lvl = self.controller.vault.get("last_level", "")
        if last_lvl:
            self.route_lvl.insert(0, last_lvl)
            
        ctk.CTkButton(row, text="Update Tracker", command=self.gen_route, fg_color="#1976D2").pack(side="right", padx=10)
        
        self.cur_card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        self.cur_card.pack(fill="x", pady=15, padx=20)
        ctk.CTkLabel(self.cur_card, text="📍 Current Location", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FFD740").pack(pady=10)
        self.lbl_cur_loc = ctk.CTkLabel(self.cur_card, text="Awaiting data...", font=ctk.CTkFont(size=16))
        self.lbl_cur_loc.pack(pady=5)
        
        self.next_card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        self.next_card.pack(fill="x", pady=10, padx=20)
        ctk.CTkLabel(self.next_card, text="➡️ Next Destination", font=ctk.CTkFont(size=16, weight="bold"), text_color="#448AFF").pack(pady=10)
        self.lbl_next_loc = ctk.CTkLabel(self.next_card, text="Awaiting data...", font=ctk.CTkFont(size=14))
        self.lbl_next_loc.pack(pady=5)

    def gen_route(self):
        try:
            lvl_text = self.route_lvl.get().strip()
            if not lvl_text: return
            lvl = int(lvl_text)
            if lvl > 2550: lvl = 2550
            
            prog = lvl / 2550
            self.prog_bar.set(prog)
            self.lbl_prog.configure(text=f"Max Level Progress: {int(prog * 100)}%")
            
            self.controller.vault["last_level"] = str(lvl)
            self.controller.save_vault()
            
            idx = next((i for i, v in enumerate(config.LEVELING_ROUTE) if v[0] <= lvl <= v[1]), -1)
            if idx == -1:
                self.lbl_cur_loc.configure(text="Level out of bounds (Sea 3 mapping needed).")
                self.lbl_next_loc.configure(text="")
                return
                
            c = config.LEVELING_ROUTE[idx]
            self.lbl_cur_loc.configure(text=f"Island: {c[2]}\nMobs to farm: {c[3]}\nLevels: {c[0]} - {c[1]}")
            
            if idx + 1 < len(config.LEVELING_ROUTE):
                n = config.LEVELING_ROUTE[idx + 1]
                self.lbl_next_loc.configure(text=f"{n[2]} (Unlocks at Level {n[0]})\nTarget Mobs: {n[3]}")
            else:
                self.lbl_next_loc.configure(text="No further mapping available.")
                
            self.controller.log_event("ROUTE", f"Route calculated for lvl {lvl}.")
        except ValueError:
            pass

class UtilsFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Automated APIs & Tools", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        card_wiki = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        card_wiki.pack(fill="x", pady=10)
        ctk.CTkLabel(card_wiki, text="Direct Wiki Search", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        row_wiki = ctk.CTkFrame(card_wiki, fg_color="transparent")
        row_wiki.pack(fill="x", padx=30, pady=5)
        self.entry_wiki = ctk.CTkEntry(row_wiki, placeholder_text="e.g. Dough, Saber...")
        self.entry_wiki.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(row_wiki, text="Open Article", command=self.search_wiki, fg_color="#00695C").pack(side="right")
        
        card_intel = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        card_intel.pack(fill="x", pady=10)
        ctk.CTkLabel(card_intel, text="Roblox Player Intel (ID Fetcher)", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(card_intel, text="Verify accounts before trading.", font=ctk.CTkFont(size=11, slant="italic")).pack()
        row_intel = ctk.CTkFrame(card_intel, fg_color="transparent")
        row_intel.pack(fill="x", padx=30, pady=10)
        self.entry_player = ctk.CTkEntry(row_intel, placeholder_text="Enter exact Roblox Username")
        self.entry_player.pack(side="left", fill="x", expand=True, padx=5)
        
        self.btn_profile = ctk.CTkButton(row_intel, text="Open Profile", state="disabled", fg_color="#00695C", width=100)
        self.btn_profile.pack(side="right", padx=5)
        ctk.CTkButton(row_intel, text="Fetch Intel", command=self.fetch_player, width=100).pack(side="right", padx=5)
        
        self.lbl_intel = ctk.CTkLabel(card_intel, text="Result: ---", text_color="#FFD740")
        self.lbl_intel.pack(pady=5)

        card_trade = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        card_trade.pack(fill="x", pady=10)
        ctk.CTkLabel(card_trade, text="Live Market Trade Values", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(card_trade, text="Check real-time fruit prices directly from the market.", font=ctk.CTkFont(size=12, slant="italic")).pack()
        ctk.CTkButton(card_trade, text="Open BloxFruitsValues", command=lambda: webbrowser.open("https://bloxfruitsvalues.com/values/fruits"), fg_color="#1976D2").pack(pady=10)

        card1 = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        card1.pack(fill="x", pady=10)
        ctk.CTkLabel(card1, text="Raid Awakening Calculator", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.opt_fruit = ctk.CTkOptionMenu(card1, values=list(config.AWAKENING_COSTS.keys()))
        self.opt_fruit.pack(pady=5)
        self.entry_frags = ctk.CTkEntry(card1, placeholder_text="Current Fragments")
        self.entry_frags.pack(pady=5)
        self.lbl_awaken = ctk.CTkLabel(card1, text="Result: ---", font=ctk.CTkFont(weight="bold"))
        self.lbl_awaken.pack(pady=10)
        ctk.CTkButton(card1, text="Calculate Raids", command=self.calc_awaken).pack(pady=10)

    def search_wiki(self):
        query = self.entry_wiki.get().strip()
        if query:
            formatted = query.title().replace(" ", "_")
            url = f"https://blox-fruits.fandom.com/wiki/{formatted}"
            webbrowser.open(url)
            self.controller.log_event("WIKI", f"Opened wiki for '{formatted}'")

    def fetch_player(self):
        user = self.entry_player.get().strip()
        if not user: return
        self.lbl_intel.configure(text="Fetching from Roblox API...", text_color="white")
        self.btn_profile.configure(state="disabled")
        
        def run():
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                res = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [user], "excludeBannedUsers": False}, headers=headers, timeout=5)
                data = res.json().get("data", [])
                if data:
                    user_id = data[0]["id"]
                    self.lbl_intel.configure(text=f"User Found! | ID: {user_id}", text_color="#69F0AE")
                    self.btn_profile.configure(state="normal", command=lambda: webbrowser.open(f"https://www.roblox.com/users/{user_id}/profile"))
                    self.controller.log_event("API", f"Fetched User ID {user_id} for {user}")
                else:
                    self.lbl_intel.configure(text="User not found or banned.", text_color="#FF5252")
            except requests.Timeout:
                self.lbl_intel.configure(text="Request Timed Out.", text_color="#FF5252")
            except Exception as e:
                self.lbl_intel.configure(text="API Error.", text_color="#FF5252")
        threading.Thread(target=run, daemon=True).start()

    def calc_awaken(self):
        try:
            frags_input = self.entry_frags.get().strip()
            frags = int(frags_input) if frags_input else 0
            needed = config.AWAKENING_COSTS[self.opt_fruit.get()] - frags
            raids = max(0, (needed // 1000) + (1 if needed % 1000 != 0 else 0))
            self.lbl_awaken.configure(text=f"Total Raids Needed: {raids} (at ~1k frags/raid)", text_color="#69F0AE")
        except ValueError:
            pass

class SocialFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Discord Embed Broadcaster", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        card_discord = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        card_discord.pack(fill="x", pady=10)
        ctk.CTkLabel(card_discord, text="Send Pro Trade Offers", font=ctk.CTkFont(weight="bold")).pack(pady=15)
        
        saved_webhook = self.controller.vault.get("discord_webhook", "")
        self.entry_webhook = ctk.CTkEntry(card_discord, placeholder_text="Webhook URL (Will be encrypted)")
        self.entry_webhook.pack(pady=5, padx=30, fill="x")
        if saved_webhook: self.entry_webhook.insert(0, saved_webhook)
            
        self.entry_offer = ctk.CTkEntry(card_discord, placeholder_text="Offering (e.g. Leopard, Dragon)")
        self.entry_offer.pack(pady=5, padx=30, fill="x")
        self.entry_target = ctk.CTkEntry(card_discord, placeholder_text="Looking For (e.g. Kitsune)")
        self.entry_target.pack(pady=15, padx=30, fill="x")
        ctk.CTkButton(card_discord, text="Send Embed to Discord", command=self.broadcast_trade, height=35).pack(pady=15)

    def broadcast_trade(self):
        webhook = self.entry_webhook.get().strip()
        offer = self.entry_offer.get().strip()
        target = self.entry_target.get().strip()
        
        if not webhook or not offer or not target: return messagebox.showerror("Error", "Please fill all fields!")
            
        if webhook != self.controller.vault.get("discord_webhook"):
            self.controller.vault["discord_webhook"] = webhook
            self.controller.save_vault()
            
        payload = {
            "username": "Blox OS Market",
            "avatar_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Roblox_player_icon_black.svg/1200px-Roblox_player_icon_black.svg.png",
            "embeds": [{
                "title": "🚨 New Trade Offer 🚨",
                "color": 3447003,
                "fields": [
                    {"name": "WTS (Offering)", "value": f"**{offer}**", "inline": True},
                    {"name": "WTB (Looking For)", "value": f"**{target}**", "inline": True}
                ],
                "footer": {"text": "Sent automatically via Blox OS"}
            }]
        }
        
        def send_req():
            try:
                res = requests.post(webhook, json=payload, timeout=5)
                if res.status_code == 204:
                    self.controller.log_event("DISCORD", "Embed offer broadcasted.")
                    messagebox.showinfo("Success", "Professional Embed sent to Discord!")
                else:
                    self.controller.log_event("ERROR", f"Discord Error: {res.status_code}")
            except requests.Timeout:
                self.controller.log_event("ERROR", "Discord Request Timed Out.")
            except Exception as e:
                self.controller.log_event("ERROR", f"Network Error: {e}")
        threading.Thread(target=send_req, daemon=True).start()

class SystemFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="System Logs & Updates", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        row_sys = ctk.CTkFrame(self, fg_color="transparent")
        row_sys.pack(fill="x", pady=5)
        ctk.CTkButton(row_sys, text="Update Code (Git Pull)", command=self.git_pull).pack(side="left", padx=5)
        
        self.lbl_git = ctk.CTkLabel(row_sys, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_git.pack(side="left", padx=15)
        
        self.terminal = ctk.CTkTextbox(self, font=("Consolas", 13), fg_color="#0D0D0D", text_color="#69F0AE")
        self.terminal.pack(fill="both", expand=True, pady=10)
        self.terminal.configure(state="disabled")

    def append_log(self, category, msg):
        stamp = datetime.now().strftime("%H:%M:%S")
        self.terminal.configure(state="normal")
        self.terminal.insert("end", f"[{stamp}] [{category}] {msg}\n")
        self.terminal.yview("end")
        self.terminal.configure(state="disabled")

    def git_pull(self):
        self.lbl_git.configure(text="Checking...", text_color="white")
        self.append_log("GIT", "Requesting codebase update...")
        def run():
            try:
                res = subprocess.check_output(["git", "pull"], stderr=subprocess.STDOUT, text=True)
                self.append_log("GIT", res.strip())
                
                if "Already up to date" in res:
                    self.lbl_git.configure(text="✅ Code is up to date", text_color="#69F0AE")
                else:
                    self.lbl_git.configure(text="⚠️ Update applied! Restart OS", text_color="#FFD740")
            except Exception:
                self.lbl_git.configure(text="❌ Git Error", text_color="#FF5252")
                self.append_log("ERROR", "Git is not configured in this directory.")
        threading.Thread(target=run, daemon=True).start()