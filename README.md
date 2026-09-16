# 012_AutoClicker

<div align="center">

# ⚡ 012_AutoClicker
**High-Performance Cross-Platform Auto Clicker & Macro Automation Suite**  
**高效能、高對比暗夜風格跨平台極速自動連點與鍵鼠自動化輔助工具**

<p align="center">
  <a href="#-english-documentation"><img src="https://img.shields.io/badge/Language-English-2563eb?style=for-the-badge&logo=googlechrome&logoColor=white" alt="English Documentation"></a>
  <a href="#-繁體中文說明文件"><img src="https://img.shields.io/badge/語言-繁體中文-dc2626?style=for-the-badge&logo=readme&logoColor=white" alt="繁體中文說明文件"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-0284c7?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3b82f6?style=flat-square&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-10b981?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Release-v3.0-8b5cf6?style=flat-square" alt="Release">
</p>

</div>

---

# 🌐 English Documentation

An ultra-fast, dark-themed, high-contrast automation utility engineered specifically for **macOS** and **Windows**. It combines an uncapped high-speed Auto Clicker, an automated Auto Typer, a versatile Action Recorder (Macro), and an advanced Safety & Security suite into a unified, zero-lag interface.

---

## 🌟 Key Features

- **Native Cross-Platform Architecture**: Dedicated, platform-native Python source code for both Windows and macOS, seamlessly integrating with OS-level input hooks and native UI rendering.
- **Bilingual Support**: Built-in English and Traditional Chinese language packs. Switch seamlessly in real-time with the top-right `🌐` button.
- **High-Contrast Pure Dark Theme**:
  - Overcomes macOS Aqua engine limitations (which force white text on white buttons) using custom dark-neon widget rendering.
  - Native Windows Per-Monitor V2 HiDPI awareness ensures razor-sharp text and graphics with zero blurriness.
- **Global Safe Hotkeys & Cooldown**:
  - Click any hotkey button in the GUI to rebind in seconds.
  - 0.5-second anti-accidental trigger cooldown and key-release binding verification.
  - Global Panic Emergency Stop Key (`[ESC]`) to instantly release all synthetic inputs and abort background threads.

---

## 📁 Repository Structure

| File Name | Platform | Description |
| :--- | :--- | :--- |
| `AutoClicker-Windows.py` | Windows | Windows dedicated source code with Per-Monitor V2 HiDPI scaling |
| `AutoClicker-Mac.py` | macOS | macOS dedicated source code with Aqua dark theme fixes & Retina support |
| `presets.json` | All | Automatically generated: Stores user-saved CPS presets |
| `macros.json` | All | Automatically generated: Stores recorded action routines |
| `typer_macros.json` | All | Automatically generated: Stores text templates for Auto Typer |
| `README.md` | All | Complete bilingual user manual and documentation |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
This project requires **Python 3** and the **pynput** global input library:

```bash
pip install pynput
```
*(On macOS with system python3, please run `pip3 install pynput`)*

---

### 2. Running on macOS

1. Download or clone the repository to a local folder.
2. Open **Terminal** and navigate to the directory:
   ```bash
   python3 AutoClicker-Mac.py
   ```
3. **Crucial macOS Permissions (Accessibility & Input Monitoring)**:  
   macOS enforces strict sandboxing on synthetic input and global key event listeners. On your first run:
   - Go to `System Settings` ➔ `Privacy & Security` ➔ `Accessibility`.
   - Toggle **ON** the checkbox for **Terminal** (or **Python**).
   - Go to `Privacy & Security` ➔ `Input Monitoring`.
   - Ensure **Terminal** (or **Python**) is granted permission.

---

### 3. Running on Windows

1. Download or clone the repository to a local folder.
2. Open **Command Prompt (CMD)** or **PowerShell**, navigate to the directory, and run:
   ```cmd
   python AutoClicker-Windows.py
   ```
3. **Administrator Privileges**:  
   If your target window (such as high-privilege games, browsers, or administrative tools) runs as Administrator, Windows UIPI (User Interface Privilege Isolation) will block synthetic mouse events. Simply right-click CMD and select **"Run as administrator"**.

---

## 🎮 User Operations Guide

### ⚡ Tab 1: Auto Clicker
1. **Adjust CPS**: Drag the continuous slider or directly enter a target number (1 ~ 1,000 CPS).
2. **Uncapped Mode**: Toggle to remove speed limits and achieve the maximum click rate permitted by hardware and OS scheduling.
3. **Mouse Button**: Switch between **Left Button**, **Right Button**, and **Middle Button**.
4. **Preset Management**:
   - Click any preset button to immediately apply its CPS value.
   - Click `➕ Save Current CPS` to add a new preset.
   - **Right-click (or two-finger tap on Mac)** any preset button to delete it instantly.
5. **Start / Stop**: Press the global hotkey `[F6]` or click the large bottom toggle button.

---

### ⌨️ Tab 2: Auto Typer
1. **Manage Snippets**: Create, edit, and save frequently used text blocks, slogans, or game chat commands.
2. **Delay Timing**: Adjust keystroke intervals (in milliseconds) to match target application input buffers.
3. **Start / Stop**: Press the global hotkey `[F7]` to initiate automated sequential character typing.

---

### 🎬 Tab 3: Action Recorder (Macro)
1. **Configure Scope**: Toggle **Mouse Clicks**, **Keyboard Keys**, and optional **Mouse Movement (Smooth)**.
2. **Start Recording**: Press `[F9]` (or click `⏺ Start Recording`). The status bar illuminates red to indicate live event capture.
3. **Stop Recording**: Press `[F9]` again. The stop keystroke is automatically trimmed from the sequence.
4. **Save Macro**: Click `💾 Save Macro`, enter a descriptive name, and save it to the local library.
5. **Playback**: Select any saved macro from the list, set loop count (`0` = infinite loops) and speed multiplier (1.0x, 1.5x, 2.0x), then press `[F8]` to start or stop playback.
6. **Live Monitor**: Observe the real-time event log at the bottom to verify incoming actions and timings.

---

### 🛡️ Tab 4: Safety & Security
1. **Jitter Randomization**: Adds microsecond jitter delays between successive clicks to bypass robotic rhythm detection.
2. **Cursor Micro-Drift**: Subtle, natural pixel shifting during long auto-clicking sessions prevents AFK idle detection.
3. **Emergency Panic Key**: Default `[ESC]`. When pressed, it immediately terminates all clicking, typing, and macro playback loops, releasing all held keys.

---

## ❓ Frequently Asked Questions (FAQ)

#### Q1: Should I enable "Mouse Movement" during recording?
> - **Disabled (Default)**: Only captures click coordinates (X, Y) and keystrokes. Keeps macro file sizes minimal and delivers rock-solid playback reliability for menu navigation, button clicking, and game spell casting.
> - **Enabled**: Records full, continuous cursor gliding paths. Recommended for drawing, drag-and-drop tasks, or workflows where trajectory matters.

#### Q2: How do I customize hotkeys?
> Click any button labeled with `[Change]` or a hotkey name. When the button turns gold, press and release your desired key. The system applies the binding with a 0.5s protective cooldown.

#### Q3: Why does playback type correctly but the mouse doesn't move on Windows?
> Windows UIPI blocks low-level input injection from standard user processes to elevated windows. Right-click CMD or your compiled `.exe` and choose **"Run as administrator"**.

---

# 🇹🇼 繁體中文說明文件

一款專為 **macOS** 與 **Windows** 打造的高效能、高對比暗夜風格全能輔助工具。集結「極速自動連點」、「自動打字機」、「鍵鼠巨集錄製」與「防偵測安全」四大核心模組，提供極致流暢且零延遲的自動化操作體驗。

---

## 🌟 核心特色

- **跨平台原生架構**：提供 Windows 與 macOS 獨立專用原始碼，底層分別深度對接 Win32 API 與 macOS Quartz / Cocoa 事件系統。
- **即時雙語支援**：內建英文（English）與繁體中文（Traditional Chinese），點擊右上角 `🌐` 按鈕即可即時無縫切換。
- **深邃暗夜主題 (Pure Dark UI)**：
  - 徹底解決 macOS 系統原生 Aqua 引擎強制覆蓋白底白字的問題，全元件採自訂深色霓虹渲染。
  - Windows 原生 Per-Monitor V2 高 DPI 清晰度適配，高解析度螢幕字體邊緣銳利不模糊。
- **全域安全快速鍵與冷卻防抖**：
  - 介面上所有熱鍵均可點擊即時重新綁定。
  - 具備 0.5 秒防誤觸冷卻與放開按鍵確認機制。
  - 內建全局緊急終止鍵（Panic Key，預設 `[ESC]`），危急時一鍵停止所有自動化程序並釋放鍵鼠。

---

## 📁 專案檔案架構

| 檔案名稱 | 適用平台 | 說明 |
| :--- | :--- | :--- |
| `AutoClicker-Windows.py` | Windows | Windows 專用原始碼，含 Per-Monitor V2 高 DPI 縮放與 Win32 適配 |
| `AutoClicker-Mac.py` | macOS | macOS 專用原始碼，解決 Aqua 白底問題並適配 Retina 與游標 |
| `presets.json` | 全平台 | 程式自動生成：儲存使用者常用 CPS 檔位配置 |
| `macros.json` | 全平台 | 程式自動生成：儲存已命名的動作錄製（巨集）腳本庫 |
| `typer_macros.json` | 全平台 | 程式自動生成：儲存自動打字機自訂文本庫 |
| `README.md` | 全平台 | 完整雙語專案說明手冊與操作指南 |

---

## 🚀 快速開始指南

### 1. 環境需求
本專案基於 **Python 3** 與 **pynput** 全域鍵鼠庫開發：

```bash
pip install pynput
```
*(在 macOS 上若使用系統 python3，請執行 `pip3 install pynput`)*

---

### 2. 在 macOS 上執行

1. 下載或複製專案至本機資料夾。
2. 開啟「終端機 (Terminal)」並進入該目錄：
   ```bash
   python3 AutoClicker-Mac.py
   ```
3. **重要權限設定（輔助使用與輸入監控）**：  
   macOS 對於全域鍵盤監聽與滑鼠模擬有嚴格的安全規範。首次執行時，請前往：  
   `系統設定 (System Settings)` ➔ `隱私權與安全性 (Privacy & Security)`：
   - **輔助使用 (Accessibility)**：勾選允許 **Terminal**（或 **Python**）。
   - **輸入監控 (Input Monitoring)**：勾選允許 **Terminal**（或 **Python**）。

---

### 3. 在 Windows 上執行

1. 下載或複製專案至本機資料夾。
2. 開啟 CMD 或 PowerShell 進入目錄並執行：
   ```cmd
   python AutoClicker-Windows.py
   ```
3. **系統管理員權限建議**：  
   若目標程式、瀏覽器或遊戲以系統管理員身分運行，Windows UIPI 機制會封鎖外部模擬輸入。請對命令提示字元按右鍵選擇**「以系統管理員身分執行」**。

---

## 🎮 詳細操作指南

### ⚡ 分頁 1：自動連點 (Auto Clicker)
1. **調整速度**：拖動滑桿或直接在文字框輸入目標數值（1 ~ 1,000 CPS）。
2. **極限無上限模式 (Uncapped)**：勾選後解除點擊頻率限制，釋放硬體最高點擊效能。
3. **切換按鍵**：自由選取「左鍵」、「右鍵」或「滾輪中鍵」。
4. **檔位管理**：
   - 點選預設檔位按鈕立即套用數值。
   - 點擊「➕ 儲存當前 CPS」可新增檔位。
   - **在檔位按鈕上按滑鼠右鍵（Mac 上雙指點擊）**可直接刪除該檔位。
5. **啟動 / 停止**：按下全域快速鍵 `[F6]` 或點擊底部的啟動按鈕。

---

### ⌨️ 分頁 2：自動打字機 (Auto Typer)
1. **建立文本庫**：新增、編輯並儲存常用的發話內容、指令或宣傳文案。
2. **控制延遲**：微調字元間的按鍵輸出間隔（毫秒），防止目標軟體輸入過快吃字。
3. **啟動 / 停止**：按下全域快速鍵 `[F7]` 即刻自動輸出文字。

---

### 🎬 分頁 3：動作錄製 (Action Recorder)
1. **錄製範圍篩選**：可個別切換是否錄製「滑鼠點擊」、「鍵盤按鍵」與「滑鼠移動軌跡」。
2. **開始錄製**：按下 `[F9]`（或點擊「⏺ 開始錄製」），頂部狀態顯示紅燈，開始記錄鍵鼠操作。
3. **結束錄製**：再次按下 `[F9]`，系統自動剔除最後的停止按鍵並暫存資料。
4. **儲存腳本**：點擊「💾 儲存目前錄製」，輸入名稱保存至本機清單。
5. **選擇與回放**：在已儲存動作清單中選中腳本，設定循環次數（設為 `0` 為無限循環）與速度倍率（1.0x / 1.5x / 2.0x），按下 `[F8]` 即可啟動或中斷播放。
6. **即時監視器**：下方日誌即時捲動顯示當前捕獲的事件內容與時序。

---

### 🛡️ 分頁 4：安全與防護 (Safety & Security)
1. **隨機延遲 (Jitter Mode)**：在點擊間隙注入微小隨機波動，打破機械化規律，防範連點偵測。
2. **游標微飄移 (Micro-Drift)**：長時間連點時加入微像素自然漂移，防止固定座標判定掛網。
3. **緊急終止鍵 (Panic Key)**：預設 `[ESC]`，任何情況下一鍵立即終止所有連點、打字與巨集線程。

---

## ❓ 常見問題 (FAQ)

#### Q1：錄製動作時該不該開啟「滑鼠移動軌跡」？
> - **關閉軌跡（預設建議）**：僅記錄滑鼠點擊瞬間的座標 (X, Y) 與鍵盤操作。腳本檔案極為精簡，回放最穩定，適合一般視窗按鈕點擊、技能連擊與介面操作。
> - **開啟軌跡**：完整記錄游標滑動過程。適用於拖曳操作、繪圖塗鴉或要求平滑路徑的特殊場景。

#### Q2：如何自訂各功能快速鍵？
> 點擊介面上任何標有 `[更改]` 或按鍵名稱的按鈕，按鈕變為金色提示後，直接在鍵盤上按下您想要的鍵，放開後即可完成綁定並進入 0.5 秒防誤觸冷卻。

#### Q3：Windows 下為什麼打字有反應，但滑鼠沒有移動？
> Windows UIPI（使用者介面權限隔離）機制會擋掉低權限程式對高權限視窗的滑鼠控制。請將 CMD 或打包後的程式「以系統管理員身分執行」即可正常運作。

---

## 📄 開源授權 (License)

本專案採用 **[MIT License](LICENSE)** 授權條款，歡迎自由使用與二次開發。

