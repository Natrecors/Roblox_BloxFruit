# 🏴‍☠️ Blox Fruits Ultimate OS v8.0 (Command Center)

A powerful, modular, open-source desktop dashboard designed to optimize your Blox Fruits experience. Built with Python and `customtkinter`, this toolkit provides real-time event tracking, market live-checks, PvP statistics, and crew management inside a modern, dark-themed UI.

🔒 **100% Ban-Free & Safe:** This application uses official public APIs and local mathematical models. It does **not** inject scripts, modify game memory, or read hidden DataStores.

## ✨ Pro Features
* ⚔️ **PvP Bounty Tracker:** Track your session wins/losses, calculate win rate, and monitor net bounty changes.
* ⚖️ **Trade Ledger & Live Market:** Log your successful trades locally and use the quick-link to check live market values.
* 💬 **Discord Embed Broadcaster:** Send professional, automated trade offers directly to your Discord servers via webhook.
* 📋 **Crew To-Do List & Private Servers:** Manage crew tasks and launch VIP servers with a single click.
* 🗺️ **Visual Island Tracker:** Enter your level to see your current farming location, next destination, and max level progress bar.
* ⏰ **Timers & Utilities:** Global event alarms (Factory, Fruit Spawns), Server Hop cooldowns, Player Intel (ID Fetcher), and Raid calculations.
* 🛡️ **Cybersecurity Vault:** All sensitive data (Discord Webhooks, Trade History, To-Do list) is encrypted locally using `cryptography.fernet`.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Natrecors/Roblox_BloxFruit.git](https://github.com/Natrecors/Roblox_BloxFruit.git)
   cd Roblox_BloxFruit

2. **Install required dependencies:**
   Make sure you have Python 3 installed, then run:
   ```bash
   pip install customtkinter cryptography requests
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```
   (Note: The application uses a modular architecture. Always execute main.py to start the OS).
## ⚙️ System Requirements
* Windows 10/11 (for full `winsound` alarm compatibility)
* Python 3.8 or higher

## 📂 Data Privacy Note
* The app dynamically creates a data/ folder to store your encrypted vault.enc and secret.key. These files are ignored by git to ensure your webhooks and private logs remain strictly on your machine.
---
*Developed by [Natrecors](https://github.com/Natrecors)*
