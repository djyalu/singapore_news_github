<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// WhatsApp API 설정
$api_url = 'https://gate.whapi.cloud/messages/text';
$api_token = 'ZCF4emVil1iJLNRJ6Sb7ce7TsyctIEYq';

// POST 데이터 받기
$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['channel']) || !isset($input['message'])) {
    echo json_encode(['success' => false, 'error' => '필수 파라미터가 누락되었습니다.']);
    exit;
}

$channel = $input['channel'];
$message = $input['message'];

// WhatsApp API 호출
$data = [
    'to' => $channel,
    'body' => $message
];

$options = [
    'http' => [
        'header' => [
            "Content-Type: application/json",
            "Authorization: Bearer $api_token"
        ],
        'method' => 'POST',
        'content' => json_encode($data)
    ]
];

$context = stream_context_create($options);
$result = @file_get_contents($api_url, false, $context);

if ($result === FALSE) {
    echo json_encode(['success' => false, 'error' => 'API 호출 실패']);
} else {
    $response = json_decode($result, true);
    if (isset($response['message_id'])) {
        echo json_encode(['success' => true, 'message_id' => $response['message_id']]);
    } else {
        echo json_encode(['success' => false, 'error' => $response['error'] ?? '알 수 없는 오류']);
    }
}
?>