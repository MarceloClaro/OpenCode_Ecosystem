import os
import sys

def search_directory(root_dir):
    print(f"Scanning {root_dir}...")
    for root, dirs, files in os.walk(root_dir, topdown=True):
        try:
            # Modify dirs in-place to avoid traversing into OneDrive or system folders that cause errors
            dirs_to_keep = []
            for d in dirs:
                try:
                    path = os.path.join(root, d)
                    # Skip OneDrive
                    if "onedrive" in path.lower():
                        continue
                    # Skip typical system or cache dirs that are very large
                    if d.lower() in ['.git', 'node_modules', '$recycle.bin', 'system volume information', 'windows', 'microsoft', 'google']:
                        continue
                    dirs_to_keep.append(d)
                except Exception:
                    pass
            dirs[:] = dirs_to_keep

            # Check directory names
            for d in dirs:
                try:
                    if "cweijan" in d.lower() or "database-client" in d.lower() or "dbclient" in d.lower():
                        full_path = os.path.join(root, d)
                        print(f"[FOUND DIR] {full_path}")
                except Exception:
                    pass

            # Check file names
            for f in files:
                try:
                    if "cweijan" in f.lower() or "database-client" in f.lower() or "dbclient" in f.lower():
                        full_path = os.path.join(root, f)
                        print(f"[FOUND FILE] {full_path}")
                except Exception:
                    pass
        except Exception:
            pass

if __name__ == "__main__":
    import string
    print("Starting search for 'cweijan', 'database-client', or 'dbclient' on your system...")
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    print(f"Detected drives: {drives}")
    for drive in drives:
        # Search the user profile if on C drive, otherwise search the whole drive
        if drive.upper().startswith("C"):
            search_directory("C:\\Users\\marce")
            search_directory("C:\\Program Files")
            search_directory("C:\\Program Files (x86)")
        else:
            search_directory(drive)
    print("Search completed.")
