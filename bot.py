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
            # 1. Xử lý thời gian (GMT+7)
            utc_time_str = fixture.get('startTime', '')
            dt_vn = datetime.max
            if utc_time_str:
                try:
                    dt_utc = datetime.strptime(utc_time_str[:19], '%Y-%m-%dT%H:%M:%S')
                    dt_vn = dt_utc + timedelta(hours=7)
                except:
                    pass

            # 2. Phân loại nhóm thể thao
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

            # 3. Lọc link chất lượng cao (Full HD hoặc FHD)
            stream_url = None
            commentators = fixture.get('fixtureCommentators', [])
            for comm_entry in commentators:
                if stream_url: break 
                streams = comm_entry.get('commentator', {}).get('streams', [])
                for s in streams:
                    s_name = s.get('name', '').upper().replace(" ", "")
                    # Kiểm tra xem tên có chứa 'FULLHD' hoặc 'FHD' không
                    if "FULLHD" in s_name or "FHD" in s_name:
                        stream_url = s.get('sourceUrl')
                        if stream_url:
                            break
            
            if stream_url:
                fixtures_list.append({
                    'time_obj': dt_vn,
                    'group': group_label,
                    'title': fixture.get('title'),
                    'logo': fixture.get('homeTeam', {}).get('logoUrl', ''),
                    'url': stream_url
                })

        # 4. Sắp xếp theo giờ thi đấu
        fixtures_list.sort(key=lambda x: x['time_obj'])

        # 5. Ghi file M3U
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in fixtures_list:
                time_str = item['time_obj'].strftime('%H:%M') if item['time_obj'] != datetime.max else "Live"
                display_name = f"{time_str} [{item['group']}] {item['title']}"
                f.write(f"#EXTINF:-1 tvg-logo='{item['logo']}' group-title='{item['group']}', {display_name}\n")
                f.write(f"{item['url']}\n")
                
        print(f"Thành công! Đã quét được {len(fixtures_list)} trận chất lượng cao.")
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    generate_m3u()
