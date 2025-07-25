from app.main import app

def test_home_endpoint_integration():
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.get_data(as_text=True)
        assert "My public IP is:" in data

        # Extract the IP and validate format
        ip = data.split("My public IP is: ")[-1].strip()
        segments = ip.split(".")
        assert len(segments) == 4 and all(seg.isdigit() for seg in segments)
        assert all(0 <= int(seg) <= 255 for seg in segments)
