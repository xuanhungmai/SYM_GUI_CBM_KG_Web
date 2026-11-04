# Hệ thống biện chứng luận trị YHCT (ComboBox tầng 1 + CBM + KG) – bản web

Chuyển từ `SYM_GUI_CBM_KG.py` (Tkinter) sang Flask. Giữ nguyên tri thức, mạng nơ-ron và cách suy luận; giao diện có 2 tab:
1. **Chẩn đoán & Quản trị Tri thức**: 3 cột (dữ liệu thô ComboBox + ngưỡng, kết quả 3 tầng, bảng triple).
2. **Sơ đồ Đồ thị Tri thức**: bảng quan hệ toàn màn hình.

## Cấu trúc
```
├── app.py            # KG + mạng nơ-ron (numpy/networkx) + API /api/diagnose
├── requirements.txt  ├── Procfile  ├── render.yaml  └── .gitignore
├── templates/index.html
└── static/css/style.css, static/js/app.js
```

## Chạy trên máy
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py          # http://localhost:5000  (macOS bận cổng 5000: PORT=5001 python app.py)
```

## GitHub + Render
```bash
git init && git add . && git commit -m "He thong chan doan YHCT" && git branch -M main
git remote add origin https://github.com/<tai-khoan>/<ten-repo>.git && git push -u origin main
```
Render: **New → Web Service** → chọn repo; Build: `pip install -r requirements.txt`; Start: `gunicorn app:app --timeout 60`; gói Free (hoặc **New → Blueprint** dùng `render.yaml`). Render không đọc `Procfile`.

## Thêm/sửa tri thức
Sửa danh sách `tri_thuc` trong `app.py` (nguồn, quan hệ, đích); các ô ComboBox và 2 bảng tự cập nhật theo.
