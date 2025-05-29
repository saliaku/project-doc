<?php
require_once('../../config.php');
require_login();

$PAGE->set_context(context_system::instance());  // Or course context if inside a course
$PAGE->set_url(new moodle_url('/local/learningpath/dashboard.php'));

if (session_status() == PHP_SESSION_NONE) {
    session_start();
}

$userid = $USER->id;
$pythonPath = '/usr/bin/python3';
$scriptPath = '/var/www/html/moodle/local/learningpath/get_dashboard_data.py';
$command = escapeshellcmd("$pythonPath $scriptPath $userid 2>&1");
$output = shell_exec($command);

echo $OUTPUT->header();
echo $OUTPUT->heading("Your Learning Style Dashboard");

if (!$output) {
    echo "<p>Error fetching dashboard data. No output from script.</p>";
    echo $OUTPUT->footer();
    exit;
}

$data = json_decode($output, true);

if (!is_array($data) || isset($data['error'])) {
    echo "<p>Error fetching dashboard data: " . htmlspecialchars($data['error'] ?? 'Unknown error') . "</p>";
    echo $OUTPUT->footer();
    exit;
}

$v = $data['v'];
$a = $data['a'];
$t = $data['t'];
?>

<canvas id="vatChart" width="600" height="400" style="margin: 40px auto; display: block;"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    const ctx = document.getElementById('vatChart').getContext('2d');

    const data = {
        labels: ['Visual', 'Auditory', 'Textual'],
        datasets: [{
            label: 'Learning Style Strength',
            data: [<?= $v ?>, <?= $a ?>, <?= $t ?>],
            backgroundColor: ['#3498db', '#2ecc71', '#e67e22'],
            borderRadius: 10,
            barThickness: 50
        }]
    };

    const options = {
        plugins: {
            title: {
                display: true,
                text: 'Your Learning Style Distribution',
                font: {
                    size: 24,
                    weight: 'bold'
                },
                color: '#333',
                padding: {
                    top: 20,
                    bottom: 30
                }
            },
            tooltip: {
                backgroundColor: '#333',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#fff',
                borderWidth: 1
            },
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 1,
                ticks: {
                    color: '#333',
                    font: {
                        size: 16
                    }
                },
                grid: {
                    color: '#eee'
                }
            },
            x: {
                ticks: {
                    color: '#333',
                    font: {
                        size: 16
                    }
                },
                grid: {
                    display: false
                }
            }
        }
    };

    new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
</script>

<?php
echo $OUTPUT->footer();
