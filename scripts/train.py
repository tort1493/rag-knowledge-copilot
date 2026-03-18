from pathlib import Path
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

OUT = Path("artifacts")
OUT.mkdir(exist_ok=True)

def main():
    # TODO: replace with real data loading
    X = np.random.rand(500, 10)
    y = (X.mean(axis=1) > 0.5).astype(int)

    clf = LogisticRegression(max_iter=200)
    clf.fit(X, y)

    joblib.dump(clf, OUT / "model.joblib")
    print("Saved:", OUT / "model.joblib")

if __name__ == "__main__":
    main()
