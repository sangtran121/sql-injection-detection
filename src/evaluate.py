from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from preprocess import load_and_preprocess

def evaluate_model(model_name='best'):
    X_train, X_test, y_train, y_test, _, _ = load_and_preprocess()
    
    if model_name.lower() == 'xgboost':
        model = joblib.load('models/xgboost_model.pkl')  # Chúng ta sẽ lưu riêng
        title = "XGBoost"
    else:
        model = joblib.load('models/sql_injection_best_model.pkl')
        title = "Random Forest (Best Model)"
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    
    print("="*70)
    print(f"📊 ĐÁNH GIÁ MÔ HÌNH: {title}")
    print("="*70)
    print(f"Accuracy : {acc:.4f}")
    print(f"AUC      : {auc:.4f}\n")
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=['Normal SQL', 'SQL Injection']))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Normal', 'Injection'],
                yticklabels=['Normal', 'Injection'])
    plt.title(f'Confusion Matrix - {title}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.show()

if __name__ == "__main__":
    evaluate_model('xgboost')   # Evaluate XGBoost
    # evaluate_model('best')    # Uncomment để evaluate Random Forest