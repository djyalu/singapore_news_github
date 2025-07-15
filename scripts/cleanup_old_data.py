import os
import json
import glob
from datetime import datetime, timedelta

def cleanup_old_data(retention_days=30):
    """
    30일 이전의 스크래핑 데이터와 전송 이력을 자동 삭제
    """
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_files = []
    
    print(f"Cleaning up data older than {cutoff_date.strftime('%Y-%m-%d')}...")
    
    # 1. 스크래핑 데이터 정리 (data/scraped/news_*.json)
    scraped_pattern = 'data/scraped/news_*.json'
    scraped_files = glob.glob(scraped_pattern)
    
    for file_path in scraped_files:
        try:
            # 파일명에서 날짜 추출 (news_YYYYMMDD_HHMMSS.json)
            filename = os.path.basename(file_path)
            date_part = filename.replace('news_', '').replace('.json', '').split('_')[0]
            
            if len(date_part) == 8:  # YYYYMMDD 형식
                file_date = datetime.strptime(date_part, '%Y%m%d')
                
                if file_date < cutoff_date:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    print(f"Deleted scraped file: {file_path}")
                    
        except (ValueError, IndexError) as e:
            print(f"Skipping file with invalid date format: {file_path} ({e})")
            continue
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    
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
                    print(f"Deleted history file: {file_path}")
                else:
                    # 파일 내부의 오래된 항목들도 정리
                    cleanup_history_entries(file_path, cutoff_date)
                    
        except (ValueError, IndexError) as e:
            print(f"Skipping file with invalid date format: {file_path} ({e})")
            continue
        except Exception as e:
            print(f"Error processing history file {file_path}: {e}")
    
    print(f"Cleanup completed. Deleted {len(deleted_files)} files.")
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
                if 'timestamp' in entry:
                    entry_date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    # timezone 정보 제거 후 비교
                    entry_date = entry_date.replace(tzinfo=None)
                    
                    if entry_date >= cutoff_date:
                        filtered_history.append(entry)
                elif 'id' in entry:
                    # timestamp가 없는 경우 id에서 날짜 추출 시도 (YYYYMMDDHHMMSS)
                    if len(entry['id']) >= 8:
                        date_part = entry['id'][:8]
                        entry_date = datetime.strptime(date_part, '%Y%m%d')
                        
                        if entry_date >= cutoff_date:
                            filtered_history.append(entry)
                else:
                    # 날짜 정보가 없는 항목은 유지
                    filtered_history.append(entry)
                    
            except (ValueError, TypeError) as e:
                # 날짜 파싱 실패 시 항목 유지
                filtered_history.append(entry)
        
        # 변경사항이 있을 때만 파일 업데이트
        if len(filtered_history) < original_count:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_history, f, ensure_ascii=False, indent=2)
            
            removed_count = original_count - len(filtered_history)
            print(f"Cleaned up {removed_count} old entries from {history_file}")
            
    except Exception as e:
        print(f"Error cleaning up history entries in {history_file}: {e}")

def get_data_usage_stats():
    """
    현재 데이터 사용량 통계 반환
    """
    stats = {
        'scraped_files': 0,
        'history_files': 0,
        'total_size_mb': 0,
        'oldest_scraped': None,
        'newest_scraped': None
    }
    
    # 스크래핑 파일 통계
    scraped_files = glob.glob('data/scraped/news_*.json')
    stats['scraped_files'] = len(scraped_files)
    
    if scraped_files:
        dates = []
        for file_path in scraped_files:
            try:
                filename = os.path.basename(file_path)
                date_part = filename.replace('news_', '').replace('.json', '').split('_')[0]
                if len(date_part) == 8:
                    dates.append(datetime.strptime(date_part, '%Y%m%d'))
            except:
                continue
        
        if dates:
            stats['oldest_scraped'] = min(dates).strftime('%Y-%m-%d')
            stats['newest_scraped'] = max(dates).strftime('%Y-%m-%d')
    
    # 히스토리 파일 통계
    history_files = glob.glob('data/history/*.json')
    stats['history_files'] = len(history_files)
    
    # 전체 크기 계산
    all_files = scraped_files + history_files
    total_size = 0
    for file_path in all_files:
        try:
            total_size += os.path.getsize(file_path)
        except:
            continue
    
    stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
    
    return stats

if __name__ == "__main__":
    print("=== Data Cleanup Tool ===")
    
    # 현재 상태 확인
    print("\nCurrent data usage:")
    stats = get_data_usage_stats()
    print(f"  Scraped files: {stats['scraped_files']}")
    print(f"  History files: {stats['history_files']}")
    print(f"  Total size: {stats['total_size_mb']} MB")
    if stats['oldest_scraped']:
        print(f"  Date range: {stats['oldest_scraped']} ~ {stats['newest_scraped']}")
    
    # 정리 실행
    print(f"\nStarting cleanup (30-day retention)...")
    deleted_files = cleanup_old_data(30)
    
    # 정리 후 상태 확인
    print(f"\nData usage after cleanup:")
    stats_after = get_data_usage_stats()
    print(f"  Scraped files: {stats_after['scraped_files']} (was {stats['scraped_files']})")
    print(f"  History files: {stats_after['history_files']} (was {stats['history_files']})")
    print(f"  Total size: {stats_after['total_size_mb']} MB (was {stats['total_size_mb']} MB)")
    
    size_saved = stats['total_size_mb'] - stats_after['total_size_mb']
    if size_saved > 0:
        print(f"  Space saved: {size_saved} MB")