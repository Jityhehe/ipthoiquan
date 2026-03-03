import requests
from datetime import datetime, timedelta

def generate_m3u():
    api_url = "https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        fixtures_list = []
        
        for fixture in data.get('data', []):
            # 1. Xử lý thời gian sang giờ Việt Nam (GMT+7)
            utc_time_str = fixture.get('startTime', '')
            dt_vn = None
            
            if utc_time_str:
                try:
                    # API trả về định dạng ISO 8601 (2026-03-03T17:00:00.000Z)
                    dt_utc = datetime.strptime(utc_time_str[:19], '%Y-%m-%dT%H:%M:%S')
                    dt_vn = dt_utc + timedelta(hours=7)
                except:
                    dt_vn = datetime.max # Nếu lỗi giờ thì đẩy xuống cuối

            # 2. Phân loại nhóm thể thao (Để gắn vào tên kênh)
            sport_info = fixture.get('sport', {})
            sport_name_raw = sport_info.get('name', '').lower()
            
            if "bóng đá" in sport_name_raw:
                group_label = "Bóng Đá"
            elif "bóng rổ" in sport_name_raw:
                group_label = "Bóng Rổ"
            elif any(x in sport_name_raw for x in ["esport", "liên minh", "dota", "csgo", "valorant"]):
                group_label = "Esport"
            else:
                group_label = "Khác"

            # 3. Lọc duy nhất 1 link Full HD
            stream_url = None
            commentators = fixture.get('fixtureCommentators', [])
            for comm_entry in commentators:
                if stream_url: break 
                streams = comm_entry.get('commentator', {}).get('streams', [])
                for s in streams:
                    if "FULL HD" in s.get('name', '').upper():
                        stream_url = s.get('sourceUrl')
                        break
            
            if stream_url:
                fixtures_list.append({
                    'time_obj': dt_vn,
                    'group': group_label,
                    'title': fixture.get('title'),
                    'logo': fixture.get('homeTeam', {}).get('logoUrl', ''),
                    'url': stream_url
                })

        # 4. SẮP XẾP CHÍNH: Theo Thời gian (Trận nào đá sớm nhất hiện lên đầu)
        fixtures_list.sort(key=lambda x: x['time_obj'])

        # 5. GHI FILE M3U
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            for item in fixtures_list:
                # Định dạng tên: "17:00 [Bóng Đá] Arsenal vs Liverpool"
                time_str = item['time_obj'].strftime('%H:%M')
                display_name = f"{time_str} [{item['group']}] {item['title']}"
                
                # Ghi thông tin M3U
                f.write(f"#EXTINF:-1 tvg-logo='{item['logo']}' group-title='{item['group']}', {display_name}\n")
                f.write(f"{item['url']}\n")
                
        print(f"Thành công! Đã sắp xếp theo giờ {len(fixtures_list)} trận.")
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    generate_m3u()
