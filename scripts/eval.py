from pathlib import Path
import joblib
import numpy as np
from sklearn.metrics import roc_auc_score

def main():
    model_path = Path("artifacts/model.joblib")
    if not model_path.exists():
        raise SystemExit("Model not found. Run: make train")

    clf = joblib.load(model_path)

    X = np.random.rand(200, 10)
    y = (X.mean(axis=1) > 0.5).astype(int)

    p = clf.predict_proba(X)[:, 1]
    auc = roc_auc_score(y, p)
    print("AUC:", round(float(auc), 4))

if __name__ == "__main__":
    main()
