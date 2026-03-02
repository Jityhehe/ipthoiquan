import requests

def generate_m3u():
    # API cung cấp danh sách trận đấu
    api_url = "https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Mở file để ghi
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            # Duyệt qua mảng dữ liệu (thường nằm trong data['data'])
            items = data.get('data', [])
            for item in items:
                # Lấy tên đội nhà và đội khách
                home = item.get('home_team', {}).get('name', 'Unknown')
                away = item.get('away_team', {}).get('name', 'Unknown')
                name = f"{home} vs {away}"
                
                # Lấy link stream (thay đổi 'link' tùy theo thực tế API trả về)
                # Thường là item['stream_links'][0]['link'] hoặc tương tự
                links = item.get('links', [])
                if links:
                    stream_url = links[0].get('link') # Lấy link đầu tiên
                    f.write(f"#EXTINF:-1 tvg-logo='' group-title='Bóng Đá Trực Tiếp', {name}\n")
                    f.write(f"{stream_url}\n")
                    
        print("Cập nhật file M3U thành công!")
        
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    generate_m3u()
