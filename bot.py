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
            display_time = "Đang cập nhật"
            
            if utc_time_str:
                try:
                    dt_utc = datetime.strptime(utc_time_str[:19], '%Y-%m-%dT%H:%M:%S')
                    dt_vn = dt_utc + timedelta(hours=7)
                    display_time = dt_vn.strftime('%H:%M - %d/%m')
                except:
                    pass

            # 2. Phân loại nhóm thể thao
            sport_info = fixture.get('sport', {})
            sport_name_raw = sport_info.get('name', '').lower()
            
            if "bóng đá" in sport_name_raw:
                group = "Bóng Đá"
            elif "bóng rổ" in sport_name_raw:
                group = "Bóng Rổ"
            elif any(x in sport_name_raw for x in ["esport", "liên minh", "dota", "csgo"]):
                group = "Esport"
            else:
                group = "Khác"

            # 3. Tìm duy nhất 1 link Full HD
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
                    'time_obj': dt_vn if dt_vn else datetime.max,
                    'group': group,
                    'display_name': f"{display_time} | {fixture.get('title')}",
                    'logo': fixture.get('homeTeam', {}).get('logoUrl', ''),
                    'url': stream_url
                })

        # 4. Sắp xếp theo thời gian (Trận sớm nhất lên đầu)
        fixtures_list.sort(key=lambda x: x['time_obj'])

        # 5. GHI FILE M3U
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in fixtures_list:
                # Ghi thông tin kênh với Group-title và Logo
                f.write(f"#EXTINF:-1 tvg-logo='{item['logo']}' group-title='{item['group']}', {item['display_name']}\n")
                f.write(f"{item['url']}\n")
                
        print(f"Thành công! Đã cập nhật {len(fixtures_list)} trận vào các nhóm.")
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    generate_m3u()
