# 🐍 Snake Game AI - Deep Reinforcement Learning (DQN)

An autonomous Snake AI built with **Python**, **PyTorch**, and **Pygame**. The snake learns to navigate the grid, hunt food, and avoid collisions using a **Deep Q-Network (DQN)** with experience replay and target networks.

---

## 🌟 Key Features

- **Deep Q-Learning (DQN)**:
  - Neural network policy estimating Q-values for action decisions.
  - Target network stabilization to avoid overestimation bias.
  - $\epsilon$-greedy exploration-exploitation strategy that decays over time.
  - Experience replay with both short-term memory (per-step) and long-term memory (mini-batch replay per game).
- **Custom Pygame Graphics**:
  - Modular sprite rendering for snake heads, straight bodies, corners/bends, directional tails, and apples.
  - Live on-screen score display.
- **Visual & Headless Modes**:
  - Run with visual rendering to watch the snake learn in real-time.
  - Run headless (without window rendering) for significantly faster training throughput.
- **Live Training Analytics**:
  - Real-time visualization using Matplotlib to track game score and cumulative moving average score.
- **Persistent High Scores & Checkpoints**:
  - Automatically saves the best model weights to `model/model.pth`.
  - Automatically tracks and updates the all-time high score in `highscore.txt`.

---

## 🧠 How the AI Works

### 1. State Representation (11 Inputs)
The agent perceives its environment through an 11-dimensional binary vector:

| State Index | Feature | Description |
| :--- | :--- | :--- |
| `0` | **Danger Straight** | Immediate collision risk ahead |
| `1` | **Danger Right** | Immediate collision risk to the right |
| `2` | **Danger Left** | Immediate collision risk to the left |
| `3` | **Moving Right** | Snake currently traveling right `(1, 0)` |
| `4` | **Moving Left** | Snake currently traveling left `(-1, 0)` |
| `5` | **Moving Down** | Snake currently traveling down `(0, 1)` |
| `6` | **Moving Up** | Snake currently traveling up `(0, -1)` |
| `7` | **Food Right** | Food is to the right of the head |
| `8` | **Food Left** | Food is to the left of the head |
| `9` | **Food Up** | Food is above the head |
| `10` | **Food Down** | Food is below the head |

### 2. Action Space (3 Outputs)
The agent makes relative direction choices rather than absolute coordinates:
- `[1, 0, 0]` $\rightarrow$ **0: Continue Straight**
- `[0, 1, 0]` $\rightarrow$ **1: Turn Right (90° clockwise)**
- `[0, 0, 1]` $\rightarrow$ **2: Turn Left (90° counter-clockwise)**

### 3. Reward Function
- **+10**: Eating an apple (snake length increments by 1).
- **-10**: Collision with wall, self-collision, or looping timeout ($> 100 \times \text{body length}$).
- **+0.1**: Moving closer to the food (Euclidean distance shaping).
- **-0.1**: Moving farther from the food.

### 4. Neural Network Architecture
```
Input Layer (11) ──> Linear(11, 128) ──> ReLU ──> Linear(128, 256) ──> ReLU ──> Linear(256, 3) ──> Q-values
```
- **Optimizer**: Adam (`lr=0.001`)
- **Loss Function**: Mean Squared Error (MSE)
- **Discount Factor ($\gamma$)**: `0.99`

---

## 📁 Project Structure

```text
snake_game/
├── assets/                  # Snake & apple sprite textures
│   ├── apple.png
│   ├── body_bottomleft.png
│   ├── body_bottomright.png
│   ├── body_horizontal.png
│   ├── body_topleft.png
│   ├── body_topright.png
│   ├── body_vertical.png
│   ├── head_up.png / head_down.png / head_left.png / head_right.png
│   └── tail_up.png / tail_down.png / tail_left.png / tail_right.png
├── model/                   # Saved model checkpoints
│   └── model.pth
├── src/
│   ├── __init__.py
│   ├── agent.py             # DQN Agent (memory, state extraction, action selection)
│   ├── game.py              # Pygame environment, sprites, collisions, step logic
│   ├── helper.py            # Live Matplotlib score plot utility
│   └── model.py             # PyTorch DQN architecture and DQNTrainer
├── highscore.txt            # Persistent high score record
├── req.txt                  # Python dependencies
├── train.py                 # Training pipeline and entry point
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- (Optional) CUDA-compatible GPU if using GPU-accelerated PyTorch

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/EyobTesfaye8/snake_game.git
cd snake_game

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r req.txt
```

---

## 🎮 Usage

### Train with Graphical Window (Render Mode)
To observe the snake playing and learning in real-time with Pygame graphics and a live training graph:

```bash
python train.py -r
```

### Train Headless (Fast Mode)
To maximize training speed without opening the Pygame window:

```bash
python train.py
```

During training, terminal logs will report:
```text
Game 1 | Score 0 | Record 0
Game 2 | Score 1 | Record 1
...
Game 85 | Score 34 | Record 34
```
Whenever a new record score is achieved, the model weights are automatically saved to `model/model.pth`.

---

## 🛠️ Configuration & Hyperparameters

Hyperparameters can be tuned in `src/agent.py`, `src/model.py`, and `train.py`:

| Parameter | Location | Default | Description |
| :--- | :--- | :--- | :--- |
| `lr` | `train.py` / `DQNTrainer` | `0.001` | Learning rate for Adam optimizer |
| `gamma` | `DQNTrainer` | `0.99` | Discount factor for future rewards |
| `memory maxlen` | `Agent.__init__` | `100,000` | Replay buffer capacity |
| `batch_size` | `Agent.train_long_memory` | `1000` | Experience sample size for long-term memory |
| `CELL_SIZE` | `src/game.py` | `50` | Pixel dimensions per grid cell |
| `CELL_NUMBER` | `src/game.py` | `30` | Number of cells per row/column |
| `tick` | `src/game.py` | `150` | Pygame clock tick speed in render mode |

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
