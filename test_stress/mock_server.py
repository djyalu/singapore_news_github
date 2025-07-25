#!/usr/bin/env python3
"""
로컬 테스트용 모의 서버
실제 Vercel 서버 대신 사용하여 스트레스 테스트 수행
"""

from flask import Flask, jsonify, request
import random
import time
import json
from datetime import datetime, timezone, timedelta
import threading
import psutil
import os

app = Flask(__name__)

# KST 시간대
KST = timezone(timedelta(hours=9))

# 서버 상태 모니터링
class ServerMonitor:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.start_time = datetime.now(KST)
        self.response_times = []
        self.lock = threading.Lock()
        
    def record_request(self, response_time, is_error=False):
        with self.lock:
            self.request_count += 1
            if is_error:
                self.error_count += 1
            self.response_times.append(response_time)
            
            # 메모리 사용량 체크
            if self.request_count % 100 == 0:
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()
                print(f"[Monitor] Requests: {self.request_count}, Errors: {self.error_count}, Memory: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%")

monitor = ServerMonitor()

# 모의 데이터
MOCK_ARTICLES = [
    {
        "title": "Singapore Economy Shows Strong Growth",
        "content": "The Singapore economy has shown remarkable resilience...",
        "link": "https://example.com/article1",
        "published_date": datetime.now(KST).isoformat(),
        "source": "Channel NewsAsia",
        "group": "Economy"
    },
    {
        "title": "New Tech Hub Opens in Jurong",
        "content": "A new technology hub has opened its doors in Jurong...",
        "link": "https://example.com/article2",
        "published_date": datetime.now(KST).isoformat(),
        "source": "The Straits Times",
        "group": "Technology"
    }
]

# API 엔드포인트 구현
@app.route('/api/auth', methods=['POST'])
def auth():
    start_time = time.time()
    
    # 랜덤 지연 시뮬레이션
    time.sleep(random.uniform(0.1, 0.3))
    
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == 'Admin@123':
        response = jsonify({
            "success": True,
            "token": "mock_token_" + str(random.randint(1000, 9999))
        })
        status_code = 200
    else:
        response = jsonify({"error": "Invalid credentials"})
        status_code = 401
    
    monitor.record_request(time.time() - start_time, status_code != 200)
    return response, status_code

@app.route('/api/get-latest-scraped', methods=['GET'])
def get_latest_scraped():
    start_time = time.time()
    
    # 부하 시뮬레이션
    time.sleep(random.uniform(0.2, 0.5))
    
    # 10% 확률로 에러 발생
    if random.random() < 0.1:
        monitor.record_request(time.time() - start_time, True)
        return jsonify({"error": "Server error"}), 500
    
    response = jsonify({
        "scraped_date": datetime.now(KST).isoformat(),
        "articles": random.sample(MOCK_ARTICLES, min(len(MOCK_ARTICLES), 2)),
        "total_count": len(MOCK_ARTICLES)
    })
    
    monitor.record_request(time.time() - start_time)
    return response

@app.route('/api/trigger-scraping', methods=['POST'])
def trigger_scraping():
    start_time = time.time()
    
    # 긴 작업 시뮬레이션
    time.sleep(random.uniform(0.5, 1.0))
    
    # 20% 확률로 rate limit
    if random.random() < 0.2:
        monitor.record_request(time.time() - start_time, True)
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    response = jsonify({
        "success": True,
        "workflow_id": f"run_{random.randint(100000, 999999)}",
        "message": "Scraping workflow triggered"
    })
    
    monitor.record_request(time.time() - start_time)
    return response, 202

@app.route('/api/get-scraping-status', methods=['GET'])
def get_scraping_status():
    start_time = time.time()
    
    time.sleep(random.uniform(0.1, 0.3))
    
    statuses = ["idle", "running", "completed", "failed"]
    response = jsonify({
        "status": random.choice(statuses),
        "last_run": datetime.now(KST).isoformat(),
        "articles_scraped": random.randint(5, 20)
    })
    
    monitor.record_request(time.time() - start_time)
    return response

@app.route('/api/save-data', methods=['POST'])
def save_data():
    start_time = time.time()
    
    time.sleep(random.uniform(0.2, 0.4))
    
    # 5% 확률로 에러
    if random.random() < 0.05:
        monitor.record_request(time.time() - start_time, True)
        return jsonify({"error": "Failed to save data"}), 500
    
    response = jsonify({
        "success": True,
        "message": "Data saved successfully"
    })
    
    monitor.record_request(time.time() - start_time)
    return response

@app.route('/api/get-scraped-articles', methods=['GET'])
def get_scraped_articles():
    start_time = time.time()
    
    time.sleep(random.uniform(0.3, 0.6))
    
    # 쿼리 파라미터 처리
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    response = jsonify({
        "articles": MOCK_ARTICLES,
        "filtered_count": len(MOCK_ARTICLES),
        "date_range": {
            "start": start_date,
            "end": end_date
        }
    })
    
    monitor.record_request(time.time() - start_time)
    return response

@app.route('/', methods=['GET'])
def dashboard():
    start_time = time.time()
    
    time.sleep(random.uniform(0.1, 0.2))
    
    # 간단한 HTML 응답
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Singapore News Scraper</title></head>
    <body>
        <h1>Singapore News Scraper Dashboard</h1>
        <p>Mock server for stress testing</p>
        <p>Server Status: Running</p>
        <p>Requests Processed: {}</p>
        <p>Error Rate: {:.2f}%</p>
    </body>
    </html>
    """.format(
        monitor.request_count,
        (monitor.error_count / monitor.request_count * 100) if monitor.request_count > 0 else 0
    )
    
    monitor.record_request(time.time() - start_time)
    return html

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """서버 통계 조회"""
    uptime = (datetime.now(KST) - monitor.start_time).total_seconds()
    
    # 시스템 리소스
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    cpu_percent = process.cpu_percent()
    
    avg_response_time = sum(monitor.response_times) / len(monitor.response_times) if monitor.response_times else 0
    
    return jsonify({
        "uptime_seconds": uptime,
        "total_requests": monitor.request_count,
        "error_count": monitor.error_count,
        "error_rate": (monitor.error_count / monitor.request_count * 100) if monitor.request_count > 0 else 0,
        "average_response_time": avg_response_time,
        "memory_usage_mb": memory_mb,
        "cpu_usage_percent": cpu_percent,
        "requests_per_second": monitor.request_count / uptime if uptime > 0 else 0
    })

if __name__ == '__main__':
    print("모의 서버 시작 중...")
    print("서버 주소: http://localhost:5000")
    print("통계 조회: http://localhost:5000/api/stats")
    
    # 디버그 모드 비활성화로 성능 향상
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)