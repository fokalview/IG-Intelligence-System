# Tracker system for follower intelligence
# Tracker system for follower intelligence

import csv
from datetime import datetime
import os

# Fix path so it works from anywhere
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

RUNS_FILE = os.path.join(DATA_DIR, "runs.csv")
MASTER_FILE = os.path.join(DATA_DIR, "followers_master.csv")


def load_csv_as_dict(file_path, key_field):
    data = {}
    if not os.path.exists(file_path):
        return data

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row[key_field]] = row
    return data


def append_run(total_followers):
    run_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(RUNS_FILE, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([run_id, date, total_followers])

    return run_id


def update_master(current_usernames, run_id):
    master_data = load_csv_as_dict(MASTER_FILE, "username")
    updated_rows = {}

    # Track current users
    for username in current_usernames:
        if username in master_data:
            master_data[username]["last_seen_run"] = run_id
            master_data[username]["status"] = "active"
        else:
            master_data[username] = {
                "username": username,
                "first_seen_run": run_id,
                "last_seen_run": run_id,
                "status": "active"
            }

    # Detect unfollowers
    for username in master_data:
        if username not in current_usernames:
            master_data[username]["status"] = "unfollowed"

        updated_rows[username] = master_data[username]

    # Sort newest → oldest
    sorted_rows = sorted(
        updated_rows.values(),
        key=lambda x: x["first_seen_run"],
        reverse=True
    )

    # Write back to CSV
    with open(MASTER_FILE, "w", newline='', encoding='utf-8') as f:
        fieldnames = ["username", "first_seen_run", "last_seen_run", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(sorted_rows)


def run_tracker(current_usernames):
    # Use set for faster lookup
    current_usernames = set(current_usernames)

    total_followers = len(current_usernames)
    run_id = append_run(total_followers)

    update_master(current_usernames, run_id)

    print(f"Run complete: {run_id}")
    print(f"Total followers: {total_followers}")


# ---------------- TEST BLOCK ---------------- #

if __name__ == "__main__":
    print("\n--- TEST RUN 1 ---")
    test_users = ["user1", "user2", "user3"]
    run_tracker(test_users)

    print("\n--- TEST RUN 2 ---")
    test_users = ["user1", "user3", "user4"]
    run_tracker(test_users)

    print("\n--- TEST RUN 3 ---")
    test_users = ["user1", "user4"]
    run_tracker(test_users)
