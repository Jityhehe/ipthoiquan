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
            # 1. Thời gian Việt Nam
            utc_time_str = fixture.get('startTime', '')
            dt_vn = None
            display_time = "Live"
            
            if utc_time_str:
                try:
                    dt_utc = datetime.strptime(utc_time_str[:19], '%Y-%m-%dT%H:%M:%S')
                    dt_vn = dt_utc + timedelta(hours=7)
                    display_time = dt_vn.strftime('%H:%M')
                except:
                    pass

            # 2. Phân loại nhóm (Thêm Icon vào tên nhóm để dễ nhìn)
            sport_info = fixture.get('sport', {})
            sport_name_raw = sport_info.get('name', '').lower()
            
            if "bóng đá" in sport_name_raw:
                group = "Bóng Đá"
                icon = "⚽"
            elif "bóng rổ" in sport_name_raw:
                group = "Bóng Rổ"
                icon = "🏀"
            elif any(x in sport_name_raw for x in ["esport", "liên minh", "dota", "csgo", "valorant"]):
                group = "Esport"
                icon = "🎮"
            else:
                group = "Khác"
                icon = "📺"

            # 3. Mò link Full HD
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
                    'icon': icon,
                    'title': fixture.get('title'),
                    'logo': fixture.get('homeTeam', {}).get('logoUrl', ''),
                    'url': stream_url
                })

        # 4. SẮP XẾP: Theo Nhóm trước (A-Z), sau đó mới đến Thời gian
        # Điều này giúp các trận Bóng Đá nằm cùng nhau, Bóng Rổ cùng nhau...
        fixtures_list.sort(key=lambda x: (x['group'], x['time_obj']))

        # 5. GHI FILE M3U
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            current_group = ""
            for item in fixtures_list:
                # Tạo tên hiển thị cực kỳ rõ ràng: [Bóng Đá] 20:00 | Tên trận
                display_name = f"[{item['group']}] {item['time_obj'].strftime('%H:%M')} | {item['title']}"
                
                # Ghi cả thuộc tính chuẩn và tên hiển thị bao quát
                f.write(f"#EXTINF:-1 tvg-logo='{item['logo']}' group-title='{item['group']}', {display_name}\n")
                f.write(f"{item['url']}\n")
                
        print(f"Thành công! Đã cập nhật {len(fixtures_list)} trận.")
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    generate_m3u()
