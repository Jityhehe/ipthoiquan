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
                
                commentators = fixture.get('fixtureCommentators', [])
                if commentators:
                    # Lấy danh sách luồng từ bình luận viên đầu tiên
                    streams = commentators[0].get('commentator', {}).get('streams', [])
                    for stream in streams:
                        stream_raw_name = stream.get('name', '')
                        
                        # CHỈ LẤY NẾU TÊN LUỒNG CÓ CHỮ 'FULL HD'
                        if "FULL HD" in stream_raw_name.upper():
                            url = stream.get('sourceUrl')
                            if url:
                                # Ghi vào file M3U (loại bỏ phần tên chất lượng trong ngoặc cho sạch)
                                f.write(f"#EXTINF:-1 tvg-logo='{logo}' group-title='HoiQuanTV Full HD', {title}\n")
                                f.write(f"{url}\n")
                                
        print("Đã cập nhật chỉ các link Full HD!")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    generate_m3u()
