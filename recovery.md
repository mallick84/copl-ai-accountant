# 🔄 Recovery Guide — AI-Accountant

This document explains how to use the **Version Recovery System** to protect and restore your working code.

---

## Prerequisites

- Python 3 installed
- Terminal / Command Prompt access
- Navigate to the project folder:
  ```bash
  cd /Users/avijitmallick/analytics/antigravity/AIGST
  ```

---

## 📸 Create a Backup

Run this **before** making any significant code changes:

```bash
python backup.py
```

**What happens:**
- All key files (`app.py`, `database.py`, `gst_automation.py`, `requirements.txt`, `pages/`) are copied into a timestamped folder inside `backups/`.
- A version number is assigned automatically (v1, v2, v3...).

---

## 📋 List All Backups

To see all available recovery points:

```bash
python backup.py --list
```

**Example output:**
```
📦 Available Backups:
------------------------------------------------------------
  Version   1  |  18-Feb-2026 02:36 PM  |  v1_20260218_143600
  Version   2  |  19-Feb-2026 10:00 AM  |  v2_20260219_100000
------------------------------------------------------------
Total: 2 backup(s)
```

---

## ♻️ Restore a Backup

To restore your code to a previous version:

```bash
python backup.py --restore <version_number>
```

**Example — Restore to Version 1:**
```bash
python backup.py --restore 1
```

**What happens:**
1. You will see a confirmation prompt.
2. Type `yes` to confirm.
3. All your current code files will be **replaced** with the backed-up version.

> ⚠️ **Important:** Restoring will overwrite your current files. Create a new backup first if you want to save your current state before restoring.

---

## 🛡️ Best Practices

| When | What to do |
|---|---|
| Before editing code | Run `python backup.py` |
| Before updating dependencies | Run `python backup.py` |
| After a successful feature | Run `python backup.py` |
| Something broke | Run `python backup.py --restore <version>` |

---

## 📁 Where Are Backups Stored?

Backups are saved locally in the `backups/` folder inside the project directory. Each version is a complete copy of all application files.

```
AIGST/
├── backups/
│   ├── v1_20260218_143600/
│   │   ├── app.py
│   │   ├── database.py
│   │   ├── gst_automation.py
│   │   ├── requirements.txt
│   │   └── pages/
│   └── versions.json
├── app.py
├── backup.py
└── ...
```

> **Note:** Backups are excluded from Git (via `.gitignore`) to keep the repository clean. They are stored only on your local machine.
