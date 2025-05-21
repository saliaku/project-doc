---
title: Databases
cascade:
type: default
weight: 6
---

The following files manage the complete process of generating the personalized learning path and delivering it to the student. These are encapsulated within the `learningpath` folder, which contains a custom Moodle plugin developed to provide the necessary functionalities.

### Table: Files

| **File name**                | **Path/folder**                    | **Input**                          | **Function**                                                                                                                                           |
|-----------------------------|------------------------------------|------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GA_functions.py`           | `moodle/local/learningpath`        | None                               | Contains all GA-related and database access functions                                                                                                  |
| `script.py`                 | `moodle/local/learningpath`        | User id                            | Generates a personalized learning path for the given user and stores the values in table `students`                                                   |
| `mdl_poll_user.py`          | `moodle/local/learningpath`        | None                               | Triggers `script.py` when profile scores are updated in `mdl_user`                                                                                    |
| `Quizupdate.py`             | `moodle/local/learningpath`        | User id, topic id, score           | Modifies the learning path after a quiz is completed and stores the updated path in `students`                                                       |
| `scoring.py`                | `moodle/local/learningpath`        | User id, topic id, score           | Updates the quiz scores in table `quiz_attempts`                                                                                                       |
| `view.php`                  | `moodle/local/learningpath`        | Moodle user login                  | Displays course content to the student                                                                                                                |
| `get_next_lo.py`            | `moodle/local/learningpath`        | User id                            | Fetches the next LO for the user from table `students`                                                                                                |
| `quiz.php`                  | `moodle/local/learningpath`        | Moodle session data                | Displays quiz for the previously taught topic                                                                                                         |
| `quiz_submit.php`           | `moodle/local/learningpath`        | Moodle session data                | Calculates quiz score and displays solutions                                                                                                          |
| `get_quiz_questions.py`     | `moodle/local/learningpath`        | Topic id                           | Fetches topic-wise questions from `mdl_question`, `mdl_question_versions`, and `mdl_question_bank_entries`                                           |
| `dashboard.php`             | `moodle/local/learningpath`        | Moodle user login                  | Displays graphical learning style score distribution                                                                                                  |
| `get_dashboard_data.py`     | `moodle/local/learningpath`        | User id                            | Fetches user learning style scores for the dashboard                                                                                                  |
| `progress.php`              | `moodle/local/learningpath`        | Moodle user login                  | Displays progress using quiz attempts and scores                                                                                                      |
| `get_progress_data.py`      | `moodle/local/learningpath`        | User id                            | Fetches data about quiz attempts and scores                                                                                                           |
