import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiaWF0IjoxNzYwOTc3MzczLCJleHAiOjE3NjA5ODQ1NzN9.7AlvkdXkv2rb6OKNnUYYz3NXP_3R0QQEm87c24-oIso"
secret = "abc!@#123"  # Thay bằng SECRET_KEY trong app.py

try:
    data = jwt.decode(token, secret, algorithms=["HS256"])
    print("✅ Signature OK. Payload:", data)
except Exception as e:
    print("❌ Verify failed:", type(e).__name__, e)