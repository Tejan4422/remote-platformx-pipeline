import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
from typing import Tuple, Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

class SimpleRequirementClassifier:
    """
    Simple requirement classifier using TF-IDF features with traditional ML classifiers
    """
    
    def __init__(self, max_features: int = 5000):
        """
        Initialize the classifier with TF-IDF vectorizer
        
        Args:
            max_features: Maximum number of features for TF-IDF
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents='ascii'
        )
        self.label_encoder = LabelEncoder()
        self.rf_classifier = None
        self.svm_classifier = None
        self.lr_classifier = None
        self.best_classifier = None
        self.best_classifier_name = None
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load requirement data from CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            DataFrame with requirements and labels
        """
        try:
            df = pd.read_csv(file_path)
            print(f"Data loaded successfully: {df.shape[0]} samples, {df.shape[1]} columns")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Label distribution:\n{df.iloc[:, 1].value_counts()}")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess the data by generating TF-IDF features and encoding labels
        
        Args:
            df: DataFrame with requirements and labels
            
        Returns:
            Tuple of (features, encoded_labels)
        """
        # Assume first column is requirements, second column is labels
        requirements = df.iloc[:, 0].tolist()
        labels = df.iloc[:, 1].tolist()
        
        print("Generating TF-IDF features...")
        features = self.vectorizer.fit_transform(requirements)
        
        print("Encoding labels...")
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        print(f"Features shape: {features.shape}")
        print(f"Unique labels: {self.label_encoder.classes_}")
        
        return features, encoded_labels
    
    def train_models(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, 
                    random_state: int = 42) -> Dict[str, Any]:
        """
        Train multiple classifiers and compare their performance
        
        Args:
            X: Feature matrix
            y: Encoded labels
            test_size: Fraction of data to use for testing
            random_state: Random state for reproducibility
            
        Returns:
            Dictionary with model performance metrics
        """
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"Training set size: {X_train.shape[0]}")
        print(f"Test set size: {X_test.shape[0]}")
        
        # Define classifiers
        classifiers = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=random_state),
            'SVM': SVC(kernel='rbf', random_state=random_state, probability=True),
            'Logistic Regression': LogisticRegression(random_state=random_state, max_iter=1000)
        }
        
        results = {}
        best_score = 0
        
        for name, classifier in classifiers.items():
            print(f"\nTraining {name}...")
            
            # Train the model
            classifier.fit(X_train, y_train)
            
            # Predictions
            y_pred = classifier.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation score
            cv_scores = cross_val_score(classifier, X_train, y_train, cv=5)
            
            results[name] = {
                'model': classifier,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'classification_report': classification_report(y_test, y_pred, 
                                                             target_names=self.label_encoder.classes_),
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'predictions': y_pred,
                'y_test': y_test
            }
            
            print(f"{name} - Accuracy: {accuracy:.4f}, CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            # Track best model
            if accuracy > best_score:
                best_score = accuracy
                self.best_classifier = classifier
                self.best_classifier_name = name
        
        # Store the best performing models
        self.rf_classifier = results['Random Forest']['model']
        self.svm_classifier = results['SVM']['model']
        self.lr_classifier = results['Logistic Regression']['model']
        
        print(f"\nBest performing model: {self.best_classifier_name} with accuracy: {best_score:.4f}")
        
        return results
    
    def predict(self, requirements: List[str]) -> List[str]:
        """
        Predict labels for new requirements
        
        Args:
            requirements: List of requirement texts
            
        Returns:
            List of predicted labels
        """
        if self.best_classifier is None:
            raise ValueError("Model not trained yet. Please train the model first.")
        
        # Generate features for new requirements
        features = self.vectorizer.transform(requirements)
        
        # Predict using the best classifier
        predictions = self.best_classifier.predict(features)
        
        # Decode labels
        predicted_labels = self.label_encoder.inverse_transform(predictions)
        
        return predicted_labels.tolist()
    
    def predict_proba(self, requirements: List[str]) -> np.ndarray:
        """
        Get prediction probabilities for new requirements
        
        Args:
            requirements: List of requirement texts
            
        Returns:
            Array of prediction probabilities
        """
        if self.best_classifier is None:
            raise ValueError("Model not trained yet. Please train the model first.")
        
        features = self.vectorizer.transform(requirements)
        probabilities = self.best_classifier.predict_proba(features)
        
        return probabilities
    
    def save_model(self, save_dir: str):
        """
        Save the trained model and components
        
        Args:
            save_dir: Directory to save the model files
        """
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the vectorizer
        joblib.dump(self.vectorizer, os.path.join(save_dir, 'vectorizer.pkl'))
        
        # Save the best classifier
        joblib.dump(self.best_classifier, os.path.join(save_dir, 'best_classifier.pkl'))
        
        # Save all classifiers
        joblib.dump(self.rf_classifier, os.path.join(save_dir, 'random_forest.pkl'))
        joblib.dump(self.svm_classifier, os.path.join(save_dir, 'svm.pkl'))
        joblib.dump(self.lr_classifier, os.path.join(save_dir, 'logistic_regression.pkl'))
        
        # Save label encoder
        joblib.dump(self.label_encoder, os.path.join(save_dir, 'label_encoder.pkl'))
        
        # Save model metadata
        metadata = {
            'best_classifier_name': self.best_classifier_name,
            'label_classes': self.label_encoder.classes_.tolist(),
            'vectorizer_features': self.vectorizer.max_features
        }
        
        joblib.dump(metadata, os.path.join(save_dir, 'metadata.pkl'))
        
        print(f"Model saved to {save_dir}")
    
    def load_model(self, save_dir: str):
        """
        Load a previously trained model
        
        Args:
            save_dir: Directory containing the saved model files
        """
        # Load metadata
        metadata = joblib.load(os.path.join(save_dir, 'metadata.pkl'))
        
        # Load vectorizer
        self.vectorizer = joblib.load(os.path.join(save_dir, 'vectorizer.pkl'))
        
        # Load label encoder
        self.label_encoder = joblib.load(os.path.join(save_dir, 'label_encoder.pkl'))
        
        # Load classifiers
        self.best_classifier = joblib.load(os.path.join(save_dir, 'best_classifier.pkl'))
        self.rf_classifier = joblib.load(os.path.join(save_dir, 'random_forest.pkl'))
        self.svm_classifier = joblib.load(os.path.join(save_dir, 'svm.pkl'))
        self.lr_classifier = joblib.load(os.path.join(save_dir, 'logistic_regression.pkl'))
        
        self.best_classifier_name = metadata['best_classifier_name']
        
        print(f"Model loaded from {save_dir}")
        print(f"Best classifier: {self.best_classifier_name}")
        print(f"Available classes: {self.label_encoder.classes_}")


# For backward compatibility, create an alias
RequirementClassifier = SimpleRequirementClassifier