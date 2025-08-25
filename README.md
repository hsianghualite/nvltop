README.md
# nvltop

A lightweight terminal-based monitor for **NVIDIA NVLink** traffic (RX/TX).  
It provides a `top`-like interface (similar to `nvtop`) but focuses on **real-time NVLink bandwidth monitoring**.

![screenshot](docs/screenshot.png)

---

## Features

- Real-time monitoring of NVLink traffic per GPU and per link.
- Summarized RX/TX per GPU and global totals.
- Curses-based UI with automatic screen refresh.
- Supports **multi-GPU systems** (tested with NVIDIA V100/A100/H100).
- Flexible layout (e.g. 2 GPUs per row in multi-column mode).

---

## Requirements

- Linux with NVIDIA GPUs and NVLink.
- NVIDIA driver with `nvidia-smi` supporting NVLink counters:
  ```bash
  nvidia-smi nvlink -gt d
- Python **3.6+**
- Standard library (`curses`, `subprocess`, `time`) — no external dependencies.

---

## Installation

Clone the repository:

  ```bash
  git clone https://github.com/hsianghualite/nvltop.git
  cd nvltop
  chmod +x nvltop.py
  alias nvltop="python3 /path/to/nvltop/nvltop.py"
```
---

## Usage

- Run with default refresh interval (1s):

  ```bash
  ./nvltop.py

- Custom refresh interval (e.g. 0.5s):

  ```bash
  ./nvltop.py -i 0.5

Exit with q or Ctrl+C.

---

## Contributing
- Pull requests and issues are welcome!
- If you want to add features or fix bugs, please open an issue first to discuss.

---

## License

- MIT License. See LICENSE for details.


