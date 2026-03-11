import joblib
import os
from dotenv import load_dotenv

load_dotenv()

class MLLayer:
    def __init__(self):
        # Model paths from .env
        self.svm_path = os.getenv("MODEL_SVM_PATH", "models/linear_svm.pkl")
        self.nb_path = os.getenv("MODEL_NB_PATH", "models/naive_bayes.pkl")
        self.lr_path = os.getenv("MODEL_LR_PATH", "models/logistic_regression.pkl")
        self.tfidf_path = os.getenv("TFIDF_PATH", "models/tfidf_vectorizer_v2.pkl")
        
        # Load models and vectorizer
        try:
            self.svm_model = self._load_model(self.svm_path)
            self.nb_model = self._load_model(self.nb_path)
            self.lr_model = self._load_model(self.lr_path)
            self.tfidf = self._load_model(self.tfidf_path)
            print(f"DEBUG: All models and vectorizer loaded successfully.")
        except Exception as e:
            print(f"Error loading models/vectorizer: {e}")
            self.svm_model = None
            self.nb_model = None
            self.lr_model = None
            self.tfidf = None

    def _resolve_path(self, path):
        """Resolves path relative to project root or backend folder."""
        for p in [path, os.path.join("backend", path)]:
            if os.path.exists(p):
                return p
        return path

    def _load_model(self, path):
        resolved = self._resolve_path(path)
        if os.path.exists(resolved):
            return joblib.load(resolved)
        return None

    def predict(self, text: str):
        if not self.tfidf:
            return 0.5, {}
            
        vectorized_text = self.tfidf.transform([text])
        
        # Breakdown for transparency
        breakdown = {}
        weighted_scores = []
        
        # 1. Linear SVM (Weight: 20% -> 0.20)
        if self.svm_model:
            try:
                prob = float(self.svm_model.predict_proba(vectorized_text)[0][1]) if hasattr(self.svm_model, 'predict_proba') else float(self.svm_model.predict(vectorized_text)[0])
                breakdown["Linear SVM (Best)"] = {"prob": prob, "weight": 0.20, "contribution": prob * 0.20}
                weighted_scores.append(prob * 0.20)
            except Exception as e:
                print(f"SVM Predict Error: {e}")
                weighted_scores.append(0.5 * 0.20)

        # 2. Naive Bayes (Weight: 15% -> 0.15)
        if self.nb_model:
            try:
                prob = float(self.nb_model.predict_proba(vectorized_text)[0][1])
                breakdown["Naive Bayes"] = {"prob": prob, "weight": 0.15, "contribution": prob * 0.15}
                weighted_scores.append(prob * 0.15)
            except Exception as e:
                print(f"NB Predict Error: {e}")
                weighted_scores.append(0.5 * 0.15)

        # 3. Logistic Regression (Weight: 15% -> 0.15)
        if self.lr_model:
            try:
                prob = float(self.lr_model.predict_proba(vectorized_text)[0][1])
                breakdown["Logistic Regression"] = {"prob": prob, "weight": 0.15, "contribution": prob * 0.15}
                weighted_scores.append(prob * 0.15)
            except Exception as e:
                print(f"LR Predict Error: {e}")
                weighted_scores.append(0.5 * 0.15)

        ml_total = sum(weighted_scores)
        return ml_total, breakdown
