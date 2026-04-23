# 🛡️ SQL Injection Detection System

> Hệ thống phát hiện SQL Injection bằng **Hybrid Model** — kết hợp Machine Learning (TF-IDF + Classifier) và Rule-Based Engine để đạt độ chính xác cao.

---

## 📌 Tổng quan

Dự án xây dựng một hệ thống phát hiện tấn công SQL Injection theo phương pháp **Hybrid** gồm hai lớp bảo vệ:

1. **Machine Learning Layer** — Dùng TF-IDF vectorizer kết hợp với mô hình phân loại (scikit-learn) được huấn luyện trên tập dữ liệu SQL injection, trả về xác suất tấn công.
2. **Rule-Based Engine** — Bộ luật thủ công kiểm tra các dấu hiệu đặc trưng như `'`, `OR`, `--`, `UNION SELECT`, `SLEEP()`, `DROP`, `EXEC`... để tính thêm điểm rủi ro.

Kết quả cuối cùng là điểm tổng hợp: **60% từ ML + 40% từ Rule Engine**, từ đó phân loại mức độ nguy hiểm: `LOW`, `MEDIUM`, hoặc `HIGH`.

Hệ thống hỗ trợ hai giao diện:
- **Web App** (Flask) — Nhập query qua trình duyệt, nhận kết quả trực quan.
- **CLI** — Chạy terminal, kiểm tra query trực tiếp từ dòng lệnh.

---

## 🏗️ Cấu trúc dự án

```
sql-injection-detection/
├── app.py                  # Flask web application
├── main.py                 # CLI entry point
├── requirements.txt        # Thư viện cần thiết
├── data/                   # Dataset huấn luyện
├── src/
│   ├── preprocess.py       # Tiền xử lý query & trích xuất đặc trưng
│   └── predict.py          # Logic hybrid predict (dùng cho CLI)
├── templates/
│   └── index.html          # Giao diện web Flask
└── models/                 # Model & vectorizer đã được train (*.pkl)
    ├── sql_injection_best_model.pkl
    └── tfidf_vectorizer.pkl
```

---

## ⚙️ Cách hoạt động

### Pipeline phát hiện (Hybrid Predict)

```
Input Query
    │
    ▼
clean_sql()          ← Làm sạch, chuẩn hoá chuỗi SQL
    │
    ├──► TF-IDF Vectorizer  →  ML Model  →  ml_prob (xác suất ML)
    │
    └──► extract_sql_features()  →  Rule Engine  →  rule_score
                │
                ├─ has_single_quote + has_or        → +0.98
                ├─ has_dash_comment + has_single_quote → +0.92
                ├─ has_union + has_select            → +0.95
                └─ has_sleep / has_drop / has_exec   → +0.95
    │
    ▼
final_prob = (ml_prob × 0.60) + (rule_score × 0.40)
    │
    ▼
Phân loại mức độ rủi ro:
    final_prob > 0.78  →  HIGH  🚨
    final_prob > 0.60  →  MEDIUM 🚨
    final_prob ≤ 0.60  →  LOW   ✅
```

> **Bảo vệ false positive**: Câu `SELECT ... FROM ...` thuần tuý (không có OR, UNION, dấu nháy đơn) sẽ bị giới hạn `rule_score ≤ 0.08` để tránh báo nhầm.

---

## 🚀 Cài đặt & Chạy

### 1. Clone repository

```bash
git clone https://github.com/sangtran121/sql-injection-detection.git
cd sql-injection-detection
```

### 2. Cài đặt thư viện

```bash
pip install -r requirements.txt
pip install flask
```

> **Lưu ý:** `flask` chưa có trong `requirements.txt`, cần cài thêm thủ công.

### 3. Chạy Web App (Flask)

```bash
python app.py
```

Truy cập trình duyệt tại: [http://127.0.0.1:5000](http://127.0.0.1:5000)

Nhập câu SQL vào ô input, hệ thống sẽ trả về:
- Xác suất tấn công (%)
- Mức độ rủi ro: `LOW` / `MEDIUM` / `HIGH`
- Trạng thái: `✅ NORMAL` hoặc `🚨 SQL INJECTION`

### 4. Chạy CLI

```bash
python main.py
```

```
🔍 SQL Injection Detection System (Hybrid Model)

Nhập câu truy vấn SQL (hoặc 'exit' để thoát): ' OR 1=1 --
Kết quả: HIGH Risk
Xác suất: 97.20%
```

Gõ `exit`, `quit` hoặc `thoát` để kết thúc.

---

## 📦 Thư viện sử dụng

| Thư viện       | Mục đích                              |
|----------------|---------------------------------------|
| `pandas`       | Xử lý dataset                         |
| `numpy`        | Tính toán số học                      |
| `scikit-learn` | TF-IDF Vectorizer + ML Classifier     |
| `matplotlib`   | Vẽ biểu đồ kết quả huấn luyện        |
| `seaborn`      | Trực quan hoá dữ liệu                 |
| `joblib`       | Lưu/tải model `.pkl`                  |
| `flask`        | Web server (cần cài thêm)             |

---

## 🧪 Ví dụ kiểm thử

| Query                                          | Kết quả dự đoán       |
|-----------------------------------------------|-----------------------|
| `SELECT * FROM users WHERE id = 1`            | ✅ NORMAL — LOW       |
| `' OR 1=1 --`                                 | 🚨 SQL INJECTION — HIGH |
| `1; DROP TABLE users; --`                     | 🚨 SQL INJECTION — HIGH |
| `1 UNION SELECT username, password FROM users`| 🚨 SQL INJECTION — HIGH |
| `SELECT name FROM products WHERE price > 100` | ✅ NORMAL — LOW       |

---

## 📁 Dữ liệu

Dataset được lưu trong thư mục `data/`. Mô hình sau khi train sẽ được lưu dưới dạng file `.pkl` trong thư mục `models/`:
- `sql_injection_best_model.pkl` — mô hình phân loại tốt nhất
- `tfidf_vectorizer.pkl` — bộ vector hoá TF-IDF

---

## 🔒 Lưu ý bảo mật

Đây là dự án **nghiên cứu và học thuật**. Không nên dùng trực tiếp làm hệ thống bảo mật production mà không kết hợp thêm các biện pháp khác như:
- Parameterized queries / Prepared statements
- Web Application Firewall (WAF)
- Input validation phía server

---

## 👤 Tác giả

**sangtran121** — [github.com/sangtran121](https://github.com/sangtran121)
