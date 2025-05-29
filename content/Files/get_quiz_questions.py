import pymysql
import json
import sys
import variables
import random


topic_id = int(sys.argv[1])

# Step 1: Fetch topic name and num_questions from 'fyp.topics'
try:
    conn_fyp = pymysql.connect(
        host=variables.HOST,
        user=variables.USER,
        password=variables.PASS,
        database='fyp'
    )
    cursor_fyp = conn_fyp.cursor()
    cursor_fyp.execute("SELECT topic_name, num_questions FROM topics WHERE id = %s", (topic_id,))
    topic_data = cursor_fyp.fetchone()
    if not topic_data:
        raise Exception("Topic not found in fyp.topics")
    topic_name, num_questions = topic_data
    category_id = int(topic_id) - 18 #mapping between topic and question bank category
    cursor_fyp.close()
    conn_fyp.close()
except Exception as e:
    print(json.dumps({"error": f"Error fetching topic info: {str(e)}"}))
    sys.exit()

# Step 2: Fetch questions and options from Moodle DB
try:
    conn_moodle = pymysql.connect(
        host=variables.HOST,
        user=variables.USER,
        password=variables.PASS,
        database='moodle'
    )
    cursor = conn_moodle.cursor()

    query = """
    SELECT q.id, q.questiontext, q.qtype, q.generalfeedback
    FROM mdl_question q
    JOIN mdl_question_versions v ON q.id = v.questionid
    JOIN mdl_question_bank_entries e ON v.questionbankentryid = e.id
    WHERE e.questioncategoryid = %s
    ORDER BY RAND()
    """
    cursor.execute(query, (category_id, ))
    questions_raw = cursor.fetchall()

    questions = []
    for qid, text, qtype, feedback in questions_raw:
        question = {
            "id": qid,
            "text": text,
            "type": qtype,
            "feedback":feedback,
            "options": []
        }

        if qtype == "multichoice":
            cursor.execute("SELECT answer, fraction FROM mdl_question_answers WHERE question = %s", (qid,))
            for answer, fraction in cursor.fetchall():
                question["options"].append({
                    "text": answer,
                    "is_correct": fraction > 0
                })

        elif qtype == "truefalse":
            cursor.execute("SELECT answer, fraction FROM mdl_question_answers WHERE question = %s", (qid,))
            for answer, fraction in cursor.fetchall():
                question["options"].append({
                    "text": answer,
                    "is_correct": fraction > 0
                })

        questions.append(question)

   

    # Shuffle and select only num_questions
    #print(questions)
    random.shuffle(questions)
    questions = questions[:num_questions]


    print(json.dumps({
        "questions": questions,
        "topic_name": topic_name,
        "topic_id": topic_id
    }))

    conn_moodle.close()

except Exception as e:
    print(json.dumps({"error": f"Error fetching questions: {str(e)}"}))
    sys.exit()
