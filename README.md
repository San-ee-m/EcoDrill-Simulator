# EcoDrill Simulator 🛢️🌱

**EcoDrill Simulator** is a Python game built with Pygame that simulates oil drilling while balancing environmental sustainability.

---

## 🎮 Gameplay

- Drill oil to earn money  
- Sell oil and upgrade your drill  
- Manage pollution and environment levels  
- Reach the money goal before environmental collapse  

---

## ⚙️ Features

- Animated drilling rigs  
- Drill efficiency upgrades  
- Cooldown-based drilling mechanic  
- Multiple difficulty levels:  
  - **Easy:** 1000  
  - **Medium:** 3000  
  - **Hard:** 10000  
  - **Extreme:** 50000  
- Local leaderboard (time-based)  
- Player name input  
- Sound effects & UI feedback  

---

## 🏆 Leaderboard

Leaderboard entries store:

- Player name  
- Difficulty  
- Time taken  
- Date achieved  

Entries are stored locally in `leaderboard.json`.

---

## 🧰 Tools

### `tools/extract_frames.py`

A helper script to split a spritesheet into individual frames for your game.

**Usage:**

```bash
python tools/extract.py path/to/spritesheet.png output/folder frame_width frame_height
