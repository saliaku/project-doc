import pymysql
import time
import subprocess
from datetime import datetime
import variables

# Store last seen timestamps
last_seen = {}

def fetch_updated_users():
    conn = pymysql.connect(
        host=variables.HOST,
        user=variables.USER,
        password=variables.PASS,
        database='moodle'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, last_profile_update FROM mdl_user WHERE attempt = 0")
    users = cursor.fetchall()
    conn.close()
    return users

def scores_available(user_id):
    """Checks if all required scores are available (not NULL) for the user."""
    conn = pymysql.connect(
        host=variables.HOST,
        user=variables.USER,
        password=variables.PASS,
        database='moodle'
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT wmv, wma, wmt, ipv, ipa, ipt, flesch
        FROM mdl_user
        WHERE id = %s
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False

    return all(score is not None for score in result)

def mark_attempt_done(user_id):
    conn = pymysql.connect(
        host=variables.HOST,
        user=variables.USER,
        password=variables.PASS,
        database='moodle'
    )
    cursor = conn.cursor()
    cursor.execute("UPDATE mdl_user SET attempt = 1 WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()

def main():
    while True:
        print("Polling for updates...")
        updated_users = fetch_updated_users()
        for user_id, last_update in updated_users:
            if user_id not in last_seen or (last_update and last_update > last_seen[user_id]):
                if scores_available(user_id):
                    print(f"[INFO] Detected update with scores for user {user_id}, running script.py")
                    subprocess.Popen(["python3", "script.py", str(user_id)])
                    last_seen[user_id] = last_update
                    mark_attempt_done(user_id)
                else:
                    print(f"[WARN] Update detected for user {user_id}, but scores incomplete.")
        time.sleep(30)  # Poll every 30 seconds

if __name__ == "__main__":
    main()
