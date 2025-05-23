---
title: Quiz pages
cascade:
type: default
weight: 2
---


```php
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