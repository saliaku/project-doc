---
title: Display learning content
cascade:
type: default
weight: 2
---

## get_next_lo.py

```python
#get_next_lo.py

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
```

## view.php

```python
# view.php

<?php

require_once('../../config.php');
require_login();
$userid = $USER->id;

// Run Python script
$command = "python3 /var/www/html/moodle/local/learningpath/get_next_lo.py $userid 2>&1";
$output = shell_exec($command);

if (!$output) {
    echo "Error: Python script did not return anything.<br>";
    exit;
}

$result = json_decode($output, true);

// Extract and store values
$path = $result['path'] ?? null;
$topic_id = $result['topic_id'] ?? null;
$topic_name = $result['topic_name'] ?? null;

$_SESSION['topic_id'] = $topic_id;
$_SESSION['topic_name'] = $topic_name;

if (!$path || $path === "none") {
    echo '
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; text-align: center;">
        <h3 style="font-size: 36px; color: #4CAF50; margin-bottom: 20px;">Course completed! Thank you for taking it! 🎉</h3>
        <a href="/moodle/course/view.php?id=2" style="font-size: 18px; color: white; background-color: #007bff; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
            ⬅️ Return to Moodle
        </a>
    </div>';

    exit;
}




// Display topic title centered in dark blue, bold
echo "<div style='width: 100%; text-align: center; margin: 30px 0 20px;'>
        <h3 style='color: #003366; font-weight: bold; font-size: 32px;'>
            📝 $topic_name
        </h3>
      </div>";

      $file_extension = strtolower(pathinfo($path, PATHINFO_EXTENSION));

      if ($file_extension === 'txt') {
          $content = @file_get_contents($path);
          if ($content === false) {
              echo "<p style='color: red; text-align: center;'>Failed to load content.</p>";
          } else {
              echo "<div style='margin: 0 auto; max-width: 900px; padding: 40px; background-color: #dbf3ff; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); font-family: Georgia, serif; font-size: 18px; line-height: 1.8; color: #333;'>
                      " . nl2br(htmlspecialchars($content)) . "
                    </div>";
          }
      } elseif ($file_extension === 'mp4') {
          echo "<div style='display: flex; justify-content: center;'>
                  <video controls style='width: 90%; max-width: 960px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>
                      <source src='$path' type='video/mp4'>
                      Your browser does not support the video tag.
                  </video>
                </div>";
      } else {
          echo "<iframe src='$path' style='width: 100vw; height: calc(100vh - 250px); border: none; display: block; margin: 0 auto;'></iframe>";
      }
      

// Proceed to Quiz button styled and spaced
echo "<div style='text-align: center; margin-top: 40px;'>
        <a href='quiz.php'>
            <button style='background-color: #0056b3; color: white; padding: 14px 28px; font-size: 18px; border: none; border-radius: 6px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                ➡️ Proceed to Quiz
            </button>
        </a>
      </div>";


?>
```
