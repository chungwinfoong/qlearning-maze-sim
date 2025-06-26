# 🔍 Search and Rescue (SAR) Mission Simulator

A Q-learning based simulation where a robot agent must rescue victims and safely navigate to the exit while avoiding fire hazards.

---

## 🚀 Features

- Search and Rescue mission with "easy" and "hard" levels
- Q-learning agent trained and saved as `q_table_easy.pkl` and `q_table_hard.pkl`
- Grid-based environment with fire, victims, and exit points
- Real-time mission playback

---

## 📁 Files Overview

- `agent.py` – Q-learning agent logic  
- `environment.py` – Simulation environment setup  
- `learning.py` – Q-learning training script  
- `mission.py` – Runs the rescue mission using a trained Q-table  
- `q_table_easy.pkl`, `q_table_hard.pkl` – Pre-trained Q-tables  
- `requirements.txt` – Python dependencies

---

## 🧪 Running the Simulation

1. **Install dependencies**  
```bash
pip install -r requirements.txt
Run a mission

bash
Copy
Edit
python mission.py --level easy
# or
python mission.py --level hard
To train the agent (optional)

bash
Copy
Edit
python learning.py