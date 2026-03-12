import requests
from datetime import datetime, timedelta

# Header dùng chung để tránh bị chặn
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def save_m3u(filename, fixtures):
    """Hàm ghi file M3U dùng chung cho cả 2 nguồn"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            # Sắp xếp theo thời gian tăng dần
            fixtures.sort(key=lambda x: x['time'])
            for item in fixtures:
                time_str = item['time'].strftime('%H:%M') if item['time'] != datetime.max else "Live"
                display_name = f"{time_str} [{item['group']}] {item['title']}"
                
                # Thêm User-Agent vào link để xem mượt trên VLC/Mon Player
                final_url = f"{item['url']}|User-Agent={HEADERS['User-Agent']}"
                
                f.write(f"#EXTINF:-1 tvg-logo='{item['logo']}' group-title='{item['provider']}', {display_name}\n")
                f.write(f"{final_url}\n")
        print(f"--- Đã tạo xong {filename} ({len(fixtures)} trận) ---")
    except Exception as e:
        print(f"Lỗi khi ghi file {filename}: {e}")

def process_hoiquan():
    """Xử lý nguồn HoiQuanTV -> playlist.m3u"""
    url = "https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished"
    fixtures = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=15).json()
        for item in res.get('data', []):
            dt_vn = datetime.max
            if item.get('startTime'):
                dt_vn = datetime.strptime(item['startTime'][:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=7)
            
            stream_url = None
            for comm in item.get('fixtureCommentators', []):
                if stream_url: break
                for s in comm.get('commentator', {}).get('streams', []):
                    name = s.get('name', '').upper().replace(" ", "")
                    # Nhận diện cả Full HD và FHD
                    if "FULLHD" in name or "FHD" in name:
                        stream_url = s.get('sourceUrl')
                        break
            
            if stream_url:
                fixtures.append({
                    'time': dt_vn,
                    'group': "HoiQuanTV",
                    'title': item.get('title'),
                    'logo': item.get('homeTeam', {}).get('logoUrl', ''),
                    'url': stream_url,
                    'provider': 'HoiQuanTV'
                })
    except: pass
    return fixtures

def process_vongcam():
    """Xử lý nguồn VongcamTV -> vongcam.m3u"""
    url = "https://sv.bugiotv.xyz/internal/api/matches"
    fixtures = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=15).json()
        for item in res.get('data', []):
            # Xử lý giờ VN
            dt_vn = datetime.max
            if item.get('startTime'):
                dt_vn = datetime.strptime(item['startTime'][:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=7)

            # Lấy link FHD từ cấu trúc JSON Vongcam
            commentator = item.get('commentator', {})
            stream_url = commentator.get('streamSourceFhd')
            
            if stream_url:
                fixtures.append({
                    'time': dt_vn,
                    'group': item.get('tournamentName', 'VongcamTV'),
                    'title': item.get('title'),
                    'logo': item.get('homeClub', {}).get('logoUrl', ''),
                    'url': stream_url,
                    'provider': 'VongcamTV'
                })
    except: pass
    return fixtures

if __name__ == "__main__":
    # 1. Chạy nguồn HoiQuan
    hq_data = process_hoiquan()
    save_m3u("playlist.m3u", hq_data)
    
    # 2. Chạy nguồn Vongcam
    vc_data = process_vongcam()
    save_m3u("vongcam.m3u", vc_data)
