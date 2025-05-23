import sys
import json
import pymysql
import variables

userid = sys.argv[1]

def safe(x):
    return x if x is not None else 0

# Connect to DB
conn = pymysql.connect(
    host=variables.HOST,
    user=variables.USER,
    password=variables.PASS,
    database='fyp'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

cursor.execute("""
    SELECT t.id AS topic_id, t.topic_name, qa.attempts, qa.scores
    FROM topics t
    LEFT JOIN quiz_attempts qa ON qa.topic_id = t.id AND qa.student_id = %s
    ORDER BY t.id
""", (userid,))

topics_scores = cursor.fetchall()

topics_data = {}

for row in topics_scores:
    topic_id = row['topic_id']
    topic_name = row['topic_name']
    attempts = safe(row['attempts'])
    scores_str = row['scores']

    # Parse scores from JSON string to dictionary
    try:
        scores = json.loads(scores_str) if scores_str else {}
    except json.JSONDecodeError:
        scores = {}

    if topic_id not in topics_data:
        topics_data[topic_id] = {
            'topic_name': topic_name,
            'attempts': attempts,
            'scores': {}
        }

    # Assuming scores is already a dict like {"1": 0, "2": 1}
    topics_data[topic_id]['scores'] = scores

conn.close()

print(json.dumps(topics_data))
