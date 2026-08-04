import os
import time
import glob
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix)

def setup_environment():
    """Locate dataset files within the Kaggle input directory."""
    print("[*] Setting up environment and locating data files...")
    input_dir = '/kaggle/input/'
    
    # Locate all CSV files inside the Kaggle dataset directory recursively
    csv_files = glob.glob(os.path.join(input_dir, '**/*.csv'), recursive=True)
    if not csv_files:
        print("[!] No CSV files found in /kaggle/input/. Ensure dataset is attached.")
    else:
        print(f"[*] Found {len(csv_files)} CSV files across the dataset.")
    
    return csv_files

def ingest_and_clean_data(csv_files, rows_per_file=40000):
    """Load samples from ALL available CSV files to ensure a mix of benign and malicious traffic."""
    print(f"[*] Ingesting data across all {len(csv_files)} CSV files (~{rows_per_file} rows per file)...")
    
    if not csv_files:
        return pd.DataFrame()
        
    df_list = []
    for target_file in csv_files:
        try:
            print(f"[*] Reading sample from: {os.path.basename(target_file)}")
            # low_memory=False suppresses DtypeWarning
            chunk = pd.read_csv(target_file, nrows=rows_per_file, low_memory=False)
            df_list.append(chunk)
        except Exception as e:
            print(f"[!] Warning - could not read {target_file}: {e}")

    if not df_list:
        return pd.DataFrame()

    df = pd.concat(df_list, ignore_index=True)
    print(f"[*] Total aggregated dataset size: {len(df)} rows.")

    print("[*] Cleaning column names...")
    df.columns = df.columns.str.strip()
    
    # Remove repeated header rows
    target_col_candidates = ['Label', 'label']
    for t_col in target_col_candidates:
        if t_col in df.columns:
            df = df[df[t_col] != t_col]
            df = df[df[t_col] != t_col.capitalize()]

    return df

def preprocess_features(df):
    """Separate features and target, clean numeric values, and eliminate inf/nan values."""
    print("[*] Preprocessing features and target labels...")
    
    target_col = 'Label'
    if target_col not in df.columns:
        if 'label' in df.columns:
            target_col = 'label'
        else:
            print("[!] Target column 'Label' not found.")
            return None, None, None

    print("[*] Mapping labels to Binary (0 = Benign, 1 = Malicious)...")
    df['Binary_Label'] = df[target_col].apply(
        lambda x: 0 if str(x).strip().lower() == 'benign' else 1
    )
    
    y = df['Binary_Label']
    
    print(f"[*] Label distribution in dataset:\n{y.value_counts()}")
    
    # Drop non-numeric network identifiers
    cols_to_drop = [
        target_col, 'Binary_Label', 'Timestamp', 
        'Flow ID', 'Src IP', 'Dst IP', 'Src Port', 'Dst Port'
    ]
    cols_to_drop = [c for c in cols_to_drop if c in df.columns]
    
    X = df.drop(columns=cols_to_drop)
    
    # 1. Convert columns to numeric FIRST (strings like "Infinity" become np.inf)
    X = X.apply(pd.to_numeric, errors='coerce')
    
    # 2. Replace inf / -inf values with NaN
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # 3. Fill NaNs with 0
    X.fillna(0, inplace=True)
    
    # 4. Clip extreme numbers to prevent XGBoost float32 overflow
    X = X.clip(lower=-1e12, upper=1e12)
    
    # Ensure purely numeric feature set
    X = X.select_dtypes(include=[np.number])
    print(f"[*] Final feature matrix shape: {X.shape}")
    
    if X.shape[1] == 0:
        print("[!] Error: No numeric features remaining after preprocessing.")
        return None, None, None
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    return X, y_encoded, le

def train_xgboost(X_train, y_train):
    """Initialize and train the XGBoost model with optimized parameters."""
    print("[*] Initializing XGBoost Classifier...")
    
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        random_state=42,
        tree_method='hist',
        eval_metric='logloss'
    )
    
    print("[*] Training the model...")
    start_time = time.time()
    
    xgb_model.fit(X_train, y_train)
    
    end_time = time.time()
    print(f"[*] Training completed in {end_time - start_time:.2f} seconds.")
    
    return xgb_model

def evaluate_model(model, X_test, y_test):
    """Predict on test set and evaluate performance metrics."""
    print("[*] Evaluating Model Performance...")
    
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    try:
        roc_auc = roc_auc_score(y_test, y_proba)
    except ValueError:
        roc_auc = float('nan')
        
    print("-" * 40)
    print(f"Accuracy  : {acc:.4f}")
    print(f"Precision : {prec:.4f}")
    print(f"Recall    : {rec:.4f}")
    print(f"F1-Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")
    print("-" * 40)
    
    print("[*] Generating Confusion Matrix...")
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Benign (0)', 'Malicious (1)'], 
                yticklabels=['Benign (0)', 'Malicious (1)'])
    plt.title("Confusion Matrix - XGBoost")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    
    os.makedirs('/kaggle/working', exist_ok=True)
    try:
        plt.savefig('/kaggle/working/confusion_matrix.png')
        print("[*] Confusion matrix saved to /kaggle/working/confusion_matrix.png")
    except Exception:
        plt.savefig('confusion_matrix.png')

def evaluate_threat_confidence(confidence_score, threshold=0.90):
    """Gatekeeper function to route threats based on probability confidence."""
    if confidence_score >= threshold:
        status = "CRITICAL THREAT: Automatic Mitigation Triggered"
        action = "BLOCK"
    else:
        status = "POTENTIAL THREAT: Routed for Manual SOC Review"
        action = "REVIEW"
        
    print(f"[-] Threat Confidence: {confidence_score:.2%} -> {status} (Action: {action})")
    return action

def main():
    print("=" * 55)
    print(" CSE-CIC-IDS2018 Anomaly Detection - XGBoost Training ")
    print("=" * 55)
    
    csv_files = setup_environment()
    if not csv_files:
        print("[!] Execution aborted due to missing data.")
        return
        
    df = ingest_and_clean_data(csv_files, rows_per_file=40000)
    if df.empty:
        print("[!] DataFrame is empty. Execution aborted.")
        return
        
    X, y, label_encoder = preprocess_features(df)
    if X is None:
        print("[!] Preprocessing failed. Execution aborted.")
        return
        
    print("[*] Splitting dataset into 80% Train and 20% Test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    print(f"[*] Train set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")
    
    model = train_xgboost(X_train, y_train)
    
    evaluate_model(model, X_test, y_test)
    
    print("\n[*] Demonstrating Confidence Threshold Gatekeeper...")
    evaluate_threat_confidence(confidence_score=0.96)
    evaluate_threat_confidence(confidence_score=0.78)
    
    print("\n[*] Exporting model and encoders...")
    export_path = '/kaggle/working/threathchain_xgboost.joblib'
    export_data = {
        'model': model,
        'label_encoder': label_encoder
    }
    
    try:
        joblib.dump(export_data, export_path)
        print(f"[*] Successfully saved model bundle to {export_path}")
    except Exception as e:
        local_path = 'threathchain_xgboost.joblib'
        joblib.dump(export_data, local_path)
        print(f"[!] Saved locally to {local_path} due to directory error: {e}")
        
    print("[*] Pipeline execution completed successfully.")

if __name__ == "__main__":
    main()