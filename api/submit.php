<?php
/**
 * Form submission handler for La Bible de l'IA
 * Handles: newsletter, contact, submit-tool forms
 * Sends email to contact@labibledelia.com
 */

// CORS & Security
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

// Only accept POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Rate limiting (simple file-based, 10 submissions per IP per hour)
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rate_file = sys_get_temp_dir() . '/form_rate_' . md5($ip);
$now = time();
$submissions = [];

if (file_exists($rate_file)) {
    $submissions = json_decode(file_get_contents($rate_file), true) ?: [];
    // Keep only last hour
    $submissions = array_filter($submissions, fn($t) => ($now - $t) < 3600);
}

if (count($submissions) >= 10) {
    http_response_code(429);
    echo json_encode(['error' => 'Too many submissions. Please try again later.']);
    exit;
}

$submissions[] = $now;
file_put_contents($rate_file, json_encode($submissions));

// Honeypot check
if (!empty($_POST['bot-field'])) {
    // Bot detected, fake success
    echo json_encode(['success' => true]);
    exit;
}

// Get form type
$form_name = $_POST['form-name'] ?? '';
$to = 'contact@labibledelia.com';

// Build email based on form type
switch ($form_name) {
    case 'newsletter-fr':
    case 'newsletter-en':
        $email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);
        if (!$email) {
            http_response_code(400);
            echo json_encode(['error' => 'Invalid email']);
            exit;
        }
        $subject = "[Bible IA] Nouvelle inscription newsletter";
        $body = "Nouvelle inscription newsletter :\n\n";
        $body .= "Email : {$email}\n";
        $body .= "Langue : " . ($form_name === 'newsletter-fr' ? 'Français' : 'English') . "\n";
        $body .= "Date : " . date('Y-m-d H:i:s') . "\n";
        $body .= "IP : {$ip}\n";
        break;

    case 'contact-fr':
    case 'contact-en':
        $name = htmlspecialchars($_POST['nom'] ?? $_POST['name'] ?? '');
        $email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);
        $sujet = htmlspecialchars($_POST['sujet'] ?? $_POST['subject'] ?? '');
        $message = htmlspecialchars($_POST['message'] ?? '');

        if (!$email || !$message) {
            http_response_code(400);
            echo json_encode(['error' => 'Missing required fields']);
            exit;
        }

        $subject = "[Bible IA] Contact : {$sujet}";
        $body = "Nouveau message de contact :\n\n";
        $body .= "Nom : {$name}\n";
        $body .= "Email : {$email}\n";
        $body .= "Sujet : {$sujet}\n";
        $body .= "Message :\n{$message}\n\n";
        $body .= "Date : " . date('Y-m-d H:i:s') . "\n";
        break;

    case 'submit-tool-fr':
    case 'submit-tool-en':
        $tool_name = htmlspecialchars($_POST['tool-name'] ?? '');
        $tool_url = htmlspecialchars($_POST['tool-url'] ?? '');
        $category = htmlspecialchars($_POST['category'] ?? '');
        $pricing = htmlspecialchars($_POST['pricing'] ?? '');
        $launch_year = htmlspecialchars($_POST['launch-year'] ?? '');
        $description = htmlspecialchars($_POST['description'] ?? '');
        $submitter_name = htmlspecialchars($_POST['submitter-name'] ?? '');
        $submitter_email = filter_var($_POST['submitter-email'] ?? '', FILTER_VALIDATE_EMAIL);
        $relation = htmlspecialchars($_POST['relation'] ?? '');

        if (!$tool_name || !$tool_url || !$submitter_email) {
            http_response_code(400);
            echo json_encode(['error' => 'Missing required fields']);
            exit;
        }

        $subject = "[Bible IA] Nouvel outil soumis : {$tool_name}";
        $body = "Nouvel outil soumis :\n\n";
        $body .= "=== OUTIL ===\n";
        $body .= "Nom : {$tool_name}\n";
        $body .= "URL : {$tool_url}\n";
        $body .= "Catégorie : {$category}\n";
        $body .= "Tarification : {$pricing}\n";
        $body .= "Année : {$launch_year}\n";
        $body .= "Description : {$description}\n\n";
        $body .= "=== SOUMIS PAR ===\n";
        $body .= "Nom : {$submitter_name}\n";
        $body .= "Email : {$submitter_email}\n";
        $body .= "Relation : {$relation}\n\n";
        $body .= "Date : " . date('Y-m-d H:i:s') . "\n";
        break;

    default:
        http_response_code(400);
        echo json_encode(['error' => 'Unknown form']);
        exit;
}

// Send email
$headers = "From: noreply@labibledelia.com\r\n";
$headers .= "Reply-To: " . ($email ?? 'noreply@labibledelia.com') . "\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "X-Mailer: BibleIA-Forms/1.0\r\n";

$sent = mail($to, $subject, $body, $headers);

if ($sent) {
    echo json_encode(['success' => true]);
} else {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to send email']);
}
