Đặc điểm v1:
- Đơn giản
- Không có bảo mật
- Mất dữ liệu khi restart server

Đặc điểm v2:
- Có xác thực user bằng JWT
- Dữ liệu lưu vào DB
- Hỗ trợ Idempotency-Key để tránh thanh toán trùng.

-> So sánh v1 với v2:
- v2 có phương thức xác thực JWT -> Mức độ bảo mật cao hơn
- v2 có nơi lưu trữ dữ liệu thanh toán
- v2 có header có chứa Idempotency-Key để tránh double payment
- v2 có thêm GET /api/v2/payments/<int:payment_id>