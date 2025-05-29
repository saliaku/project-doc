import pymysql
import json
import sys
import variables

# Usage: python store_score.py <userid> <topic_id> <score>
userid = int(sys.argv[1])
topic_id = int(sys.argv[2])
score = float(sys.argv[3])  # score can be a float

try:
    conn = pymysql.connect(
        host=variables.HOST,
        user=variables.USER,
        password=variables.PASS,
        database='fyp'
    )
    cursor = conn.cursor()

    # Fetch existing scores and attempts for this user-topic
    cursor.execute("SELECT scores, attempts FROM quiz_attempts WHERE student_id=%s AND topic_id=%s", (userid, topic_id))
    row = cursor.fetchone()

    if row:
        current_scores, current_attempts = row
        if current_scores is None:
            scores_dict = {}
        else:
            try:
                scores_dict = json.loads(current_scores)
            except json.JSONDecodeError:
                scores_dict = {}

        scores_dict[str(current_attempts)] = score  # Use current attempt number as key (string)

        # Update only the scores
        cursor.execute(
            "UPDATE quiz_attempts SET scores=%s WHERE student_id=%s AND topic_id=%s",
            (json.dumps(scores_dict), userid, topic_id)
        )
        conn.commit()
        print(json.dumps({"status": "updated", "attempt": current_attempts, "score": score}))
    else:
        # First time inserting — default attempt is 1
        scores_dict = {"1": score}
        cursor.execute(
            "INSERT INTO quiz_attempts (student_id, topic_id, scores, attempts) VALUES (%s, %s, %s, %s)",
            (userid, topic_id, json.dumps(scores_dict), 1)
        )
        conn.commit()
        print(json.dumps({"status": "inserted", "attempt": 1, "score": score}))

    cursor.close()
    conn.close()

except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit()
