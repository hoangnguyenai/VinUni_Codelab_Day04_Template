# Starter Code — Lab #4

> Dành cho học viên VinUni AI Product Labs.

## Cách Sử Dụng

1. **Cài đặt môi trường:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Các phần đã hoàn thiện:**
   - `tools.py`: tra cứu JSON, lọc danh mục/giá, lưu nối tiếp ticket và hai JSON Schemas.
   - `template.py`: System Prompt đủ 5 phần, baseline tĩnh, nhận diện ý định độc lập,
     Agent Loop có trace và giới hạn số bước.
   - Xử lý kết quả rỗng, lỗi đọc/ghi dữ liệu, thiếu tên khách hàng và câu hỏi ngoài phạm vi.

3. **Chạy thử:**
   ```bash
   python3 template.py
   ```

4. **Kiểm thử autograder:**
   ```bash
   python3 -m pytest ../autograder/test_agent.py -v
   ```

   Chạy cả 8 test gốc và các test bổ sung bằng dữ liệu tạm, từ thư mục gốc dự án:
   ```bash
   python autograder/run_tests.py
   ```
   Runner sao chép JSON để không thêm ticket kiểm thử vào `raw-data`.
   Nếu cài pytest riêng bằng `python -m pip install --target .lab-deps -r starter-code/requirements.txt`,
   runner cũng tự tìm thư viện trong `.lab-deps`.

## Lưu Ý
- Code chạy ở chế độ **Mock Simulator** mặc định (không cần API key).
- Agent dùng keyword/regex, chưa tích hợp Live API; đặt `GEMINI_API_KEY` không chuyển sang chế độ live.
- `iterations` đếm bước thực thi: một tool hoặc FAQ cần 1 bước, hai tool cần 2 bước.
  Final Answer được tổng hợp ngay sau tool cuối cùng để khớp autograder.
- Giá và thông số chỉ lấy từ dữ liệu mẫu bài lab. FAQ bảo hành không đoán thời hạn khi chưa có nguồn xác minh.
