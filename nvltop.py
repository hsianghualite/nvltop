#!/usr/bin/env python3
import curses
import subprocess
import time
import re
from collections import defaultdict
import argparse

def get_nvlink_counters():
    result = subprocess.run(
        ["nvidia-smi", "nvlink", "-gt", "d"],
        stdout=subprocess.PIPE, text=True
    )
    counters = {}
    current_gpu = None
    for line in result.stdout.splitlines():
        m_gpu = re.match(r"GPU (\d+):", line)
        if m_gpu:
            current_gpu = int(m_gpu[1])
            continue
        m = re.match(r"\s*Link (\d+): Data (Tx|Rx):\s+(\d+) KiB", line)
        if m and current_gpu is not None:
            link = int(m[1])
            direction = m[2].upper()
            value = int(m[3])
            counters[(current_gpu, link, direction)] = value
    return counters

def format_bw(mb_per_s):
    return f"{mb_per_s/1024:.2f} GB/s" if mb_per_s >= 1024 else f"{mb_per_s:.2f} MB/s"

def safe_addstr(stdscr, y, x, text):
    max_y, max_x = stdscr.getmaxyx()
    if y >= max_y:
        return
    if len(text) > max_x - x:
        text = text[:max_x - x - 1]
    try:
        stdscr.addstr(y, x, text)
    except curses.error:
        pass

def main(stdscr, interval):
    curses.curs_set(0)
    stdscr.nodelay(True)
    prev = get_nvlink_counters()
    time.sleep(interval)

    while True:
        curr = get_nvlink_counters()
        stdscr.clear()
        safe_addstr(stdscr, 0, 0, f"NVLINK TOP - 四行两列显示模式 | 刷新间隔 {interval}s | 按 q 退出")

        row = 2
        gpus = sorted({k[0] for k in curr.keys()})
        gpu_totals = defaultdict(lambda: {"RX": 0.0, "TX": 0.0})
        gpu_links = {}
        max_links = 0

        
        for gpu in gpus:
            links = sorted({k[1] for k in curr.keys() if k[0] == gpu})
            gpu_links[gpu] = links
            max_links = max(max_links, len(links))
            for link in links:
                rx = (curr[(gpu, link, "RX")] - prev.get((gpu, link, "RX"), 0)) / 1024 / interval
                tx = (curr[(gpu, link, "TX")] - prev.get((gpu, link, "TX"), 0)) / 1024 / interval
                gpu_totals[gpu]["RX"] += rx
                gpu_totals[gpu]["TX"] += tx

        col_width = 40
        num_cols = 2  
        num_rows = (len(gpus) + num_cols - 1) // num_cols 

        for r in range(num_rows):
            for link_idx in range(max_links):
                line = ""
                for c in range(num_cols):
                    gpu_idx = r * num_cols + c
                    if gpu_idx < len(gpus):
                        gpu = gpus[gpu_idx]
                        links = gpu_links[gpu]
                        if link_idx < len(links):
                            l = links[link_idx]
                            rx = (curr[(gpu, l, "RX")] - prev.get((gpu, l, "RX"), 0)) / 1024 / interval
                            tx = (curr[(gpu, l, "TX")] - prev.get((gpu, l, "TX"), 0)) / 1024 / interval
                            line += f"GPU{gpu}L{l}: RX {format_bw(rx)} TX {format_bw(tx)}".ljust(col_width)
                        else:
                            line += " " * col_width
                safe_addstr(stdscr, row, 0, line)
                row += 1

            line = ""
            for c in range(num_cols):
                gpu_idx = r * num_cols + c
                if gpu_idx < len(gpus):
                    gpu = gpus[gpu_idx]
                    line += f"GPU{gpu} SUM: RX {format_bw(gpu_totals[gpu]['RX'])} TX {format_bw(gpu_totals[gpu]['TX'])}".ljust(col_width)
            safe_addstr(stdscr, row, 0, line)
            row += 2

        global_rx = sum(gpu_totals[gpu]["RX"] for gpu in gpus)
        global_tx = sum(gpu_totals[gpu]["TX"] for gpu in gpus)
        safe_addstr(stdscr, row, 0, f"ALL SUM: RX {format_bw(global_rx)} TX {format_bw(global_tx)}")
        row += 1

        prev = curr
        stdscr.refresh()
        time.sleep(interval)
        key = stdscr.getch()
        if key == ord('q'):
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NVLink Top - 四行两列显示模式，每条 Link 默认显示")
    parser.add_argument("--interval", type=float, default=2.0, help="刷新间隔秒 (默认2秒)")
    args = parser.parse_args()

    curses.wrapper(main, args.interval)

