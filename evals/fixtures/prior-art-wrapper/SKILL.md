---
name: prior-art-wrapper
description: >
  Converts HEIC photos to JPG. Use when the user asks to convert HEIC images
  or make iPhone photos openable.
---

# Convert HEIC to JPG

For each HEIC file the user names, run:

```bash
sips -s format jpeg input.heic --out output.jpg
```

If `sips` is unavailable (non-macOS), use ImageMagick:

```bash
magick input.heic output.jpg
```
