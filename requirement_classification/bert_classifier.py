#!/usr/bin/env python3
"""
BERT-based requirement classifier (requires more dependencies)
This is the advanced version with sentence-transformers
"""

# This import will only work if sentence-transformers is properly installed
try:
    from sentence_transformers import SentenceTransformer
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
    print("Warning: sentence-transformers not available. Use simple_classifier.py instead.")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from typing import Tuple, Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

class BertRequirementClassifier:
    """
    Advanced requirement classifier using BERT embeddings
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        if not BERT_AVAILABLE:
            raise ImportError("sentence-transformers not available. Install with: pip install sentence-transformers")
        
        self.model_name = model_name
        self.sentence_model = SentenceTransformer(model_name)
        self.label_encoder = LabelEncoder()
        self.rf_classifier = None
        self.svm_classifier = None
        self.lr_classifier = None
        self.best_classifier = None
        self.best_classifier_name = None
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load requirement data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            print(f"Data loaded successfully: {df.shape[0]} samples, {df.shape[1]} columns")
            print(f"Label distribution:\n{df.iloc[:, 1].value_counts()}")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Generate BERT embeddings and encode labels"""
        requirements = df.iloc[:, 0].tolist()
        labels = df.iloc[:, 1].tolist()
        
        print("Generating BERT embeddings...")
        embeddings = self.sentence_model.encode(requirements, show_progress_bar=True)
        
        print("Encoding labels...")
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        print(f"Embeddings shape: {embeddings.shape}")
        print(f"Unique labels: {self.label_encoder.classes_}")
        
        return embeddings, encoded_labels
    
    def train_models(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, 
                    random_state: int = 42) -> Dict[str, Any]:
        """Train multiple classifiers and compare performance"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"Training set size: {X_train.shape[0]}")
        print(f"Test set size: {X_test.shape[0]}")
        
        classifiers = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=random_state),
            'SVM': SVC(kernel='rbf', random_state=random_state, probability=True),
            'Logistic Regression': LogisticRegression(random_state=random_state, max_iter=1000)
        }
        
        results = {}
        best_score = 0
        
        for name, classifier in classifiers.items():
            print(f"\nTraining {name}...")
            classifier.fit(X_train, y_train)
            y_pred = classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            cv_scores = cross_val_score(classifier, X_train, y_train, cv=5)
            
            results[name] = {
                'model': classifier,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'classification_report': classification_report(y_test, y_pred, 
                                                             target_names=self.label_encoder.classes_),
                'confusion_matrix': confusion_matrix(y_test, y_pred)
            }
            
            print(f"{name} - Accuracy: {accuracy:.4f}, CV Score: {cv_scores.mean():.4f}")
            
            if accuracy > best_score:
                best_score = accuracy
                self.best_classifier = classifier
                self.best_classifier_name = name
        
        self.rf_classifier = results['Random Forest']['model']
        self.svm_classifier = results['SVM']['model']
        self.lr_classifier = results['Logistic Regression']['model']
        
        print(f"\nBest performing model: {self.best_classifier_name} with accuracy: {best_score:.4f}")
        return results
    
    def predict(self, requirements: List[str]) -> List[str]:
        """Predict labels for new requirements"""
        if self.best_classifier is None:
            raise ValueError("Model not trained yet.")
        
        embeddings = self.sentence_model.encode(requirements)
        predictions = self.best_classifier.predict(embeddings)
        return self.label_encoder.inverse_transform(predictions).tolist()
    
    def predict_proba(self, requirements: List[str]) -> np.ndarray:
        """Get prediction probabilities"""
        if self.best_classifier is None:
            raise ValueError("Model not trained yet.")
        
        embeddings = self.sentence_model.encode(requirements)
        return self.best_classifier.predict_proba(embeddings)
    
    def save_model(self, save_dir: str):
        """Save the trained model"""
        os.makedirs(save_dir, exist_ok=True)
        
        joblib.dump(self.best_classifier, os.path.join(save_dir, 'best_classifier.pkl'))
        joblib.dump(self.label_encoder, os.path.join(save_dir, 'label_encoder.pkl'))
        
        metadata = {
            'sentence_model_name': self.model_name,
            'best_classifier_name': self.best_classifier_name,
            'label_classes': self.label_encoder.classes_.tolist()
        }
        joblib.dump(metadata, os.path.join(save_dir, 'metadata.pkl'))
        print(f"Model saved to {save_dir}")
    
    def load_model(self, save_dir: str):
        """Load a previously trained model"""
        metadata = joblib.load(os.path.join(save_dir, 'metadata.pkl'))
        
        self.model_name = metadata['sentence_model_name']
        self.sentence_model = SentenceTransformer(self.model_name)
        self.label_encoder = joblib.load(os.path.join(save_dir, 'label_encoder.pkl'))
        self.best_classifier = joblib.load(os.path.join(save_dir, 'best_classifier.pkl'))
        self.best_classifier_name = metadata['best_classifier_name']
        
        print(f"Model loaded from {save_dir}")
        print(f"Best classifier: {self.best_classifier_name}")


# Demo function for BERT classifier
def bert_demo():
    if not BERT_AVAILABLE:
        print("BERT demo requires sentence-transformers to be installed.")
        print("Install with: pip install sentence-transformers")
        return
    
    print("=== BERT Requirement Classification Demo ===")
    print("Using Sentence-BERT embeddings + ML classifiers")
    print("=" * 60)
    
    DATA_FILE = "data/sample_requirements.csv"
    MODEL_DIR = "models/bert_demo_model"
    
    classifier = BertRequirementClassifier()
    
    print("1. Loading data...")
    df = classifier.load_data(DATA_FILE)
    
    print("2. Generating BERT embeddings...")
    X, y = classifier.preprocess_data(df)
    
    print("3. Training models...")
    results = classifier.train_models(X, y)
    
    print("\nResults:")
    for name, result in results.items():
        print(f"{name}: {result['accuracy']:.3f}")
    
    classifier.save_model(MODEL_DIR)
    
    # Test predictions
    test_requirements = [
        "Implement data privacy compliance",
        "Build recommendation engine",
        "Create performance dashboard"
    ]
    
    predictions = classifier.predict(test_requirements)
    probabilities = classifier.predict_proba(test_requirements)
    
    print("\nPredictions:")
    for req, pred, prob in zip(test_requirements, predictions, probabilities):
        print(f"{req} → {pred} ({max(prob):.3f})")

if __name__ == "__main__":
    bert_demo()