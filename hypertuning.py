import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split,RandomizedSearchCV
from xgboost import XGBClassifier
from sklearn.metrics import precision_score
from feature_extractor import extract_features

def best_mod():

    file_path = 'data/processed_dataset.csv'

    df = pd.read_csv(file_path)
    df['label'] = df['label'].astype(int)

    if len(df) > 50000:
        print(f"Data is huge ({len(df)} rows). Sampling 50,000 for tuning...")
        df = df.sample(n=50000, random_state=42)

    print(f'Extracting features form {len(df)} URLs ...')
    X = np.array(df["url"].apply(extract_features).tolist())
    y = df['label'].values

    rf_param = {
        'n_estimators' : [100,200,250,300,400],
        'max_depth' : [5,10,15,20,None],
        'min_samples_split' : [2,5,10,15],
        'min_samples_leaf': [1, 2, 4],
        'bootstrap': [True, False],      
        'class_weight': ['balanced', None]
    }

    xg_param = {
        'learning_rate' : [0.01,0.1,0.2],
        'max_depth' : [3,5,10],
        'subsample' : [0.6,0.8,1.0],
        'min_child_weight': [1, 3, 5],    
        'gamma': [0, 0.1, 0.2],
        'colsample_bytree': [0.7, 0.8, 1.0],
        'scale_pos_weight': [1, 5]
    }

    X_train, X_test,y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)

    rf_search = RandomizedSearchCV(
        RandomForestClassifier(),
        param_distributions=rf_param,
        n_iter=10,
        cv=3,
        n_jobs=-1,
        random_state=42
    )

    rf_search.fit(X_train,y_train)

    y_pred = rf_search.predict(X_test)

    xg_search = RandomizedSearchCV(
        XGBClassifier(),
        param_distributions=xg_param,
        n_iter=10,
        n_jobs=-1,
        cv=3,
        random_state=42
    )

    xg_search.fit(X_train, y_train)

    y_pred2 = xg_search.predict(X_test)

    print(f"Precision of RAMDOMFOREST {precision_score(y_test, y_pred)}")
    print(f"Precision of XGBOOST is {precision_score(y_test, y_pred2)}")

    print("Best RF Params:", rf_search.best_params_)
    print("Best XGB Params:", xg_search.best_params_)

if __name__=='__main__':
    best_mod()