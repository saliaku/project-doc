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
    database='moodle'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

# Only fetch V, A, T scores
cursor.execute("""
    SELECT wmv, wma, wmt, ipv, ipa, ipt 
    FROM mdl_user 
    WHERE id = %s
""", (userid,))

record = cursor.fetchone()
conn.close()

if not record:
    print(json.dumps({'error': 'User not found'}))
else:
    s = sum([
    safe(record['wmv']), safe(record['wma']), safe(record['wmt']),
    safe(record['ipv']), safe(record['ipa']), safe(record['ipt'])
])
    if (s==0):
        print(json.dumps({'v': 0, 'a': 0, 't': 0}))
    else:
        v = (safe(record['wmv']) + safe(record['ipv'])) / s
        a = (safe(record['wma']) + safe(record['ipa'])) / s
        t = (safe(record['wmt']) + safe(record['ipt'])) / s
        print(json.dumps({'v': v, 'a': a, 't': t}))