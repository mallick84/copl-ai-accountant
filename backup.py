"""
Version Recovery System for AI-Accountant
==========================================
Run this script to create a timestamped backup of all working code files.
Each backup is stored in the `backups/` directory with a version number.

Usage:
    python backup.py              # Create a new backup
    python backup.py --list       # List all available backups
    python backup.py --restore 3  # Restore backup version 3
"""

import shutil
import os
import json
import sys
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(PROJECT_DIR, "backups")
VERSION_FILE = os.path.join(BACKUP_DIR, "versions.json")

# Files and directories to back up
INCLUDE_FILES = [
    "app.py",
    "database.py",
    "gst_automation.py",
    "requirements.txt",
]
INCLUDE_DIRS = [
    "pages",
]
# Files/dirs to exclude
EXCLUDE = [
    "__pycache__",
    "backups",
    ".git",
    "bookkeeper.db",
]


def load_versions():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return json.load(f)
    return {"versions": []}


def save_versions(data):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    with open(VERSION_FILE, "w") as f:
        json.dump(data, f, indent=2)


def create_backup():
    versions = load_versions()
    version_num = len(versions["versions"]) + 1
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"v{version_num}_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    os.makedirs(backup_path, exist_ok=True)

    # Copy individual files
    for f in INCLUDE_FILES:
        src = os.path.join(PROJECT_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, backup_path)
            print(f"  ✅ Backed up: {f}")

    # Copy directories
    for d in INCLUDE_DIRS:
        src = os.path.join(PROJECT_DIR, d)
        dst = os.path.join(backup_path, d)
        if os.path.exists(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
            print(f"  ✅ Backed up: {d}/")

    # Record version
    versions["versions"].append({
        "version": version_num,
        "name": backup_name,
        "timestamp": datetime.now().isoformat(),
        "files": INCLUDE_FILES + [d + "/" for d in INCLUDE_DIRS],
    })
    save_versions(versions)

    print(f"\n🎉 Backup created: {backup_name} (Version {version_num})")
    print(f"   Location: {backup_path}")
    return version_num


def list_backups():
    versions = load_versions()
    if not versions["versions"]:
        print("No backups found.")
        return

    print("\n📦 Available Backups:")
    print("-" * 60)
    for v in versions["versions"]:
        ts = datetime.fromisoformat(v["timestamp"]).strftime("%d-%b-%Y %I:%M %p")
        print(f"  Version {v['version']:>3}  |  {ts}  |  {v['name']}")
    print("-" * 60)
    print(f"Total: {len(versions['versions'])} backup(s)\n")


def restore_backup(version_num):
    versions = load_versions()
    target = None
    for v in versions["versions"]:
        if v["version"] == version_num:
            target = v
            break

    if not target:
        print(f"❌ Version {version_num} not found.")
        list_backups()
        return

    backup_path = os.path.join(BACKUP_DIR, target["name"])
    if not os.path.exists(backup_path):
        print(f"❌ Backup directory missing: {backup_path}")
        return

    # Confirm
    print(f"\n⚠️  You are about to restore Version {version_num} ({target['name']})")
    print(f"   Created: {target['timestamp']}")
    confirm = input("   Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return

    # Restore individual files
    for f in INCLUDE_FILES:
        src = os.path.join(backup_path, f)
        dst = os.path.join(PROJECT_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  ✅ Restored: {f}")

    # Restore directories
    for d in INCLUDE_DIRS:
        src = os.path.join(backup_path, d)
        dst = os.path.join(PROJECT_DIR, d)
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  ✅ Restored: {d}/")

    print(f"\n🎉 Successfully restored to Version {version_num}!")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("\n📸 Creating backup...")
        create_backup()
    elif sys.argv[1] == "--list":
        list_backups()
    elif sys.argv[1] == "--restore" and len(sys.argv) == 3:
        try:
            ver = int(sys.argv[2])
            restore_backup(ver)
        except ValueError:
            print("Please provide a valid version number.")
    else:
        print(__doc__)
