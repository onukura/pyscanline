# Scanline Effects in Python

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![image](https://img.shields.io/pypi/v/pyscanline.svg)](https://pypi.python.org/pypi/pyscanline)
[![image](https://img.shields.io/pypi/l/pyscanline.svg)](https://pypi.python.org/pypi/pyscanline)
[![Python package](https://github.com/onukura/pyscanline/actions/workflows/python-package.yml/badge.svg)](https://github.com/onukura/pyscanline/actions/workflows/python-package.yml)

A Python-based library that recreates a retro-futuristic "scanline" style. It allows you to apply scanlines to:

- **Static images** (PNG, JPEG, etc.)
- **Animated GIFs** (frame-by-frame processing)

> **Note:** This project is inspired by the R [scanline](https://github.com/cj-holmes/scanline) package's approach to scanline effects. However, the results may differ slightly due to underlying implementations in Pillow, NumPy, and ImageIO.

## Features

- **Static image processing** via `scanline()`:
  - Resizes the image to a specified vertical resolution.
  - Applies customizable alpha-based scanline patterns, color mapping, borders, and optional noise.
- **GIF animation processing** via `scanline_gif()`:
  - Reads each GIF frame, flattens cumulatively (like R’s `image_flatten`), then applies the scanline effect.
  - Returns all frames plus per-frame durations, which can be saved as a new GIF.
- **Matplotlib figure support**:
  - Export plots to in-memory PNG and pass them into `scanline()` to produce stylized visualizations.

## Showcase

| Original | Scanlined |
|:--------------:|:---------------:|
| <img src="./examples/alien_ripley.jpg" alt="drawing" width="200"/> | <img src="./examples/alien_ripley.scan.png" alt="drawing" width="200"/> |
|  <img src="./examples/alien-1979.gif" alt="drawing" width="200"/> | <img src="./examples/alien-1979.scan.gif" alt="drawing" width="200"/> |

## Installation

```bash
pip install pyscanline
```

## Quick Start

```python
from pyscanline import scanline
# Apply the scanline effect
result_img = scanline("input.png", n_scanlines=60)
# Save the result
result_img.save("ouput.png")
```

See the [examples](./examples) directory for more usage scenarios.

## License

GPLv3 License. See [LICENSE](./LICENSE) for details.

---

**Enjoy creating retro-futuristic scanlines for your images and animations!**
