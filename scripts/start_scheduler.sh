#!/bin/bash
# Singapore News WhatsApp Scheduler Starter Script

cd "$(dirname "$0")/.."

echo "Starting Singapore News WhatsApp Scheduler..."
echo "Working directory: $(pwd)"

# Python 가상환경이 있다면 활성화
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# 필요한 패키지 설치
echo "Installing required packages..."
pip install schedule pytz requests beautifulsoup4

# 스케줄러 실행
echo "Starting scheduler..."
python scripts/scheduler.py