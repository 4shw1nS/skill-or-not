---
name: should-be-script
description: >
  Archives a finished project folder. Use when the user asks to archive a
  project or move a finished project to the archive drive.
---

# Archive a project

Run these steps in order, exactly as written:

1. `tar -czf <project>.tar.gz <project>/`
2. `mv <project>.tar.gz /Volumes/Archive/projects/`
3. `echo "$(date +%F) <project>" >> /Volumes/Archive/projects/archive.log`
4. `rm -rf <project>/`

Do not vary the sequence. Do not skip the log line. The archive drive is
always mounted at `/Volumes/Archive`.
