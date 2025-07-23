import os
import json
import glob
from datetime import datetime, timedelta
import pytz

def cleanup_old_data(retention_days=30, max_size_mb=50):
    """
    30일 이전 또는 전체 용량 50MB 초과 시 오래된 데이터부터 삭제
    """
    # KST 기준으로 삭제 기준일 설정
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst).replace(tzinfo=None)  # naive datetime으로 변환
    cutoff_date = now_kst - timedelta(days=retention_days)
    deleted_files = []
    
    print(f"Cleaning up data older than {cutoff_date.strftime('%Y-%m-%d')} or exceeding {max_size_mb}MB...")
    
    # 1. 스크래핑 데이터 정리 (data/scraped/news_*.json)
    scraped_pattern = 'data/scraped/news_*.json'
    scraped_files = glob.glob(scraped_pattern)
    
    # 파일 정보 수집
    file_info = []
    total_size = 0
    
    for file_path in scraped_files:
        try:
            size = os.path.getsize(file_path)
            mtime = os.path.getmtime(file_path)
            
            # 파일명에서 날짜 추출 시도
            filename = os.path.basename(file_path)
            date_match = filename.replace('news_', '').replace('.json', '').split('_')[0]
            
            if len(date_match) == 8:
                file_date = datetime.strptime(date_match, '%Y%m%d')
            else:
                file_date = datetime.fromtimestamp(mtime)
            
            file_info.append({
                'path': file_path,
                'size': size,
                'date': file_date,
                'mtime': mtime
            })
            total_size += size
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    # 날짜순 정렬 (오래된 것부터)
    file_info.sort(key=lambda x: x['date'])
    
    # 용량 계산
    total_size_mb = total_size / (1024 * 1024)
    print(f"Current scraped data size: {total_size_mb:.2f} MB ({len(file_info)} files)")
    
    # 삭제 진행
    for file_data in file_info:
        file_path = file_data['path']
        file_date = file_data['date']
        file_size_mb = file_data['size'] / (1024 * 1024)
        
        # 30일 이전이거나 전체 용량이 50MB 초과인 경우 삭제
        should_delete = file_date < cutoff_date or total_size_mb > max_size_mb
        
        if should_delete:
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                total_size_mb -= file_size_mb
                print(f"Deleted: {os.path.basename(file_path)} ({file_size_mb:.2f} MB, {file_date.strftime('%Y-%m-%d')})")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        else:
            # 용량이 50MB 이하이고 30일 이내면 중단
            if total_size_mb <= max_size_mb:
                break
    
    # 2. 전송 이력 정리 (data/history/YYYYMM.json)
    history_pattern = 'data/history/*.json'
    history_files = glob.glob(history_pattern)
    
    for file_path in history_files:
        try:
            # 파일명에서 월 추출 (YYYYMM.json)
            filename = os.path.basename(file_path).replace('.json', '')
            
            if len(filename) == 6 and filename.isdigit():  # YYYYMM 형식
                file_date = datetime.strptime(filename + '01', '%Y%m%d')  # 월의 첫날로 변환
                
                if file_date < cutoff_date:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    print(f"Deleted history: {os.path.basename(file_path)}")
                else:
                    # 파일 내부의 오래된 항목들도 정리
                    cleanup_history_entries(file_path, cutoff_date)
                    
        except Exception as e:
            print(f"Error processing history file {file_path}: {e}")
    
    print(f"\nCleanup completed. Deleted {len(deleted_files)} files.")
    print(f"Final scraped data size: {total_size_mb:.2f} MB")
    return deleted_files

def cleanup_history_entries(history_file, cutoff_date):
    """
    이력 파일 내부의 30일 이전 항목들을 제거
    """
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if not isinstance(history, list):
            return
        
        original_count = len(history)
        filtered_history = []
        
        for entry in history:
            try:
                entry_date = None
                
                if 'timestamp' in entry:
                    entry_date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    entry_date = entry_date.replace(tzinfo=None)
                elif 'id' in entry and len(entry['id']) >= 8:
                    # timestamp가 없는 경우 id에서 날짜 추출 시도 (YYYYMMDDHHMMSS)
                    date_part = entry['id'][:8]
                    entry_date = datetime.strptime(date_part, '%Y%m%d')
                
                if entry_date is None or entry_date >= cutoff_date:
                    filtered_history.append(entry)
                    
            except Exception:
                # 날짜 파싱 실패 시 항목 유지
                filtered_history.append(entry)
        
        # 변경사항이 있을 때만 파일 업데이트
        if len(filtered_history) < original_count:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_history, f, ensure_ascii=False, indent=2)
            
            removed_count = original_count - len(filtered_history)
            print(f"Cleaned {removed_count} old entries from {os.path.basename(history_file)}")
            
    except Exception as e:
        print(f"Error cleaning history entries: {e}")

def get_data_usage_stats():
    """
    현재 데이터 사용량 통계 반환
    """
    stats = {
        'scraped_files': 0,
        'scraped_size_mb': 0,
        'history_files': 0,
        'history_size_mb': 0,
        'total_size_mb': 0,
        'oldest_scraped': None,
        'newest_scraped': None
    }
    
    # 스크래핑 파일 통계
    scraped_files = glob.glob('data/scraped/news_*.json')
    stats['scraped_files'] = len(scraped_files)
    
    scraped_size = 0
    dates = []
    
    for file_path in scraped_files:
        try:
            scraped_size += os.path.getsize(file_path)
            
            # 날짜 추출
            filename = os.path.basename(file_path)
            date_part = filename.replace('news_', '').replace('.json', '').split('_')[0]
            if len(date_part) == 8:
                dates.append(datetime.strptime(date_part, '%Y%m%d'))
        except:
            continue
    
    stats['scraped_size_mb'] = round(scraped_size / (1024 * 1024), 2)
    
    if dates:
        stats['oldest_scraped'] = min(dates).strftime('%Y-%m-%d')
        stats['newest_scraped'] = max(dates).strftime('%Y-%m-%d')
    
    # 히스토리 파일 통계
    history_files = glob.glob('data/history/*.json')
    stats['history_files'] = len(history_files)
    
    history_size = 0
    for file_path in history_files:
        try:
            history_size += os.path.getsize(file_path)
        except:
            continue
    
    stats['history_size_mb'] = round(history_size / (1024 * 1024), 2)
    stats['total_size_mb'] = round((scraped_size + history_size) / (1024 * 1024), 2)
    
    return stats

if __name__ == "__main__":
    print("=== Data Cleanup Tool (30 days / 50MB limit) ===")
    
    # 현재 상태 확인
    print("\nCurrent data usage:")
    stats = get_data_usage_stats()
    print(f"  Scraped: {stats['scraped_files']} files, {stats['scraped_size_mb']} MB")
    print(f"  History: {stats['history_files']} files, {stats['history_size_mb']} MB")
    print(f"  Total: {stats['total_size_mb']} MB")
    if stats['oldest_scraped']:
        print(f"  Date range: {stats['oldest_scraped']} ~ {stats['newest_scraped']}")
    
    # 정리 실행 (30일 또는 50MB 제한)
    print(f"\nStarting cleanup...")
    deleted_files = cleanup_old_data(retention_days=30, max_size_mb=50)
    
    # 정리 후 상태 확인
    print(f"\nData usage after cleanup:")
    stats_after = get_data_usage_stats()
    print(f"  Scraped: {stats_after['scraped_files']} files, {stats_after['scraped_size_mb']} MB")
    print(f"  History: {stats_after['history_files']} files, {stats_after['history_size_mb']} MB")
    print(f"  Total: {stats_after['total_size_mb']} MB")
    
    size_saved = stats['total_size_mb'] - stats_after['total_size_mb']
    if size_saved > 0:
        print(f"  Space saved: {round(size_saved, 2)} MB")