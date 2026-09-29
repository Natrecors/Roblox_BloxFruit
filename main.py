import customtkinter as ctk
import os
import json
import threading
from cryptography.fernet import Fernet
import config
import views

try:
    import winsound
except ImportError:
    winsound = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class BloxFruitsOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blox Fruits Ultimate OS v8.0 (Command Center)")
        self.geometry("1150x800")
        self.minsize(1000, 700)
        
        if not os.path.exists(config.DATA_DIR):
            os.makedirs(config.DATA_DIR)
            
        self.init_security_vault()
        self.timers = {"factory": 0, "fruit": 0, "hop": 0, "bosses": {b: 0 for b in config.BOSS_RESPAWNS}}
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#121212")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(11, weight=1)
        
        ctk.CTkLabel(self.sidebar, text="Blox OS", font=ctk.CTkFont(size=28, weight="bold"), text_color="#69F0AE").grid(row=0, column=0, padx=20, pady=(25, 35))
        
        self.nav_btns = {}
        # FULL ENGLISH NAVIGATION WITH NEW MODULES
        nav_items = [
            ("dashboard", "📊 Stat Calculator"),
            ("pvp", "⚔️ PvP Bounty Tracker"),
            ("todo", "📋 Crew To-Do List"),
            ("trade", "⚖️ Trade Ledger"),
            ("servers", "🌐 Private Servers"),
            ("timers", "⏰ Timers & Alarms"),
            ("route", "🗺️ Island Tracker"),
            ("utils", "🛠️ Utilities"),
            ("social", "💬 Discord Hub"),
            ("system", "⚙️ System & Logs")
        ]
        
        for idx, (key, text) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(self.sidebar, text=text, command=lambda k=key: self.select_frame(k), 
                                fg_color="transparent", text_color=("gray10", "gray90"), 
                                hover_color="#2A2A2A", anchor="w", font=ctk.CTkFont(size=15, weight="bold"))
            btn.grid(row=idx, column=0, padx=15, pady=5, sticky="ew")
            self.nav_btns[key] = btn
            
        self.frames = {}
        # ADDED TradeFrame AND ServersFrame
        for F in (views.DashboardFrame, views.PvpFrame, views.TodoFrame, views.TradeFrame, views.ServersFrame, 
                  views.TimersFrame, views.RouteFrame, views.UtilsFrame, views.SocialFrame, views.SystemFrame):
            page_name = F.__name__.replace("Frame", "").lower()
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
            frame.grid_remove()
            
        self.select_frame("dashboard")
        self.update_global_clocks()
        self.log_event("SYSTEM", "UI Engine loaded successfully.")

    def select_frame(self, name):
        for btn in self.nav_btns.values():
            btn.configure(fg_color="transparent")
        self.nav_btns[name].configure(fg_color="#333333")
        
        for frame in self.frames.values():
            frame.grid_remove()
            
        self.frames[name].grid(row=0, column=1, sticky="nsew", padx=25, pady=25)

    def init_security_vault(self):
        key_path = os.path.join(config.DATA_DIR, "secret.key")
        vault_path = os.path.join(config.DATA_DIR, "vault.enc")
        
        if not os.path.exists(key_path):
            with open(key_path, "wb") as f:
                f.write(Fernet.generate_key())
                
        self.cipher = Fernet(open(key_path, "rb").read())
        self.vault = {}
        
        if os.path.exists(vault_path):
            try:
                self.vault = json.loads(self.cipher.decrypt(open(vault_path, "rb").read()).decode())
            except:
                pass

    def save_vault(self):
        with open(os.path.join(config.DATA_DIR, "vault.enc"), "wb") as f:
            f.write(self.cipher.encrypt(json.dumps(self.vault).encode()))

    def log_event(self, category, message):
        self.frames["system"].append_log(category, message)

    def play_alarm(self, freq=1000, dur=1000):
        if winsound:
            threading.Thread(target=lambda: winsound.Beep(freq, dur), daemon=True).start()

    def update_global_clocks(self):
        if self.timers["factory"] > 0:
            self.timers["factory"] -= 1
            if self.timers["factory"] == 0:
                self.play_alarm()
                self.log_event("ALARM", "Factory Raid!")
                
        if self.timers["fruit"] > 0:
            self.timers["fruit"] -= 1
            if self.timers["fruit"] == 300:
                self.play_alarm(800, 500)
                self.log_event("ALARM", "Fruit spawns in 5 min.")
            if self.timers["fruit"] == 0:
                self.log_event("ALARM", "Fruit has spawned.")

        if self.timers["hop"] > 0:
            self.timers["hop"] -= 1
            if self.timers["hop"] == 0:
                self.play_alarm(1500, 300)
                self.log_event("ALARM", "Server Hop cooldown finished!")
                
        for boss, t in self.timers["bosses"].items():
            if t > 0:
                self.timers["bosses"][boss] -= 1
                if self.timers["bosses"][boss] == 0:
                    self.play_alarm(1200, 800)
                    self.log_event("ALARM", f"Boss {boss} is ready!")
                    
        self.frames["timers"].refresh_ui()
        self.after(1000, self.update_global_clocks)

if __name__ == "__main__":
    app = BloxFruitsOS()
    app.mainloop()