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
