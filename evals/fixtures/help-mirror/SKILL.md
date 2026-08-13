---
name: help-mirror
description: >
  Frames an image with a colored border for social posts. Use when the user
  asks to add a border or frame to an image.
---

# Frame an image

Run `scripts/frame.py` with the right flags:

- `--width` — border width in pixels. Defaults to 20.
- `--height` — border height in pixels. Defaults to matching `--width`.
- `--color` — border color as a hex string. Defaults to `#ffffff`.

Examples:

```bash
python3 scripts/frame.py photo.jpg --width 40 --color "#000000"
python3 scripts/frame.py photo.jpg --width 20 --height 60
```

Pick a wider border for busy images and a thin one for portraits.
