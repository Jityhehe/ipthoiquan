import requests

def generate_m3u():
    api_url = "https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished"
    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for fixture in data.get('data', []):
                title = fixture.get('title', 'Trận đấu không tên')
                logo = fixture.get('homeTeam', {}).get('logoUrl', '')
                
                # Mò vào lấy link stream từ BLV đầu tiên
                commentators = fixture.get('fixtureCommentators', [])
                if commentators:
                    streams = commentators[0].get('commentator', {}).get('streams', [])
                    for stream in streams:
                        # Chỉ lấy link Full HD cho nhẹ list, hoặc lấy tất cả
                        stream_name = f"{title} ({stream.get('name')})"
                        url = stream.get('sourceUrl')
                        if url:
                            f.write(f"#EXTINF:-1 tvg-logo='{logo}' group-title='Bóng Rổ/Bóng Đá/Esport', {stream_name}\n")
                            f.write(f"{url}\n")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    generate_m3u()
