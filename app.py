from flask import Flask, render_template, request
import sys
import os
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.append(str(root_dir / "src"))

from preprocess import clean_sql, extract_sql_features
import joblib

app = Flask(__name__)

# Load model tốt nhất
model = joblib.load("models/sql_injection_best_model.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

def hybrid_predict(query):
    cleaned = clean_sql(query)
    features = extract_sql_features(query)
    X_new = vectorizer.transform([cleaned])
    
    ml_prob = model.predict_proba(X_new)[0][1]
    
    # Rule Engine (tương tự v12)
    rule_score = 0.0
    if features['has_single_quote'] >= 1 and features['has_or'] == 1:
        rule_score += 0.98
    if features['has_dash_comment'] == 1 and features['has_single_quote'] >= 1:
        rule_score += 0.92
    if features['has_union'] == 1 and features['has_select'] == 1:
        rule_score += 0.95
    if features['has_sleep'] == 1 or features['has_drop'] == 1 or features['has_exec'] == 1:
        rule_score += 0.95
    
    # Bảo vệ câu SELECT bình thường
    if ("select" in cleaned and "from" in cleaned and 
        features['has_or'] == 0 and features['has_union'] == 0 and 
        features['has_single_quote'] == 0):
        rule_score = min(rule_score, 0.08)
    
    final_prob = (ml_prob * 0.60) + (rule_score * 0.40)
    final_prob = min(final_prob, 0.98)
    
    is_injection = final_prob >= 0.60
    risk = "HIGH" if final_prob > 0.78 else "MEDIUM" if final_prob > 0.60 else "LOW"
    status = "🚨 SQL INJECTION" if is_injection else "✅ NORMAL"
    
    return {
        "query": query,
        "probability": round(final_prob * 100, 2),
        "risk": risk,
        "status": status
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            result = hybrid_predict(query)
    
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)