import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

def clean_sql(query):
    """Làm sạch nhẹ nhàng hơn để giữ pattern SQL Injection"""
    if not isinstance(query, str):
        query = str(query)
    
    query = query.lower()
    # Giữ lại các pattern quan trọng
    query = re.sub(r'/\*.*?\*/', ' ', query, flags=re.DOTALL)  # comment
    query = re.sub(r'--.*', ' ', query)
    query = re.sub(r'#.*', ' ', query)
    query = re.sub(r'\s+', ' ', query)
    return query.strip()


def extract_sql_features(query):
    """Tạo thêm đặc trưng thủ công"""
    features = {}
    q = str(query).lower()
    
    features['has_single_quote'] = q.count("'")
    features['has_double_quote'] = q.count('"')
    features['has_dash_comment'] = 1 if '--' in q else 0
    features['has_union'] = 1 if 'union' in q else 0
    features['has_select'] = 1 if 'select' in q else 0
    features['has_or'] = 1 if ' or ' in q or ' or"' in q or "or'" in q else 0
    features['has_sleep'] = 1 if 'sleep' in q or 'pg_sleep' in q else 0
    features['has_drop'] = 1 if 'drop' in q else 0
    features['has_exec'] = 1 if 'exec' in q or 'xp_cmdshell' in q else 0
    features['query_length'] = len(q)
    features['special_char_count'] = sum(1 for c in q if not c.isalnum() and c not in ' ')
    
    return features


def load_and_preprocess(data_path='data/Modified_SQL_Dataset.csv'):
    df = pd.read_csv(data_path)
    df['clean_query'] = df['Query'].apply(clean_sql)
    
    # Vectorizer với parameter tốt hơn
    vectorizer = TfidfVectorizer(
        max_features=8000,          # tăng lên
        ngram_range=(1, 4),         # tăng n-gram
        min_df=2,
        max_df=0.95,
        stop_words=None             # không xóa stopword vì SQL không có stopword thông thường
    )
    
    X_tfidf = vectorizer.fit_transform(df['clean_query'])
    y = df['Label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, y, test_size=0.2, random_state=42, stratify=y
    )
    
    return X_train, X_test, y_train, y_test, vectorizer, df


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, vec, df = load_and_preprocess()
    print(f"Dataset: {df.shape}")
    print(f"Train shape: {X_train.shape}")