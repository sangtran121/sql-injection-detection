import sys
import os
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

import joblib
from preprocess import clean_sql, extract_sql_features

def load_best_model():
    model = joblib.load(root_dir / "models" / "sql_injection_best_model.pkl")
    vectorizer = joblib.load(root_dir / "models" / "tfidf_vectorizer.pkl")
    print("✅ Loaded Random Forest (Best Model)")
    return model, vectorizer


def hybrid_predict(query):
    model, vectorizer = load_best_model()
    cleaned = clean_sql(query)
    features = extract_sql_features(query)
    X_new = vectorizer.transform([cleaned])
    
    ml_prob = model.predict_proba(X_new)[0][1]
    
    # ==================== RULE v12 - CÂN BẰNG TỐT ====================
    rule_score = 0.0
    
    if features['has_single_quote'] >= 1 and features['has_or'] == 1:
        rule_score += 0.95
    if features['has_dash_comment'] == 1 and features['has_single_quote'] >= 1:
        rule_score += 0.90
    if features['has_union'] == 1 and features['has_select'] == 1:
        rule_score += 0.92
    if features['has_sleep'] == 1 or features['has_drop'] == 1 or features['has_exec'] == 1:
        rule_score += 0.90
    
    # Rất quan trọng: Giảm mạnh cho câu SELECT bình thường
    if ("select" in cleaned and "from" in cleaned and 
        features['has_or'] == 0 and features['has_union'] == 0 and 
        features['has_single_quote'] == 0):
        rule_score = min(rule_score, 0.05)
    
    final_prob = (ml_prob * 0.65) + (rule_score * 0.35)
    final_prob = min(final_prob, 0.98)
    
    is_injection = final_prob >= 0.62   # Tăng threshold một chút
    
    risk = "HIGH" if final_prob > 0.80 else "MEDIUM" if final_prob > 0.62 else "LOW"
    status = "🚨 SQL INJECTION" if is_injection else "✅ NORMAL"
    
    print(f"Query : {query}")
    print(f"Cleaned: {cleaned}")
    print(f"ML: {ml_prob*100:5.2f}% | Rule: {rule_score*100:5.1f}% → Final: {final_prob*100:5.2f}%")
    print(f"→ {risk} {status}")
    print("-" * 100)
    
    return {"probability": final_prob, "is_sql_injection": is_injection, "risk_level": risk}


if __name__ == "__main__":
    test_payloads = [
        "SELECT * FROM users WHERE id = 1",
        "1' OR '1'='1",
        "admin'--",
        "admin' OR '1'='1'#",
        "UNION SELECT @@version--",
        "pg_sleep(5)--",
        "1; DROP TABLE users;--",
        "xp_cmdshell('dir')",
        "SELECT * FROM information_schema.tables",
        "SELECT name FROM users WHERE id=100"
    ]
    
    print("🔥 HYBRID MODEL v12 - FINAL BALANCED\n")
    for q in test_payloads:
        hybrid_predict(q)