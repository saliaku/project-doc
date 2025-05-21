---
title: Databases
cascade:
type: default
weight: 5
---

This section details the database tables used in the project. There are two databases:

- moodle: Default database created by moodle to store moodle data
- fyp: Database created to store required information of the implementation 


## moodle


{{< callout type="info" >}}
  Note: moodle tables have many built-in fields. The schema of only the required section of tables is provided.
{{< /callout >}}

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


### Table: `mdl_question_versions`

| **Field**             | **Data Type**        | **Description**                                 |
|-----------------------|----------------------|-------------------------------------------------|
| `id`                  | INT (AUTO INCREMENT) | Auto increment identifier                       |
| `questionbankentryid` | INT                  | Foreign key – ID in `mdl_question_bank_entries` |
| `questionid`          | INT                  | Foreign key – ID in `mdl_questions`             |


### Table: `mdl_question_bank_entries`

| **Field**            | **Data Type**        | **Description**                                 |
|----------------------|----------------------|-------------------------------------------------|
| `id`                 | INT (AUTO INCREMENT) | Auto increment identifier                       |
| `questioncategoryid` | INT                  | Category of the question in the question bank   |


## fyp

### Table: `topics`

| **Field**        | **Data Type**        | **Description**                                  |
|------------------|----------------------|--------------------------------------------------|
| `id`             | INT (AUTO INCREMENT) | Auto increment identifier                        |
| `topic_name`     | VARCHAR              | Name of the topic                                |
| `difficulty`     | FLOAT                | Difficulty value of the topic                    |
| `num_questions`  | INT                  | Number of quiz questions to be given for topic   |


### Table: `lo`

| **Field**      | **Data Type**        | **Description**                                   |
|----------------|----------------------|---------------------------------------------------|
| `id`           | INT (AUTO INCREMENT) | Auto increment identifier                         |
| `topic`        | INT                  | Foreign key – ID in `topics`                      |
| `v`            | FLOAT                | Visual score                                      |
| `a`            | FLOAT                | Auditory score                                    |
| `t`            | FLOAT                | Textual score                                     |
| `ip`           | FLOAT                | Information processing score                      |
| `read_metric`  | FLOAT                | Readability score                                 |
| `path`         | TEXT                 | Path to the resource in the server                |


### Table: `clusters`

| **Field**     | **Data Type**        | **Description**                                   |
|---------------|----------------------|---------------------------------------------------|
| `id`          | INT (AUTO INCREMENT) | Auto increment identifier                         |
| `centroid`    | LONG TEXT            | Centroid of the cluster as an array               |
| `gene_pool`   | LONG TEXT            | Gene pool of the cluster as JSON                  |


### Table: `students`

| **Field**          | **Data Type**        | **Description**                                                        |
|--------------------|----------------------|------------------------------------------------------------------------|
| `user_id`          | INT                  | Foreign key – ID in `mdl_user`                                         |
| `path`             | LONG TEXT            | Current learning pathway of the student                               |
| `cluster_id`       | INT                  | Foreign key – ID of `clusters`                                         |
| `difficulty`       | LONG TEXT            | Difficulty values topic-wise as JSON                                  |
| `gene_space`       | LONG TEXT            | Gene space of the student as JSON                                     |
| `explored_genes`   | LONG TEXT            | Genes explored by GA in ascending order of cost, arranged topic-wise  |
| `learning_costs`   | LONG TEXT            | Genes and their learning costs for the student as JSON                |
| `completed`        | LONG TEXT            | Topics completed by the student as an array                           |
| `stored_path`      | LONG TEXT            | Initial learning path generated for the student                       |

### Table: `quiz_attempts`

| **Field**     | **Data Type**        | **Description**                                            |
|---------------|----------------------|------------------------------------------------------------|
| `student_id`  | INT                  | Foreign key – ID in `mdl_user`                             |
| `topic_id`    | INT                  | Foreign key – ID in `topics`                               |
| `attempts`    | INT                  | Quiz attempts of the user on the given topic               |
| `scores`      | LONG TEXT            | Scores obtained by the student in quiz attempts (JSON)     |
