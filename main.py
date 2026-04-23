from src.predict import hybrid_predict

if __name__ == "__main__":
    print("🔍 SQL Injection Detection System (Hybrid Model)\n")
    
    while True:
        query = input("Nhập câu truy vấn SQL (hoặc 'exit' để thoát): ")
        if query.lower() in ['exit', 'quit', 'thoát']:
            print("Tạm biệt!")
            break
        if query.strip():
            result = hybrid_predict(query)
            if result:
                print(f"\nKết quả: {result['risk_level']} Risk")
                print(f"Xác suất: {result['probability']*100:.2f}%\n")