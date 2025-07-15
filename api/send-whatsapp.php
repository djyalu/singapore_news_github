<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// OPTIONS 요청 처리
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// WhatsApp API 설정
$api_url = 'https://gate.whapi.cloud/messages/text';
$api_token = 'ZCF4emVil1iJLNRJ6Sb7ce7TsyctIEYq';

// POST 데이터 받기
$input = json_decode(file_get_contents('php://input'), true);

// 디버깅을 위한 로깅
error_log('WhatsApp API Request: ' . json_encode($input));

if (!isset($input['channel']) || !isset($input['message'])) {
    echo json_encode(['success' => false, 'error' => '필수 파라미터가 누락되었습니다.']);
    exit;
}

$channel = $input['channel'];
$message = $input['message'];

// 채널 ID 형식 변환 (그룹의 경우 @g.us 제거하고 그룹 ID만 사용)
// WhatsApp API는 일반적으로 전화번호 형식을 사용
if (strpos($channel, '@g.us') !== false) {
    // 그룹 채널인 경우 - WhatsApp API 형식에 맞게 변환
    $channel = str_replace('@g.us', '', $channel);
}

// WhatsApp API 호출
$data = [
    'to' => $channel,
    'body' => $message,
    'typing_time' => 0
];

$ch = curl_init($api_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Authorization: Bearer ' . $api_token
]);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

$result = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlError = curl_error($ch);
curl_close($ch);

// 응답 로깅
error_log('WhatsApp API Response: ' . $result);
error_log('HTTP Code: ' . $httpCode);

if ($curlError) {
    echo json_encode(['success' => false, 'error' => 'CURL 오류: ' . $curlError]);
} else if ($result === FALSE) {
    echo json_encode(['success' => false, 'error' => 'API 호출 실패']);
} else {
    $response = json_decode($result, true);
    if ($httpCode === 200 || $httpCode === 201) {
        echo json_encode(['success' => true, 'message_id' => $response['id'] ?? 'unknown', 'response' => $response]);
    } else {
        $errorMessage = $response['message'] ?? $response['error'] ?? '알 수 없는 오류';
        echo json_encode(['success' => false, 'error' => $errorMessage, 'http_code' => $httpCode, 'response' => $response]);
    }
}
?>