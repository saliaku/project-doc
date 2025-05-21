---
title: Databases
cascade:
type: default
weight: 5
---

This section details the database tables used in the project. There are two databases:

- moodle: Default database created by moodle to store moodle data
- fyp: Database created to store required information of the implementation 


{{< callout type="info" >}}
  Note: moodle tables have many built-in fields. The schema of only the required section of tables is provided.
{{< /callout >}}

## moodle

### Table: `mdl_user`

| **Field** | **Data Type**        | **Description**                                             |
|-----------|----------------------|-------------------------------------------------------------|
| `id`      | INT (AUTO INCREMENT) | Auto increment identifier                                   |
| `flesch`  | INT                  | Flesch-Kincaid score                                        |
| `ipv`     | FLOAT                | Information processing score for visual content             |
| `ipa`     | FLOAT                | Information processing score for auditory content           |
| `ipt`     | FLOAT                | Information processing score for textual content            |
| `wmv`     | FLOAT                | Working memory score for visual content                     |
| `wma`     | FLOAT                | Working memory score for auditory content                   |
| `wmt`     | FLOAT                | Working memory score for textual content                    |
| `attempt` | SMALL INT            | Indicates whether `mdl_poll_user.py` has generated a path for the user |


### Table: `mdl_questions`

| **Field**         | **Data Type**        | **Description**                                               |
|-------------------|----------------------|---------------------------------------------------------------|
| `id`              | INT (AUTO INCREMENT) | Auto increment identifier                                     |
| `questiontext`    | TEXT                 | Text of the question                                          |
| `generalfeedback` | TEXT                 | Feedback to be given with solution                            |
| `qtype`           | TEXT                 | Indicates question type – `multichoice` / `truefalse`        |


### Table: `mdl_question_answers`

| **Field**   | **Data Type**        | **Description**                                 |
|-------------|----------------------|-------------------------------------------------|
| `id`        | INT (AUTO INCREMENT) | Auto increment identifier                       |
| `question`  | INT                  | Foreign key – ID in `mdl_questions`             |
| `answer`    | TEXT                 | Choices for the question                        |
| `fraction`  | FLOAT                | Score of the choice                             |

---

### Table: `mdl_question_versions`

| **Field**             | **Data Type**        | **Description**                                 |
|-----------------------|----------------------|-------------------------------------------------|
| `id`                  | INT (AUTO INCREMENT) | Auto increment identifier                       |
| `questionbankentryid` | INT                  | Foreign key – ID in `mdl_question_bank_entries` |
| `questionid`          | INT                  | Foreign key – ID in `mdl_questions`             |

---

### Table: `mdl_question_bank_entries`

| **Field**            | **Data Type**        | **Description**                                 |
|----------------------|----------------------|-------------------------------------------------|
| `id`                 | INT (AUTO INCREMENT) | Auto increment identifier                       |
| `questioncategoryid` | INT                  | Category of the question in the question bank   |
