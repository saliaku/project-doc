<?php
require_once('../../config.php');
require_login();

$PAGE->set_context(context_system::instance());
$PAGE->set_url(new moodle_url('/local/learningpath/progress.php'));
$PAGE->set_title("Learning Progress Dashboard");

if (session_status() == PHP_SESSION_NONE) {
    session_start();
}

$userid = $USER->id;
$pythonPath = '/usr/bin/python3';
$scriptPath = '/var/www/html/moodle/local/learningpath/get_progress_data.py';
$command = escapeshellcmd("$pythonPath $scriptPath $userid 2>&1");
$output = shell_exec($command);

echo $OUTPUT->header();
echo "<h2 style='margin-bottom: 30px; text-align: center;'>Your Learning Progress</h2>";

if (!$output) {
    echo "<div class='alert alert-danger'>Error fetching progress data. No output from script.</div>";
    echo $OUTPUT->footer();
    exit;
}

$data = json_decode($output, true);

if (!is_array($data) || isset($data['error'])) {
    echo "<div class='alert alert-danger'>Error fetching progress data: " . htmlspecialchars($data['error'] ?? 'Unknown error') . "</div>";
    echo $OUTPUT->footer();
    exit;
}

// Calculate maximum attempts for consistent column sizing
$max_attempts = 1;
foreach ($data as $topic) {
    $attempts = min(intval($topic['attempts']), count($topic['scores']));
    if ($attempts > $max_attempts) {
        $max_attempts = $attempts;
    }
}
?>
<style>
.progress-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    box-sizing: border-box;
}

.chart-wrapper {
    display: flex;
    flex-direction: column;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    padding: 25px;
    margin-bottom: 30px;
}

.chart-area {
    display: flex;
    flex-direction: row;
    margin-top: 20px;
    position: relative;
}

.y-axis {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 220px;
    padding-right: 15px;
    font-size: 12px;
    color: #555;
    border-right: 1px solid #e0e0e0;
    margin-right: 15px;
    min-width: 30px;
}

.y-axis div {
    text-align: right;
    padding-right: 5px;
}

.chart-columns-wrapper {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    overflow-x: auto;
    padding-bottom: 20px;
}

.chart-container {
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    min-height: 220px;
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 0;
    gap: 40px;
    padding-left: 10px;
    padding-right: 20px;
}

.topic-labels {
    display: flex;
    flex-direction: row;
    gap: 40px;
    padding-left: 10px;
    padding-right: 20px;
    margin-top: 10px;
}

.topic-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
}

.attempt-bars {
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    gap: 5px;
    height: 200px;
    margin-bottom: -2px;
}

.bar {
    width: 20px;
    border-radius: 3px 3px 0 0;
    transition: height 0.3s ease;
    position: relative;
}

.bar:hover {
    opacity: 0.9;
    transform: scaleY(1.02);
}

.bar.green { background-color: #27ae60; }
.bar.orange { background-color: #f39c12; }
.bar.red { background-color: #e74c3c; }
.bar.gray { background-color: #95a5a6; }

.topic-name {
    font-size: 13px;
    text-align: center;
    word-wrap: break-word;
    font-weight: 500;
    color: #34495e;
    padding: 0 5px;
}

.topic-name-wrapper {
    display: flex;
    justify-content: center;
}

.legend {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 25px;
    margin-top: 30px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 6px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #2c3e50;
}

.legend-color {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    flex-shrink: 0;
}

.legend-green { background-color: #27ae60; }
.legend-orange { background-color: #f39c12; }
.legend-red { background-color: #e74c3c; }
.legend-gray { background-color: #95a5a6; }

@media (max-width: 768px) {
    .chart-container,
    .topic-labels {
        gap: 25px;
    }

    .bar {
        width: 16px;
    }

    .topic-name {
        font-size: 12px;
    }

    .legend {
        gap: 15px;
    }
}

.no-data-message {
    text-align: center;
    padding: 40px;
    color: #7f8c8d;
    font-size: 16px;
}
</style>

<div class="progress-container">
    <div class="chart-wrapper">
        <?php if (empty($data)): ?>
            <div class="no-data-message">No progress data available yet.</div>
        <?php else: ?>
            <div class="chart-area">
                <div class="y-axis">
                    <div>1.0</div>
                    <div>0.8</div>
                    <div>0.6</div>
                    <div>0.4</div>
                    <div>0.2</div>
                    <div>0.0</div>
                </div>

                <div class="chart-columns-wrapper">
                    <!-- Chart bars -->
                    <div class="chart-container">
                        <?php foreach ($data as $topic_id => $info): ?>
                            <?php
                                $topic = htmlspecialchars($info['topic_name']);
                                $scores = $info['scores'];
                                $attempts = min(intval($info['attempts']), count($scores));
                            ?>
                            <div class="topic-column">
                                <div class="attempt-bars">
                                    <?php for ($i = 1; $i <= $attempts; $i++): 
                                        $score = floatval($scores["$i"]);
                                        $height = max(10, intval($score * 200));
                                        $colorClass = 'gray';
                                        if ($score >= 0.8) $colorClass = 'green';
                                        elseif ($score > 0.4) $colorClass = 'orange';
                                        elseif ($score > 0) $colorClass = 'red';
                                    ?>
                                        <div class="bar <?= $colorClass ?>" 
                                             style="height: <?= $height ?>px;" 
                                             title="<?= $topic ?> - Attempt <?= $i ?>: <?= number_format($score * 100, 1) ?>%">
                                        </div>
                                    <?php endfor; ?>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>

                    <!-- Topic names -->
                    <div class="topic-labels">
                        <?php foreach ($data as $topic_id => $info): ?>
                            <?php
                                $attempts = min(intval($info['attempts']), count($info['scores']));
                                $barWidth = 20;
                                $gap = 5;
                                $groupWidth = ($barWidth * $attempts) + ($gap * ($attempts - 1));
                            ?>
                            <div class="topic-name-wrapper" style="width: <?= $groupWidth ?>px; display: flex; justify-content: center;">
                                <div class="topic-name"><?= htmlspecialchars($info['topic_name']) ?></div>
                            </div>
                        <?php endforeach; ?>
                    </div>

                </div>
            </div>

            <!-- Legend -->
            <div class="legend">
                <div class="legend-item"><div class="legend-color legend-green"></div> High (≥ 80%)</div>
                <div class="legend-item"><div class="legend-color legend-orange"></div> Medium (40-79%)</div>
                <div class="legend-item"><div class="legend-color legend-red"></div> Low (1-39%)</div>
                <div class="legend-item"><div class="legend-color legend-gray"></div> Attempted (0%)</div>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php echo $OUTPUT->footer(); ?>