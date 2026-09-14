# Auto Clicker & Macro Recorder

A modern, high-performance, dark-themed Auto Clicker and Macro Action Recorder for **macOS** and **Windows**.

[English](#english) | [繁體中文](#繁體中文)

---

<a name="english"></a>
## English

### 🌟 Overview
**Auto Clicker & Macro Recorder** is a cross-platform desktop automation utility written in Python. It provides ultra-fast mouse clicking (up to 1,000 CPS) and an intelligent keyboard/mouse macro recorder with persistent profile storage and customizable hotkeys.

### ✨ Key Features
- **Cross-Platform**: Dedicated scripts optimized for both macOS (Aqua dark styling) and Windows (Per-Monitor DPI awareness).
- **Extreme Speed Auto Clicker (1 ~ 1,000 CPS)**:
  - Precise millisecond delay control.
  - **Uncapped Mode**: Maximum clicking speed without software throttling.
  - **Jitter Protection**: Micro-randomization to simulate human clicking and avoid anti-cheat/bot flags.
  - Left, right, and middle mouse button support.
  - Clickable CPS preset bar with instant adding and right-click removal.
- **Intelligent Action Recorder (Macro)**:
  - **High-Precision Timing**: Records exact keyboard key presses/releases and mouse click events (button and X, Y coordinates).
  - **Smart Filtering (No Cursor Wander)**: Deliberately ignores continuous mouse movement (`mouse_move`) to prevent massive file bloat and choppy playback.
  - **Profile Library**: Save named macros to disk (`macros.json`) and switch or delete them easily.
  - **Playback Control**: Loop count (set `0` for infinite loop) and playback speed multiplier (1.0x, 1.5x, 2.0x).
- **Customizable Global Hotkeys**:
  - Auto Click toggle: Default `[F6]`
  - Action Recording toggle: Default `[F9]`
  - Macro Playback toggle: Default `[F8]`
  - In-app key rebinding with release confirmation and 0.5s anti-accidental cooldown.

---

### 📁 Project Structure
```
├── mac_clicker.py        # macOS specialized entry script
├── windows_clicker.py    # Windows specialized entry script
├── README.md             # Project documentation (Bilingual)
├── presets.json          # Auto-generated: Saved CPS presets
└── macros.json           # Auto-generated: Saved macro profiles
```

---

### 🚀 Quick Start

#### 1. Requirements
- Python 3.8+
- `pynput` library:
```bash
pip install pynput
```
*(On macOS, run `pip3 install pynput`)*

#### 2. Running on macOS
```bash
python3 mac_clicker.py
```
> **macOS Accessibility Permission**:  
> On first run, grant Accessibility permission to Terminal / Python under:  
> `System Settings` ➔ `Privacy & Security` ➔ `Accessibility`.

#### 3. Running on Windows
```bash
python windows_clicker.py
```

---

<a name="繁體中文"></a>
## 繁體中文

### 🌟 專案介紹
一款專為 **macOS** 與 **Windows** 打造的高效能、高對比暗夜風格「極速自動連點」與「鍵鼠動作錄製（巨集）」輔助工具。

### ✨ 核心功能
- **極速自動連點 (1 ~ 1,000 CPS)**：
  - 支援每秒 1 至 1,000 次點擊微調與極速狂暴模式（Uncapped）。
  - 內建隨機延遲（Jitter）防偵測演算法。
  - 支援滑鼠左鍵、右鍵、滾輪中鍵分段切換。
  - 常用 CPS 檔位一鍵切換，支援即時新增與刪除（右鍵點擊檔位亦可直接刪除）。
- **智慧動作錄製與回放 (Action Recorder / Macro)**：
  - **高精度無延遲**：完整記錄鍵盤按鍵時序（Key Press / Release）與滑鼠點擊瞬間（Click X, Y 座標），**自動排除肥大漫遊的滑鼠連續移動軌跡**，避免資料臃腫卡頓與偏差。
  - **腳本庫管理**：支援自訂名稱「儲存」多組動作腳本至本機資料庫，並可隨時在清單中「載入」或「刪除」。
  - **靈活回放**：支援設定循環執行次數（設定 `0` 為無限循環直至手動停止）與回放速度倍率（1.0x、1.5x、2.0x）。
- **全域快速鍵與防誤觸機制**：
  - 連點開關：預設 `[F6]`
  - 錄製開關：預設 `[F9]`（按一下開始，再按一下結束）
  - 執行開關：預設 `[F8]`（按一下開始，再按一下結束）
  - 介面上各快速鍵均可「一鍵重新綁定」，並具備「放開按鍵確認」與「0.5 秒冷卻防抖」機制。

---

### 🎮 操作指南

#### ⚡ 分頁 1：自動連點 (Auto Clicker)
1. **調整速度**：拖動滑桿或在輸入框內鍵入目標數值（1 ~ 1,000 CPS）。
2. **切換按鍵**：點擊選取「左鍵」、「右鍵」或「滾輪中鍵」。
3. **啟動/停止**：按下鍵盤 `[F6]` 或點擊底部的啟動按鈕。
4. **檔位管理**：點選預設檔位立即套用；點擊「➕ 儲存當前 CPS」可新增檔位；在檔位按鈕上按滑鼠右鍵可直接刪除。

#### 🎬 分頁 2：動作錄製 (Action Recorder)
1. **開始錄製**：按下鍵盤 `[F9]`（或點擊「⏺ 開始錄製」），頂部狀態顯示紅燈，即可開始進行鍵盤操作或滑鼠點擊。
2. **結束錄製**：再次按下 `[F9]`，系統會自動排除此停止鍵本身，並將動作暫存。
3. **儲存腳本**：點擊「💾 儲存目前錄製」，輸入腳本名稱（例如 `連續採集` 或 `技能連擊`），即可保存到本機清單。
4. **選擇與執行**：在已儲存動作清單中選中該腳本，按下 `[F8]` 即可開始自動執行；再次按下 `[F8]` 可隨時中斷。
5. **刪除腳本**：在清單中選取要清理的項目，點擊「🗑️ 刪除選取動作」並確認即可。

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
