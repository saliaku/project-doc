import pymysql
import json
import sys
import variables

user_id = int(sys.argv[1])

conn = pymysql.connect(
    host=variables.HOST,
    user=variables.USER,
    password=variables.PASS,
    database='fyp'
)
cursor = conn.cursor()

# Get path from student table
cursor.execute("SELECT path FROM students WHERE user_id = %s", (user_id,))
result = cursor.fetchone()

if not result:
    print(json.dumps({"path": "none"}))
    exit()

path_str = result[0]
path = json.loads(path_str)

if not path:
    print(json.dumps({"path": "none"}))
    exit()

next_lo = path.pop(0)

# Fetch LO path and topic_id from lo table
cursor.execute("SELECT path, topic FROM lo WHERE id = %s", (next_lo,))
lo_result = cursor.fetchone()

if not lo_result:
    print(json.dumps({"path": "none"}))
    conn.close()
    exit()

lo_path, topic_id = lo_result

# Fetch topic name using topic_id
cursor.execute("SELECT topic_name FROM topics WHERE id = %s", (topic_id,))
topic_result = cursor.fetchone()
conn.close()

topic_name = topic_result[0] if topic_result else "Unknown Topic"

# Output both path and topic name
print(json.dumps({
    "path": lo_path,
    "topic_id": topic_id,
    "topic_name": topic_name
}))
