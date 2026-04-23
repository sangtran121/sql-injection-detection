from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib
from preprocess import load_and_preprocess
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import pandas as pd

def train_and_compare_models():
    print("🔄 Đang tải và xử lý dữ liệu...")
    X_train, X_test, y_train, y_test, vectorizer, _ = load_and_preprocess()
    
    models = {
        "1. Logistic Regression": LogisticRegression(max_iter=1000, 
                                                    class_weight='balanced', 
                                                    n_jobs=-1, 
                                                    random_state=42),
        
        "2. Random Forest": RandomForestClassifier(n_estimators=300, 
                                                  class_weight='balanced', 
                                                  n_jobs=-1, 
                                                  random_state=42),
        
        "3. XGBoost": xgb.XGBClassifier(n_estimators=300, 
                                       learning_rate=0.1, 
                                       max_depth=6,
                                       eval_metric='auc',
                                       random_state=42,
                                       n_jobs=-1,
                                       use_label_encoder=False)
    }
    
    results = []
    
    print("\n" + "="*70)
    print("🚀 BẮT ĐẦU HUẤN LUYỆN VÀ SO SÁNH CÁC MÔ HÌNH")
    print("="*70)
    
    for name, model in models.items():
        print(f"\nĐang train {name}...")
        model.fit(X_train, y_train)
        
        # Dự đoán
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Đánh giá
        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        print(f"✅ {name} hoàn thành!")
        print(f"   Accuracy : {acc:.4f}")
        print(f"   AUC      : {auc:.4f}")
        
        results.append({
            'Model': name,
            'Accuracy': acc,
            'AUC': auc,
            'model_obj': model
        })
    
    # Tạo bảng so sánh
    comparison_df = pd.DataFrame(results)
    comparison_df = comparison_df.drop(columns=['model_obj'])
    print("\n" + "="*70)
    print("📊 BẢNG SO SÁNH KẾT QUẢ")
    print("="*70)
    print(comparison_df.round(4))
    
    # Lưu mô hình tốt nhất
    best_model = max(results, key=lambda x: x['Accuracy'])
    joblib.dump(best_model['model_obj'], 'models/sql_injection_best_model.pkl')
    joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
    
    print(f"\n🏆 MÔ HÌNH TỐT NHẤT: {best_model['Model']}")
    print(f"Accuracy: {best_model['Accuracy']:.4f} | AUC: {best_model['AUC']:.4f}")
    
    return comparison_df, best_model['model_obj']

if __name__ == "__main__":
    train_and_compare_models()