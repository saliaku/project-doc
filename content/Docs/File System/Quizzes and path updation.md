---
title: Quiz pages
cascade:
type: default
weight: 3
---

This page details the files responsible for presenting the post-assessment quizzes after each topic. The script below, get_quiz_questions.py, retrieves quiz questions from the database based on the current topic.

```python
#get_quiz_questions.py
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
```
Download [get_quiz_questions.py](/Files/get_quiz_questions.py) from here.
The file below uses `get_quiz_questions.py` to fetch the relevant questions and renders the quiz page accordingly.

```php
//quiz.php

<?php

require_once('../../config.php');
require_login();

if (session_status() == PHP_SESSION_NONE) {
    session_start();
}

$userid = $USER->id;
$topic_id = $_SESSION['topic_id'] ?? null;
$topic_name = $_SESSION['topic_name'] ?? '';

if (!isset($_SESSION['quiz_questions']) || ($_SESSION['stored_topic_id'] ?? null) !== $topic_id) {
    $command = escapeshellcmd("python3 /var/www/html/moodle/local/learningpath/get_quiz_questions.py $topic_id");
    $output = shell_exec($command);

    if (!$output) {
        echo "<p style='text-align: center; color: red;'>❌ Error fetching quiz questions.</p>";
        exit;
    }

    $data = json_decode($output, true);

    if (!isset($data['questions']) || !is_array($data['questions'])) {
        echo "<p style='text-align: center; color: orange;'>⚠️ No questions available.</p>";
        exit;
    }

    $_SESSION['quiz_questions'] = $data['questions'];
    $_SESSION['stored_topic_id'] = $topic_id;
}

$questions = $_SESSION['quiz_questions'];

// Quiz Header
echo "<div style='width: 100%; text-align: center; margin: 20px 0;'>
        <h2 style='color: #003366; font-weight: bold; font-size: 28px;'>📝 Quiz: $topic_name</h2>
      </div>";

// Centered Quiz Box
echo "<div style='max-width: 700px; margin: auto; padding: 20px; background-color: #fffddb; border-radius: 10px;'>";

echo "<form id='quizForm' method='post'>";

foreach ($questions as $index => $question) {
    $qid = htmlspecialchars($question['id']);
    $qtext = htmlspecialchars(strip_tags($question['text']), ENT_QUOTES);
    $qtype = $question['type'];
    $options = $question['options'];

    echo "<div style='margin-bottom: 25px;'>
            <strong>Q" . ($index + 1) . ": $qtext</strong><br>";

    if ($qtype === 'multichoice') {
        foreach ($options as $i => $option) {
            $choiceText = htmlspecialchars(strip_tags($option['text']), ENT_QUOTES);
            echo "<label style='display: block; margin: 5px 0;'>
                    <input type='radio' name='q_$qid' value='$i' required>
                    $choiceText
                  </label>";
        }
    } elseif ($qtype === 'truefalse') {
        foreach ($options as $option) {
            $value = htmlspecialchars(strip_tags($option['text']), ENT_QUOTES);
            $label = htmlspecialchars($option['text'], ENT_QUOTES);
            echo "<label style='display: block; margin: 5px 0;'>
                    <input type='radio' name='q_$qid' value='$value' required>
                    $label
                  </label>";
        }
    }

    echo "</div>";
}

echo "<input type='hidden' name='topic_id' value='$topic_id'>";
echo "<input type='hidden' name='user_id' value='$userid'>";
echo "<input type='hidden' name='final_submit' value='1'>";

// Submit Only Button
echo "<div style='text-align: center; margin-top: 30px;'>
        <button type='submit' formaction='quiz_submit.php' style='background-color: #28a745; color: white; padding: 12px 24px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer;'>✅ Submit Quiz</button>
      </div>";

echo "</form>";
echo "</div>";
?>
```
Download [quiz.php](/Files/quiz.php) from here.
Depending on the quiz score achieved, `Quizupdate.py` adjusts the personalized learning path and updates the database accordingly.


```python
#Quizupdate.py

#!/usr/bin/env python3

import sys
import variables
from GA_functions import *


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(1)

    user_id = int(sys.argv[1])
    current_topic= int(sys.argv[2])
    score = float(sys.argv[3])
    

    # Fetch student profile
    student_profile, path = fetch_student_profile(user_id)
    if student_profile is None:
        sys.exit(1)
    variables.student_profile= student_profile

    # Fetch supporting data
    clusters = fetch_clusters()
    learning_objects, _ = fetch_learning_objects()
    variables.learning_objects= learning_objects
    


    # Fetch attempts count from quiz_attempts table
    attempts = fetch_attempts(user_id, current_topic)

    # Update score and path
    new_path = update_score(student_profile, score, attempts, path, clusters, variables.max_distance, learning_objects)

    # Save updated student profile
    update_student_profile(user_id, student_profile, new_path)
```
Download [Quizupdate.py](/Files/Quizupdate.py) from here.
The below file stores the obtained scores in the database.


```python
#scoring.py

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
```
Download [scoring.py](/Files/scoring.py) from here.
Once the quiz is submitted, control is passed to `quiz_submit.php` for processing the results, which in turn invokes `scoring.py` and `Quizupdate.py`.


```php
//quiz_submit.php

<?php

require_once('../../config.php');
require_login();

if (session_status() == PHP_SESSION_NONE) {
    session_start();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['user_id'], $_POST['topic_id'])) {
    $_SESSION['last_submitted_answers'] = $_POST;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !isset($_SESSION['quiz_submitted'])) {

    $userid = intval($_POST['user_id'] ?? 0);
    $topic_id = intval($_POST['topic_id'] ?? 0);
    $submitted = $_POST;

    $questions = $_SESSION['quiz_questions'] ?? [];

    if (!$questions || !$userid || !$topic_id) {
        echo "<p>Error: Missing required data.</p>";
        exit;
    }

    $total = count($questions);
    $score = 0;

    foreach ($questions as $i => $question) {
        $qid = $question['id'];
        $qtype = $question['type'];
        $options = $question['options'];
        $submitted_key = 'q_' . $qid;

        $questions[$i]['student_answer'] = 'Not Answered';
        $questions[$i]['is_correct'] = false;

        if (!isset($submitted[$submitted_key])) {
            continue;
        }

        $user_answer = $submitted[$submitted_key];

        if ($qtype === 'multichoice') {
            $selected_index = intval($user_answer);
            if (isset($options[$selected_index])) {
                $questions[$i]['student_answer'] = $options[$selected_index]['text'];
                if (!empty($options[$selected_index]['is_correct'])) {
                    $score++;
                    $questions[$i]['is_correct'] = true;
                }
            }
        } elseif ($qtype === 'truefalse') {
            $user_answer_clean = strtolower(trim(strip_tags($user_answer)));
            foreach ($options as $opt) {
                $opt_clean = strtolower(trim(strip_tags($opt['text'])));
                if ($user_answer_clean === $opt_clean) {
                    $questions[$i]['student_answer'] = $opt['text'];
                    if (!empty($opt['is_correct'])) {
                        $score++;
                        $questions[$i]['is_correct'] = true;
                    }
                    break;
                }
            }
        }
    }

    $_SESSION['quiz_questions'] = $questions;

    $percentage = ($total > 0) ? round(($score / $total) * 100, 2) : 0;
    $score_decimal = ($total > 0) ? round($score / $total, 4) : 0.0;
    $escaped_userid = escapeshellarg($userid);
    $escaped_topic_id = escapeshellarg($topic_id);
    $escaped_score = escapeshellarg($score_decimal);

    $command1 = "python3 /var/www/html/moodle/local/learningpath/scoring.py $escaped_userid $escaped_topic_id $escaped_score 2>&1";
    $output = shell_exec($command1);

    $scriptPath = "/var/www/html/moodle/local/learningpath/Quizupdate.py";
    $command = "python3 $scriptPath $escaped_userid $escaped_topic_id $escaped_score 2>&1";
    $output1 = shell_exec($command);

    $_SESSION['quiz_submitted'] = [
        'score' => $score,
        'total' => $total,
        'percentage' => $percentage,
        'output' => $output1
    ];

    unset($_SESSION['last_submitted_answers']);
    unset($_SESSION['stored_topic_id']);

    header("Location: quiz_submit.php");
    exit;
}

if (isset($_SESSION['quiz_submitted'])) {
    $score = $_SESSION['quiz_submitted']['score'];
    $total = $_SESSION['quiz_submitted']['total'];
    $percentage = $_SESSION['quiz_submitted']['percentage'];
    $output = $_SESSION['quiz_submitted']['output'];

    echo "
<div style='display: flex; justify-content: center; align-items: center; min-height: 100vh;'>
    <div style='max-width: 800px; width: 100%; text-align: left; background-color: #f3ffdb; padding: 40px 60px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);'>
        <h2 style='color: #2e7d32; font-size: 32px; text-align: center;'>✅ Quiz Completed!</h2>
        <p style='font-size: 20px;'><strong>Score:</strong> $score / $total</p>
        <p style='font-size: 20px;'><strong>Percentage:</strong> $percentage%</p>
        
        <h3 style='margin-top: 30px; color: #2e2e2e;'>📝 Review:</h3>
        <div style='margin-top: 15px;'>";

    if (isset($_SESSION['quiz_questions'])) {
        foreach ($_SESSION['quiz_questions'] as $q) {
            $qtext = $q['text'];
            $correct = '';
            foreach ($q['options'] as $opt) {
                if (!empty($opt['is_correct'])) {
                    $correct = $opt['text'];
                    break;
                }
            }

            $student_answer = $q['student_answer'] ?? 'Not Answered';
            $is_correct = $q['is_correct'] ?? false;
            $feedback = $q['feedback'] ?? '';

            $status_color = $is_correct ? 'green' : 'red';
            $status_text = $is_correct ? 'Correct ✅' : 'Incorrect ❌';

            echo "<div style='margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 6px; background-color: #fff;'>
                <p style='font-weight: bold;'>Q: " . html_entity_decode($qtext) . "</p>
                <p><strong>Your Answer:</strong> " . html_entity_decode(strip_tags($student_answer)) . "</p>
                <p><strong>Correct Answer:</strong> <span style='color: green;'>" . html_entity_decode(strip_tags($correct)) . "</span></p>
                <p style='color: $status_color; font-weight: bold;'>$status_text</p>";

            if (!empty($feedback)) {
                echo "<p style='color: #444;'><strong>💡 Feedback:</strong> " . html_entity_decode(strip_tags($feedback)) . "</p>";
            }

            echo "</div>";
        }
    }

    echo "</div>
        <div style='text-align: center; margin-top: 30px;'>
            <a href='view.php'>
                <button style='padding: 14px 28px; font-size: 18px; background-color: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; transition: background-color 0.3s;'>
                    ➡️ Proceed Next
                </button>
            </a>
            <h3 style='font-size: 24px; color: rgb(45, 42, 107); margin-top: 20px;'>" . nl2br(htmlspecialchars($output)) . "</h3>
        </div>
    </div>
</div>";

    unset($_SESSION['quiz_questions']);
    unset($_SESSION['quiz_submitted']);
}
?>
```
Download [quiz_submit.php](/Files/quiz_submit.php) from here.


