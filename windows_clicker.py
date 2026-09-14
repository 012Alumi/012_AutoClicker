#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Clicker for Windows (極速自動連點 & 動作錄製高對比版)
特色：
1. Windows 高解析度 DPI 自動適配 (介面字體清晰不模糊)
2. 支援「極速自動連點 (1~1000 CPS)」與「動作錄製 (Macro Recorder)」雙分頁
3. 動作錄製功能：
   - 儲存動作 (自訂名稱保存多組腳本) 與 刪除動作
   - 快速鍵綁定 (預設 F9 錄製開關、F8 執行開關，支援自訂按鍵)
   - 專業穩定錄製：精確記錄鍵盤按鍵與滑鼠點擊瞬間 (X, Y 座標)，自動排除連續移動軌跡，避免延遲
   - 支援重複次數設定 (0 為無限循環) 與倍速回放
4. 放開按鍵確認 + 0.5 秒冷卻防誤觸機制
"""

import os
import sys
import time
import json
import random
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

# Windows 高 DPI 清晰度支援
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button
    from pynput.keyboard import Key, KeyCode
except ImportError:
    print("尚未安裝 pynput，請在 CMD 或 PowerShell 執行：pip install pynput")
    mouse = None
    keyboard = None
    Button = None
    Key = None
    KeyCode = None

# 高對比深色配色盤
C_BG_ROOT    = "#111219"  # 最底層背景 (暗夜黑)
C_BG_CARD    = "#1a1c29"  # 卡片面板底色
C_BG_INPUT   = "#0d0e15"  # 輸入框純黑底色
C_BORDER     = "#2e3247"  # 邊框線條

C_TEXT_WHITE = "#ffffff"  # 純白文字
C_TEXT_CYAN  = "#00e5ff"  # 霓虹青藍
C_TEXT_DIM   = "#7e85a6"  # 淺灰輔助文字
C_TEXT_PURPLE= "#bb9af7"  # 霓虹紫

C_BTN_NORMAL = "#232638"  # 按鈕普通底色
C_BTN_HOVER  = "#31354f"  # 按鈕懸停底色
C_BTN_ACTIVE = "#204a87"  # 選中高亮藍

C_GREEN      = "#00e676"  # 運行狀態綠
C_RED        = "#ff3b5c"  # 停止狀態紅
C_GOLD       = "#ffc107"  # 等待按鍵金

FONT_FAMILY  = "Segoe UI" if sys.platform == "win32" else "Helvetica Neue"

PRESETS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presets.json")
MACROS_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macros.json")


class DarkButton(tk.Label):
    """自訂暗色按鈕：高對比電競風格按鈕"""
    def __init__(self, parent, text, command=None, bg=C_BTN_NORMAL, fg=C_TEXT_WHITE, 
                 hover_bg=C_BTN_HOVER, active_bg=C_BTN_ACTIVE, font=(FONT_FAMILY, 10, "bold"), 
                 padx=10, pady=5, border_color=C_BORDER, **kwargs):
        super().__init__(
            parent, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady,
            relief="solid", bd=1, highlightbackground=border_color, highlightthickness=1,
            cursor="hand2", **kwargs
        )
        self.command = command
        self.default_bg = bg
        self.default_fg = fg
        self.hover_bg = hover_bg
        self.active_bg = active_bg
        self.is_selected = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, e):
        if not self.is_selected:
            self.configure(bg=self.hover_bg)

    def _on_leave(self, e):
        if not self.is_selected:
            self.configure(bg=self.default_bg)

    def _on_click(self, e):
        if self.command:
            self.command()

    def set_selected(self, selected=True, active_fg=C_TEXT_CYAN):
        self.is_selected = selected
        if selected:
            self.configure(bg=self.active_bg, fg=active_fg, highlightbackground=C_TEXT_CYAN)
        else:
            self.configure(bg=self.default_bg, fg=self.default_fg, highlightbackground=C_BORDER)

    def set_text(self, text):
        self.configure(text=text)

    def set_color(self, bg, fg):
        self.default_bg = bg
        self.default_fg = fg
        self.configure(bg=bg, fg=fg)


class WindowsAutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker (Windows)")
        self.root.geometry("480x700")
        self.root.resizable(False, False)
        self.root.configure(bg=C_BG_ROOT)

        # 控制器
        self.mouse_controller = mouse.Controller() if mouse else None
        self.keyboard_controller = keyboard.Controller() if keyboard else None

        # 模式與執行狀態
        self.is_clicking = False
        self.click_thread = None

        self.is_recording_macro = False
        self.is_playing_macro = False
        self.macro_thread = None
        self.macro_mouse_listener = None

        # 熱鍵綁定設定 (預設: 連點 F6, 錄製 F9, 執行 F8)
        self.hotkey_click = Key.f6 if Key else "F6"
        self.hotkey_click_display = "F6"

        self.hotkey_record = Key.f9 if Key else "F9"
        self.hotkey_record_display = "F9"

        self.hotkey_play = Key.f8 if Key else "F8"
        self.hotkey_play_display = "F8"

        self.setting_hotkey_target = None  # "click", "record", "play"
        self.cooldown_until = 0.0

        # 連點控制變數
        self.cps_var = tk.DoubleVar(value=50.0)
        self.selected_mouse_btn = "left"  # left, right, middle
        self.jitter_enabled = False
        self.uncapped_enabled = False

        # 動作錄製變數
        self.record_include_clicks = True  # 包含滑鼠點擊 (不含滑動軌跡)
        self.recorded_events = []          # 臨時錄製事件
        self.saved_macros = self._load_macros() # {name: [events...]}
        self.selected_macro_name = None
        self.macro_loops_var = tk.IntVar(value=1)
        self.macro_speed_var = tk.DoubleVar(value=1.0)

        # 常用檔位載入
        self.presets = self._load_presets()

        self._build_ui()

        # 啟動 pynput 全域按鍵監聽
        if keyboard:
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
        else:
            self.keyboard_listener = None

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ==================== 資料持久化 ====================
    def _load_presets(self):
        default = [15, 25, 50, 100, 200]
        if os.path.exists(PRESETS_FILE):
            try:
                with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        return sorted(list(set(int(x) for x in data if 1 <= x <= 1000)))
            except Exception:
                pass
        return default

    def _save_presets(self):
        try:
            with open(PRESETS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=2)
        except Exception:
            pass

    def _load_macros(self):
        if os.path.exists(MACROS_FILE):
            try:
                with open(MACROS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
        return {}

    def _save_macros(self):
        try:
            with open(MACROS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.saved_macros, f, indent=2)
        except Exception:
            pass

    # ==================== UI 建構 ====================
    def _build_ui(self):
        main = tk.Frame(self.root, bg=C_BG_ROOT, padx=14, pady=12)
        main.pack(fill=tk.BOTH, expand=True)

        # 分頁切換列
        tab_bar = tk.Frame(main, bg=C_BG_ROOT)
        tab_bar.pack(fill=tk.X, pady=(0, 10))

        self.tab_btn_clicker = DarkButton(
            tab_bar, text="⚡ 自動連點 (Clicker)", 
            command=lambda: self._switch_tab("clicker"),
            font=(FONT_FAMILY, 10, "bold"), padx=14, pady=6
        )
        self.tab_btn_clicker.pack(side=tk.LEFT, padx=(0, 8))

        self.tab_btn_recorder = DarkButton(
            tab_bar, text="🎬 動作錄製 (Action Recorder)", 
            command=lambda: self._switch_tab("recorder"),
            font=(FONT_FAMILY, 10, "bold"), padx=14, pady=6
        )
        self.tab_btn_recorder.pack(side=tk.LEFT)

        # 頂部全域狀態卡片
        self.status_card = tk.Frame(
            main, bg=C_BG_CARD, highlightbackground=C_BORDER, 
            highlightthickness=1, padx=10, pady=10
        )
        self.status_card.pack(fill=tk.X, pady=(0, 10))

        self.status_label = tk.Label(
            self.status_card, text=f"● 停止中 (按 [{self.hotkey_click_display}] 啟動連點)",
            font=(FONT_FAMILY, 12, "bold"), fg=C_RED, bg=C_BG_CARD
        )
        self.status_label.pack()

        # 分頁容器
        self.container = tk.Frame(main, bg=C_BG_ROOT)
        self.container.pack(fill=tk.BOTH, expand=True)

        # 分頁 1: 連點介面
        self.frame_clicker = tk.Frame(self.container, bg=C_BG_ROOT)
        self._build_clicker_tab(self.frame_clicker)

        # 分頁 2: 動作錄製介面
        self.frame_recorder = tk.Frame(self.container, bg=C_BG_ROOT)
        self._build_recorder_tab(self.frame_recorder)

        # 預設選中連點分頁
        self._switch_tab("clicker")

    def _switch_tab(self, tab_name):
        if tab_name == "clicker":
            self.frame_recorder.pack_forget()
            self.frame_clicker.pack(fill=tk.BOTH, expand=True)
            self.tab_btn_clicker.set_selected(True)
            self.tab_btn_recorder.set_selected(False)
            self._update_status_display()
        else:
            self.frame_clicker.pack_forget()
            self.frame_recorder.pack(fill=tk.BOTH, expand=True)
            self.tab_btn_clicker.set_selected(False)
            self.tab_btn_recorder.set_selected(True)
            self._update_status_display()

    # ---------- 分頁 1: 自動連點 UI ----------
    def _build_clicker_tab(self, parent):
        preset_card = tk.Frame(
            parent, bg=C_BG_CARD, highlightbackground=C_BORDER,
            highlightthickness=1, padx=12, pady=8
        )
        preset_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            preset_card, text="⚡ 常用 CPS 檔位管理 (點擊立即切換)", 
            font=(FONT_FAMILY, 10, "bold"), fg=C_TEXT_CYAN, bg=C_BG_CARD
        ).pack(anchor=tk.W, pady=(0, 6))

        self.preset_box = tk.Frame(preset_card, bg=C_BG_CARD)
        self.preset_box.pack(fill=tk.X, pady=(0, 6))
        self._render_presets()

        preset_bar = tk.Frame(preset_card, bg=C_BG_CARD)
        preset_bar.pack(fill=tk.X)

        DarkButton(
            preset_bar, text="➕ 儲存當前 CPS 為檔位", font=(FONT_FAMILY, 9, "bold"),
            bg="#163828", fg=C_GREEN, hover_bg="#1d4d37", padx=8, pady=4,
            command=self._add_current_preset
        ).pack(side=tk.LEFT)

        DarkButton(
            preset_bar, text="🗑️ 刪除檔位", font=(FONT_FAMILY, 9),
            bg="#3d1822", fg=C_RED, hover_bg="#54212e", padx=8, pady=4,
            command=self._delete_preset_dialog
        ).pack(side=tk.RIGHT)

        # 點擊速率微調
        cps_card = tk.Frame(
            parent, bg=C_BG_CARD, highlightbackground=C_BORDER,
            highlightthickness=1, padx=12, pady=10
        )
        cps_card.pack(fill=tk.X, pady=(0, 10))

        cps_head = tk.Frame(cps_card, bg=C_BG_CARD)
        cps_head.pack(fill=tk.X)

        tk.Label(
            cps_head, text="每秒點擊次數 (1 ~ 1,000 CPS):", 
            font=(FONT_FAMILY, 10, "bold"), fg=C_TEXT_WHITE, bg=C_BG_CARD
        ).pack(side=tk.LEFT)

        self.cps_entry = tk.Entry(
            cps_head, textvariable=self.cps_var, width=7, font=(FONT_FAMILY, 12, "bold"),
            bg=C_BG_INPUT, fg=C_TEXT_CYAN, insertbackground=C_TEXT_CYAN,
            relief="solid", bd=1, highlightbackground=C_BORDER, highlightcolor=C_TEXT_CYAN,
            justify=tk.CENTER
        )
        self.cps_entry.pack(side=tk.RIGHT)
        self.cps_entry.bind("<Return>", lambda e: self._on_cps_change())
        self.cps_entry.bind("<FocusOut>", lambda e: self._on_cps_change())

        self.cps_scale = tk.Scale(
            cps_card, from_=1.0, to=500.0, variable=self.cps_var, orient=tk.HORIZONTAL,
            showvalue=False, bg=C_BG_CARD, fg=C_TEXT_WHITE, troughcolor=C_BG_INPUT,
            highlightthickness=0, activebackground=C_TEXT_CYAN,
            command=lambda v: self.cps_var.set(round(float(v), 0))
        )
        self.cps_scale.pack(fill=tk.X, pady=(8, 8))

        toggle_frame = tk.Frame(cps_card, bg=C_BG_CARD)
        toggle_frame.pack(fill=tk.X)

        self.uncapped_toggle_btn = DarkButton(
            toggle_frame, text="⚡ 極速狂暴模式：關閉", font=(FONT_FAMILY, 9, "bold"),
            bg="#251833", fg="#d19a66", hover_bg="#38244f", padx=8, pady=4,
            command=self._toggle_uncapped
        )
        self.uncapped_toggle_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.jitter_toggle_btn = DarkButton(
            toggle_frame, text="隨機延遲 (Jitter)：關閉", font=(FONT_FAMILY, 9),
            bg=C_BTN_NORMAL, fg=C_TEXT_DIM, hover_bg=C_BTN_HOVER, padx=8, pady=4,
            command=self._toggle_jitter
        )
        self.jitter_toggle_btn.pack(side=tk.LEFT)

        # 按鍵與熱鍵設定
        key_card = tk.Frame(
            parent, bg=C_BG_CARD, highlightbackground=C_BORDER,
            highlightthickness=1, padx=12, pady=10
        )
        key_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            key_card, text="⚙️ 模擬按鍵與切換熱鍵", 
            font=(FONT_FAMILY, 10, "bold"), fg=C_TEXT_CYAN, bg=C_BG_CARD
        ).pack(anchor=tk.W, pady=(0, 8))

        mouse_row = tk.Frame(key_card, bg=C_BG_CARD)
        mouse_row.pack(fill=tk.X, pady=(0, 8))
        tk.Label(mouse_row, text="連點按鍵:", font=(FONT_FAMILY, 10), fg=C_TEXT_WHITE, bg=C_BG_CARD).pack(side=tk.LEFT)

        self.btn_left = DarkButton(mouse_row, text="左鍵 (Left)", command=lambda: self._select_mouse("left"), padx=8, pady=3)
        self.btn_left.pack(side=tk.LEFT, padx=(8, 3))
        self.btn_right = DarkButton(mouse_row, text="右鍵 (Right)", command=lambda: self._select_mouse("right"), padx=8, pady=3)
        self.btn_right.pack(side=tk.LEFT, padx=3)
        self.btn_middle = DarkButton(mouse_row, text="滾輪中鍵", command=lambda: self._select_mouse("middle"), padx=8, pady=3)
        self.btn_middle.pack(side=tk.LEFT, padx=3)
        self._select_mouse("left")

        hotkey_row = tk.Frame(key_card, bg=C_BG_CARD)
        hotkey_row.pack(fill=tk.X)
        tk.Label(hotkey_row, text="連點開關熱鍵:", font=(FONT_FAMILY, 10), fg=C_TEXT_WHITE, bg=C_BG_CARD).pack(side=tk.LEFT)

        self.hotkey_btn_click = DarkButton(
            hotkey_row, text=f"[{self.hotkey_click_display}] 點我更改熱鍵", font=(FONT_FAMILY, 10, "bold"),
            bg="#2a2e45", fg=C_TEXT_CYAN, hover_bg="#353b59", padx=12, pady=4,
            command=lambda: self._start_listen_hotkey("click")
        )
        self.hotkey_btn_click.pack(side=tk.RIGHT)

        self.main_btn_click = DarkButton(
            parent, text="▶ 啟動連點 (或按熱鍵)", font=(FONT_FAMILY, 12, "bold"),
            bg="#1d3b66", fg=C_TEXT_WHITE, hover_bg="#274f8a", pady=10,
            command=self.toggle_clicking
        )
        self.main_btn_click.pack(fill=tk.X, pady=(4, 0))

    # ---------- 分頁 2: 動作錄製 UI ----------
    def _build_recorder_tab(self, parent):
        hk_card = tk.Frame(
            parent, bg=C_BG_CARD, highlightbackground=C_BORDER,
            highlightthickness=1, padx=12, pady=10
        )
        hk_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            hk_card, text="🎯 動作錄製與執行快速鍵 (按一下開始，再按一下結束)", 
            font=(FONT_FAMILY, 10, "bold"), fg=C_TEXT_PURPLE, bg=C_BG_CARD
        ).pack(anchor=tk.W, pady=(0, 8))

        row1 = tk.Frame(hk_card, bg=C_BG_CARD)
        row1.pack(fill=tk.X, pady=(0, 6))
        tk.Label(row1, text="錄製開關熱鍵:", font=(FONT_FAMILY, 10), fg=C_TEXT_WHITE, bg=C_BG_CARD).pack(side=tk.LEFT)
        self.hotkey_btn_record = DarkButton(
            row1, text=f"[{self.hotkey_record_display}] 點我更改熱鍵", font=(FONT_FAMILY, 9, "bold"),
            bg="#2a2e45", fg=C_TEXT_PURPLE, hover_bg="#353b59", padx=10, pady=3,
            command=lambda: self._start_listen_hotkey("record")
        )
        self.hotkey_btn_record.pack(side=tk.RIGHT)

        row2 = tk.Frame(hk_card, bg=C_BG_CARD)
        row2.pack(fill=tk.X, pady=(0, 6))
        tk.Label(row2, text="回放執行熱鍵:", font=(FONT_FAMILY, 10), fg=C_TEXT_WHITE, bg=C_BG_CARD).pack(side=tk.LEFT)
        self.hotkey_btn_play = DarkButton(
            row2, text=f"[{self.hotkey_play_display}] 點我更改熱鍵", font=(FONT_FAMILY, 9, "bold"),
            bg="#2a2e45", fg=C_TEXT_CYAN, hover_bg="#353b59", padx=10, pady=3,
            command=lambda: self._start_listen_hotkey("play")
        )
        self.hotkey_btn_play.pack(side=tk.RIGHT)

        row3 = tk.Frame(hk_card, bg=C_BG_CARD)
        row3.pack(fill=tk.X, pady=(4, 0))
        tk.Label(row3, text="錄製範圍:", font=(FONT_FAMILY, 10), fg=C_TEXT_WHITE, bg=C_BG_CARD).pack(side=tk.LEFT)
        
        self.btn_toggle_mouse_record = DarkButton(
            row3, text="✓ 鍵盤 + 滑鼠點擊瞬間", font=(FONT_FAMILY, 9, "bold"),
            bg="#163828", fg=C_GREEN, hover_bg="#1d4d37", padx=8, pady=3,
            command=self._toggle_mouse_recording
        )
        self.btn_toggle_mouse_record.pack(side=tk.RIGHT)

        # 動作管理卡片
        mgmt_card = tk.Frame(
            parent, bg=C_BG_CARD, highlightbackground=C_BORDER,
            highlightthickness=1, padx=12, pady=10
        )
        mgmt_card.pack(fill=tk.X, pady=(0, 10))

        mgmt_head = tk.Frame(mgmt_card, bg=C_BG_CARD)
        mgmt_head.pack(fill=tk.X, pady=(0, 6))
        tk.Label(
            mgmt_head, text="📁 已儲存動作腳本清單", 
            font=(FONT_FAMILY, 10, "bold"), fg=C_TEXT_CYAN, bg=C_BG_CARD
        ).pack(side=tk.LEFT)

        self.current_rec_label = tk.Label(
            mgmt_head, text="目前未錄製動作", font=(FONT_FAMILY, 9), fg=C_TEXT_DIM, bg=C_BG_CARD
        )
        self.current_rec_label.pack(side=tk.RIGHT)

        self.macro_listbox = tk.Listbox(
            mgmt_card, height=4, font=(FONT_FAMILY, 10),
            bg=C_BG_INPUT, fg=C_TEXT_CYAN, selectbackground=C_BTN_ACTIVE, selectforeground=C_TEXT_WHITE,
            relief="solid", bd=1, highlightbackground=C_BORDER, highlightthickness=1
        )
        self.macro_listbox.pack(fill=tk.X, pady=(0, 8))
        self.macro_listbox.bind("<<ListboxSelect>>", self._on_macro_selected)
        self._refresh_macro_list()

        act_bar = tk.Frame(mgmt_card, bg=C_BG_CARD)
        act_bar.pack(fill=tk.X)

        DarkButton(
            act_bar, text="💾 儲存目前錄製", font=(FONT_FAMILY, 9, "bold"),
            bg="#163828", fg=C_GREEN, hover_bg="#1d4d37", padx=10, pady=4,
            command=self._save_current_macro_dialog
        ).pack(side=tk.LEFT)

        DarkButton(
            act_bar, text="🗑️ 刪除選取動作", font=(FONT_FAMILY, 9),
            bg="#3d1822", fg=C_RED, hover_bg="#54212e", padx=10, pady=4,
            command=self._delete_selected_macro
        ).pack(side=tk.RIGHT)

        # 回放設定卡片
        opt_card = tk.Frame(
            parent, bg=C_BG_CARD, highlightbackground=C_BORDER,
            highlightthickness=1, padx=12, pady=10
        )
        opt_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            opt_card, text="⚙️ 回放設定", 
            font=(FONT_FAMILY, 10, "bold"), fg=C_TEXT_WHITE, bg=C_BG_CARD
        ).pack(anchor=tk.W, pady=(0, 6))

        opt_row = tk.Frame(opt_card, bg=C_BG_CARD)
        opt_row.pack(fill=tk.X)

        tk.Label(opt_row, text="重複次數 (0=無限循環):", font=(FONT_FAMILY, 9), fg=C_TEXT_DIM, bg=C_BG_CARD).pack(side=tk.LEFT)
        self.loops_entry = tk.Entry(
            opt_row, textvariable=self.macro_loops_var, width=5, font=(FONT_FAMILY, 10, "bold"),
            bg=C_BG_INPUT, fg=C_TEXT_CYAN, insertbackground=C_TEXT_CYAN,
            relief="solid", bd=1, highlightbackground=C_BORDER, justify=tk.CENTER
        )
        self.loops_entry.pack(side=tk.LEFT, padx=(6, 16))

        tk.Label(opt_row, text="回放速度:", font=(FONT_FAMILY, 9), fg=C_TEXT_DIM, bg=C_BG_CARD).pack(side=tk.LEFT)
        for spd in [1.0, 1.5, 2.0]:
            btn = DarkButton(
                opt_row, text=f"{spd}x", font=(FONT_FAMILY, 9),
                padx=6, pady=2, command=lambda s=spd: self._set_macro_speed(s)
            )
            btn.pack(side=tk.LEFT, padx=2)

        ctrl_frame = tk.Frame(parent, bg=C_BG_ROOT)
        ctrl_frame.pack(fill=tk.X, pady=(4, 0))

        self.btn_main_record = DarkButton(
            ctrl_frame, text=f"⏺ 開始錄製 (按 [{self.hotkey_record_display}])", font=(FONT_FAMILY, 11, "bold"),
            bg="#351829", fg=C_RED, hover_bg="#4a1e38", pady=10,
            command=self.toggle_recording
        )
        self.btn_main_record.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_main_play = DarkButton(
            ctrl_frame, text=f"▶ 執行動作 (按 [{self.hotkey_play_display}])", font=(FONT_FAMILY, 11, "bold"),
            bg="#1d3b66", fg=C_TEXT_WHITE, hover_bg="#274f8a", pady=10,
            command=self.toggle_macro_playback
        )
        self.btn_main_play.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    # ==================== 動作錄製邏輯 ====================
    def _toggle_mouse_recording(self):
        self.record_include_clicks = not self.record_include_clicks
        if self.record_include_clicks:
            self.btn_toggle_mouse_record.set_color("#163828", C_GREEN)
            self.btn_toggle_mouse_record.set_text("✓ 鍵盤 + 滑鼠點擊瞬間")
        else:
            self.btn_toggle_mouse_record.set_color(C_BTN_NORMAL, C_TEXT_DIM)
            self.btn_toggle_mouse_record.set_text("僅錄製鍵盤按鍵")

    def _set_macro_speed(self, speed):
        self.macro_speed_var.set(speed)

    def _refresh_macro_list(self):
        self.macro_listbox.delete(0, tk.END)
        names = list(self.saved_macros.keys())
        for name in names:
            cnt = len(self.saved_macros[name])
            self.macro_listbox.insert(tk.END, f"📌 {name} ({cnt} 個動作)")
        if names:
            self.macro_listbox.select_set(0)
            self.selected_macro_name = names[0]
        else:
            self.selected_macro_name = None

    def _on_macro_selected(self, event):
        sel = self.macro_listbox.curselection()
        if sel:
            idx = sel[0]
            names = list(self.saved_macros.keys())
            if 0 <= idx < len(names):
                self.selected_macro_name = names[idx]
                self.recorded_events = list(self.saved_macros[self.selected_macro_name])
                self.current_rec_label.config(
                    text=f"選中: {self.selected_macro_name} ({len(self.recorded_events)} 動作)",
                    fg=C_TEXT_CYAN
                )

    def _save_current_macro_dialog(self):
        if not self.recorded_events:
            messagebox.showwarning("提示", "目前沒有任何錄製的動作！\n請先按下錄製快速鍵錄製動作。")
            return
        name = simpledialog.askstring(
            "儲存動作腳本", 
            f"目前記錄了 {len(self.recorded_events)} 個動作事件。\n\n請輸入此動作腳本的名稱：",
            parent=self.root
        )
        if name:
            name = name.strip()
            if not name:
                return
            self.saved_macros[name] = list(self.recorded_events)
            self._save_macros()
            self._refresh_macro_list()
            names = list(self.saved_macros.keys())
            if name in names:
                idx = names.index(name)
                self.macro_listbox.select_clear(0, tk.END)
                self.macro_listbox.select_set(idx)
                self.selected_macro_name = name
                self.current_rec_label.config(
                    text=f"已儲存: {name} ({len(self.recorded_events)} 動作)", fg=C_GREEN
                )
            messagebox.showinfo("成功", f"動作腳本「{name}」已成功儲存！")

    def _delete_selected_macro(self):
        if not self.selected_macro_name or self.selected_macro_name not in self.saved_macros:
            messagebox.showwarning("提示", "請先在清單中選擇要刪除的動作腳本！")
            return
        if messagebox.askyesno("確認刪除", f"確定要刪除動作「{self.selected_macro_name}」嗎？"):
            del self.saved_macros[self.selected_macro_name]
            self._save_macros()
            self._refresh_macro_list()
            self.recorded_events = []
            self.current_rec_label.config(text="已刪除，請重新錄製或選取", fg=C_RED)

    def toggle_recording(self):
        if self.is_recording_macro:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        if self.is_recording_macro:
            return
        if self.is_clicking:
            self.stop_clicking()
        if self.is_playing_macro:
            self.stop_macro_playback()

        self.recorded_events = []
        self.is_recording_macro = True
        self._record_start_time = time.perf_counter()

        if mouse and self.record_include_clicks:
            self.macro_mouse_listener = mouse.Listener(on_click=self._on_recorded_mouse_click)
            self.macro_mouse_listener.daemon = True
            self.macro_mouse_listener.start()

        self.btn_main_record.set_color("#8a1c29", C_TEXT_WHITE)
        self.btn_main_record.set_text(f"⏹ 結束錄製 (按 [{self.hotkey_record_display}])")
        self.current_rec_label.config(text="🔴 錄製中 (0 動作)...", fg=C_RED)
        self._update_status_display()

    def stop_recording(self):
        if not self.is_recording_macro:
            return
        self.is_recording_macro = False

        if self.macro_mouse_listener:
            try:
                self.macro_mouse_listener.stop()
            except Exception:
                pass
            self.macro_mouse_listener = None

        if self.recorded_events and self.recorded_events[-1].get("type") in ("key_down", "key_up"):
            last_key = self.recorded_events[-1].get("key")
            if last_key and self._is_same_serialized_key(last_key, self.hotkey_record):
                self.recorded_events.pop()

        self.btn_main_record.set_color("#351829", C_RED)
        self.btn_main_record.set_text(f"⏺ 開始錄製 (按 [{self.hotkey_record_display}])")
        cnt = len(self.recorded_events)
        self.current_rec_label.config(text=f"● 錄製完成：共 {cnt} 個動作", fg=C_GREEN)
        self._update_status_display()

    def _on_recorded_mouse_click(self, x, y, button, pressed):
        if not self.is_recording_macro:
            return
        t = time.perf_counter() - self._record_start_time
        btn_str = button.name if hasattr(button, 'name') else str(button)
        self.recorded_events.append({
            "type": "mouse_click",
            "button": btn_str,
            "pressed": pressed,
            "x": int(x),
            "y": int(y),
            "time": t
        })
        self.root.after(0, self._update_rec_label)

    def _update_rec_label(self):
        if self.is_recording_macro:
            self.current_rec_label.config(text=f"🔴 錄製中 ({len(self.recorded_events)} 動作)...", fg=C_RED)

    # ==================== 動作回放邏輯 ====================
    def toggle_macro_playback(self):
        if self.is_playing_macro:
            self.stop_macro_playback()
        else:
            self.start_macro_playback()

    def start_macro_playback(self):
        if self.is_playing_macro:
            return
        if self.is_recording_macro:
            self.stop_recording()
        if self.is_clicking:
            self.stop_clicking()

        events_to_play = self.recorded_events
        if not events_to_play and self.selected_macro_name and self.selected_macro_name in self.saved_macros:
            events_to_play = self.saved_macros[self.selected_macro_name]

        if not events_to_play:
            messagebox.showwarning("提示", "尚未選擇或錄製任何動作！\n請先進行錄製或於清單中選擇動作腳本。")
            return

        self.is_playing_macro = True
        self.btn_main_play.set_color("#781d28", C_TEXT_WHITE)
        self.btn_main_play.set_text(f"⏹ 停止執行 (按 [{self.hotkey_play_display}])")
        self._update_status_display()

        self.macro_thread = threading.Thread(
            target=self._macro_playback_loop, args=(list(events_to_play),), daemon=True
        )
        self.macro_thread.start()

    def stop_macro_playback(self):
        self.is_playing_macro = False
        self.btn_main_play.set_color("#1d3b66", C_TEXT_WHITE)
        self.btn_main_play.set_text(f"▶ 執行動作 (按 [{self.hotkey_play_display}])")
        self._release_all_controls()
        self._update_status_display()

    def _macro_playback_loop(self, events):
        if not events:
            self.root.after(0, self.stop_macro_playback)
            return

        try:
            loops = max(0, int(self.macro_loops_var.get()))
        except ValueError:
            loops = 1

        speed = max(0.1, float(self.macro_speed_var.get()))
        cur_loop = 0

        while self.is_playing_macro:
            cur_loop += 1
            loop_msg = f"無限循環" if loops == 0 else f"第 {cur_loop}/{loops} 次"
            self.root.after(0, lambda m=loop_msg: self.status_label.config(
                text=f"▶ 回放執行中 ({m}，按 [{self.hotkey_play_display}] 停止)", fg=C_GREEN
            ))

            start_t = time.perf_counter()
            for evt in events:
                if not self.is_playing_macro:
                    break

                target_t = evt.get("time", 0.0) / speed
                while self.is_playing_macro:
                    elapsed = time.perf_counter() - start_t
                    rem = target_t - elapsed
                    if rem <= 0:
                        break
                    if rem > 0.005:
                        time.sleep(min(rem - 0.002, 0.02))

                if not self.is_playing_macro:
                    break

                self._dispatch_macro_event(evt)

            if loops > 0 and cur_loop >= loops:
                break

            if self.is_playing_macro and (loops == 0 or cur_loop < loops):
                time.sleep(0.05)

        self.root.after(0, self.stop_macro_playback)

    def _dispatch_macro_event(self, evt):
        etype = evt.get("type")
        if etype == "key_down":
            k = self._deserialize_key(evt.get("key"))
            if k and self.keyboard_controller:
                try:
                    self.keyboard_controller.press(k)
                except Exception:
                    pass
        elif etype == "key_up":
            k = self._deserialize_key(evt.get("key"))
            if k and self.keyboard_controller:
                try:
                    self.keyboard_controller.release(k)
                except Exception:
                    pass
        elif etype == "mouse_click":
            btn_str = evt.get("button", "left")
            btn = Button.left if btn_str == "left" else (Button.right if btn_str == "right" else Button.middle)
            x = evt.get("x")
            y = evt.get("y")
            pressed = evt.get("pressed", False)
            if self.mouse_controller:
                try:
                    if x is not None and y is not None:
                        self.mouse_controller.position = (x, y)
                    if pressed:
                        self.mouse_controller.press(btn)
                    else:
                        self.mouse_controller.release(btn)
                except Exception:
                    pass

    def _release_all_controls(self):
        if self.mouse_controller and Button:
            for b in [Button.left, Button.right, Button.middle]:
                try:
                    self.mouse_controller.release(b)
                except Exception:
                    pass

    # ==================== 按鍵序列化與比較 ====================
    def _serialize_key(self, key):
        if Key and isinstance(key, Key):
            return {"special": True, "name": key.name}
        elif KeyCode and isinstance(key, KeyCode):
            return {"special": False, "char": key.char, "vk": getattr(key, 'vk', None)}
        return {"special": True, "name": str(key).replace("Key.", "")}

    def _deserialize_key(self, data):
        if not data:
            return None
        if data.get("special"):
            name = data.get("name")
            return getattr(Key, name, None) if Key else None
        else:
            char = data.get("char")
            vk = data.get("vk")
            if KeyCode:
                if char:
                    return KeyCode.from_char(char)
                elif vk is not None:
                    return KeyCode.from_vk(vk)
        return None

    def _is_same_key(self, k1, k2):
        if k1 is None or k2 is None:
            return False
        if KeyCode and isinstance(k1, KeyCode) and isinstance(k2, KeyCode):
            if k1.char and k2.char:
                return k1.char.lower() == k2.char.lower()
            if getattr(k1, 'vk', None) and getattr(k2, 'vk', None):
                return k1.vk == k2.vk
        return k1 == k2

    def _is_same_serialized_key(self, s_key, normal_key):
        if not s_key or not normal_key:
            return False
        des = self._deserialize_key(s_key)
        return self._is_same_key(des, normal_key)

    def _format_key(self, key):
        if hasattr(key, 'char') and key.char:
            return key.char.upper()
        if hasattr(key, 'name') and key.name:
            return key.name.upper()
        return str(key).replace("Key.", "").upper()

    # ==================== 熱鍵配置 ====================
    def _start_listen_hotkey(self, target):
        if self.is_clicking:
            self.stop_clicking()
        if self.is_recording_macro:
            self.stop_recording()
        if self.is_playing_macro:
            self.stop_macro_playback()

        self.setting_hotkey_target = target
        if target == "click":
            self.hotkey_btn_click.set_color("#473611", C_GOLD)
            self.hotkey_btn_click.set_text("👉 請按下任一鍵...")
        elif target == "record":
            self.hotkey_btn_record.set_color("#473611", C_GOLD)
            self.hotkey_btn_record.set_text("👉 請按下任一鍵...")
        elif target == "play":
            self.hotkey_btn_play.set_color("#473611", C_GOLD)
            self.hotkey_btn_play.set_text("👉 請按下任一鍵...")

        self.status_label.config(text="🟡 等待按鍵中...請按下欲綁定的按鍵 (放開確認)", fg=C_GOLD)

    def _on_key_press(self, key):
        if self.setting_hotkey_target:
            self._pending_key = key
            return

        if time.time() < self.cooldown_until:
            return

        if self._is_same_key(key, self.hotkey_record):
            self.root.after(0, self.toggle_recording)
            return

        if self._is_same_key(key, self.hotkey_play):
            self.root.after(0, self.toggle_macro_playback)
            return

        if self._is_same_key(key, self.hotkey_click):
            self.root.after(0, self.toggle_clicking)
            return

        if self.is_recording_macro:
            t = time.perf_counter() - self._record_start_time
            self.recorded_events.append({
                "type": "key_down",
                "key": self._serialize_key(key),
                "time": t
            })
            self.root.after(0, self._update_rec_label)

    def _on_key_release(self, key):
        if self.setting_hotkey_target and hasattr(self, '_pending_key') and self._pending_key == key:
            target = self.setting_hotkey_target
            display = self._format_key(key)
            self.setting_hotkey_target = None
            self.cooldown_until = time.time() + 0.5

            if target == "click":
                self.hotkey_click = key
                self.hotkey_click_display = display
                self.root.after(0, lambda: self.hotkey_btn_click.set_color("#2a2e45", C_TEXT_CYAN))
                self.root.after(0, lambda: self.hotkey_btn_click.set_text(f"[{display}] 點我更改熱鍵"))
            elif target == "record":
                self.hotkey_record = key
                self.hotkey_record_display = display
                self.root.after(0, lambda: self.hotkey_btn_record.set_color("#2a2e45", C_TEXT_PURPLE))
                self.root.after(0, lambda: self.hotkey_btn_record.set_text(f"[{display}] 點我更改熱鍵"))
                self.root.after(0, lambda: self.btn_main_record.set_text(f"⏺ 開始錄製 (按 [{display}])"))
            elif target == "play":
                self.hotkey_play = key
                self.hotkey_play_display = display
                self.root.after(0, lambda: self.hotkey_btn_play.set_color("#2a2e45", C_TEXT_CYAN))
                self.root.after(0, lambda: self.hotkey_btn_play.set_text(f"[{display}] 點我更改熱鍵"))
                self.root.after(0, lambda: self.btn_main_play.set_text(f"▶ 執行動作 (按 [{display}])"))

            self.root.after(0, self._update_status_display)
            return

        if self.is_recording_macro:
            if not self._is_same_key(key, self.hotkey_record):
                t = time.perf_counter() - self._record_start_time
                self.recorded_events.append({
                    "type": "key_up",
                    "key": self._serialize_key(key),
                    "time": t
                })

    def _update_status_display(self):
        if self.is_clicking:
            txt = "⚡ 狂暴連點中..." if self.uncapped_enabled else f"● 連點中 ({int(self.cps_var.get())} CPS)"
            self.status_label.config(text=f"{txt} (按 [{self.hotkey_click_display}] 停止)", fg=C_GREEN)
        elif self.is_recording_macro:
            self.status_label.config(
                text=f"🔴 動作錄製中... (按 [{self.hotkey_record_display}] 結束錄製)", fg=C_RED
            )
        elif self.is_playing_macro:
            self.status_label.config(
                text=f"▶ 動作執行中... (按 [{self.hotkey_play_display}] 停止)", fg=C_GREEN
            )
        else:
            self.status_label.config(
                text=f"● 待機中 (連點 [{self.hotkey_click_display}] / 錄製 [{self.hotkey_record_display}] / 執行 [{self.hotkey_play_display}])", 
                fg=C_TEXT_DIM
            )

    # ==================== 連點相關邏輯 ====================
    def _render_presets(self):
        for w in self.preset_box.winfo_children():
            w.destroy()
        for val in self.presets:
            btn = DarkButton(
                self.preset_box, text=f"{val} CPS", font=(FONT_FAMILY, 9, "bold"),
                bg=C_BTN_NORMAL, fg=C_TEXT_CYAN, hover_bg=C_BTN_HOVER, padx=7, pady=3,
                command=lambda v=val: self._apply_preset(v)
            )
            btn.pack(side=tk.LEFT, padx=3, pady=2)
            btn.bind("<Button-2>", lambda e, v=val: self._delete_preset(v))
            btn.bind("<Button-3>", lambda e, v=val: self._delete_preset(v))

    def _apply_preset(self, val):
        self.uncapped_enabled = False
        self._update_uncapped_ui()
        self.cps_var.set(float(val))

    def _add_current_preset(self):
        val = int(round(float(self.cps_var.get()), 0))
        if val in self.presets:
            messagebox.showinfo("提示", f"檔位 {val} CPS 已經存在！")
            return
        self.presets.append(val)
        self.presets.sort()
        self._save_presets()
        self._render_presets()

    def _delete_preset(self, val):
        if len(self.presets) <= 1:
            messagebox.showwarning("提示", "至少需保留一個檔位！")
            return
        if messagebox.askyesno("刪除確認", f"確定要刪除 {val} CPS 檔位嗎？"):
            self.presets.remove(val)
            self._save_presets()
            self._render_presets()

    def _delete_preset_dialog(self):
        if len(self.presets) <= 1:
            messagebox.showwarning("提示", "至少需保留一個檔位！")
            return
        options = ", ".join(str(x) for x in self.presets)
        ans = simpledialog.askinteger("刪除檔位", f"目前檔位：{options}\n\n請輸入要刪除的數值：", parent=self.root)
        if ans and ans in self.presets:
            self._delete_preset(ans)
        elif ans:
            messagebox.showerror("錯誤", f"找不到 {ans} CPS 檔位！")

    def _on_cps_change(self):
        try:
            val = float(self.cps_var.get())
            self.cps_var.set(round(max(1.0, min(val, 1000.0)), 0))
        except ValueError:
            self.cps_var.set(50.0)

    def _toggle_uncapped(self):
        self.uncapped_enabled = not self.uncapped_enabled
        self._update_uncapped_ui()

    def _update_uncapped_ui(self):
        if self.uncapped_enabled:
            self.uncapped_toggle_btn.set_color("#4a1525", C_RED)
            self.uncapped_toggle_btn.set_text("⚡ 極速狂暴模式：開啟")
            self.cps_entry.config(state="disabled")
            self.cps_scale.config(state="disabled")
        else:
            self.uncapped_toggle_btn.set_color("#251833", "#d19a66")
            self.uncapped_toggle_btn.set_text("⚡ 極速狂暴模式：關閉")
            self.cps_entry.config(state="normal")
            self.cps_scale.config(state="normal")

    def _toggle_jitter(self):
        self.jitter_enabled = not self.jitter_enabled
        if self.jitter_enabled:
            self.jitter_toggle_btn.set_color("#163828", C_GREEN)
            self.jitter_toggle_btn.set_text("隨機延遲 (Jitter)：開啟")
        else:
            self.jitter_toggle_btn.set_color(C_BTN_NORMAL, C_TEXT_DIM)
            self.jitter_toggle_btn.set_text("隨機延遲 (Jitter)：關閉")

    def _select_mouse(self, btn_type):
        self.selected_mouse_btn = btn_type
        self.btn_left.set_selected(btn_type == "left")
        self.btn_right.set_selected(btn_type == "right")
        self.btn_middle.set_selected(btn_type == "middle")

    def _get_button(self):
        if not Button:
            return None
        if self.selected_mouse_btn == "right":
            return Button.right
        elif self.selected_mouse_btn == "middle":
            return Button.middle
        return Button.left

    def toggle_clicking(self):
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        if self.is_clicking:
            return
        if self.is_recording_macro:
            self.stop_recording()
        if self.is_playing_macro:
            self.stop_macro_playback()

        self.is_clicking = True
        self.main_btn_click.set_color("#781d28", C_TEXT_WHITE)
        self.main_btn_click.set_text(f"⏹ 停止連點 (按 [{self.hotkey_click_display}])")
        self._update_status_display()

        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        self.is_clicking = False
        self.main_btn_click.set_color("#1d3b66", C_TEXT_WHITE)
        self.main_btn_click.set_text(f"▶ 啟動連點 (按 [{self.hotkey_click_display}])")
        self._update_status_display()

    def _click_loop(self):
        if not self.mouse_controller:
            return
        btn = self._get_button()

        if self.uncapped_enabled:
            while self.is_clicking:
                self.mouse_controller.click(btn)
            return

        try:
            target_cps = float(self.cps_var.get())
        except ValueError:
            target_cps = 50.0

        interval = 1.0 / max(1.0, target_cps)
        next_click = time.perf_counter()

        while self.is_clicking:
            self.mouse_controller.click(btn)
            delay = interval + (random.uniform(-0.1, 0.1) * interval if self.jitter_enabled else 0)
            next_click += delay

            while self.is_clicking:
                rem = next_click - time.perf_counter()
                if rem <= 0:
                    break
                if rem > 0.002:
                    time.sleep(0.001)

    def _on_close(self):
        self.stop_clicking()
        self.stop_recording()
        self.stop_macro_playback()
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WindowsAutoClickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
