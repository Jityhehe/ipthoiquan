import requests

def generate_m3u():
    api_url = "https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished"
    try:
        response = requests.get(api_url)
        data = response.json()
        
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            # Giả sử cấu trúc JSON là data -> matches
            for item in data.get('data', []):
                name = f"{item.get('home_team')} vs {item.get('away_team')}"
                # Lấy link stream m3u8 từ API
                link = item.get('stream_url', '') 
                
                if link:
                    f.write(f"#EXTINF:-1 group-title='Live Football', {name}\n")
                    f.write(f"{link}\n")
        print("Đã cập nhật playlist.m3u")
    except Exception as e:
        print(f"Lỗi rồi: {e}")

if __name__ == "__main__":
    generate_m3u()
