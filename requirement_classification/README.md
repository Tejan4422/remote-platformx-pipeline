# Requirement Classification System

A hybrid classification system for automatically categorizing software requirements using machine learning.

## Features

- **TF-IDF Features**: Fast and reliable text classification
- **Multiple Classifiers**: Compares Random Forest, SVM, and Logistic Regression
- **Interactive Training**: Easy-to-use training interface
- **Batch Prediction**: Process multiple requirements at once
- **Model Persistence**: Save and load trained models

## Categories

The system classifies requirements into these categories:
- **Compliance**: Regulatory, legal, and compliance requirements
- **Functional**: Core business functionality requirements  
- **Business Intelligence**: Analytics, reporting, and dashboard requirements
- **AI/ML**: Machine learning and artificial intelligence requirements
- **Non functional**: Performance, scalability, and technical requirements

## Quick Start

### 1. Installation

```bash
cd requirement_classification
pip install -r requirements.txt
```

### 2. Prepare Your Data

Create a CSV file with the following format:
```csv
requirement,label
"Implement consent management for customer data processing.",Compliance
"Support approval workflows for large loan applications.",Functional
"Ensure low latency for dashboard load times.",Non functional
...
```

### 3. Run the System

```bash
python train_and_predict.py
```

The system will:
- Ask for your CSV file path (or use sample data)
- Train multiple models and select the best one
- Allow interactive testing of predictions
- Save the trained model for future use

## File Structure

```
requirement_classification/
├── data/
│   └── sample_requirements.csv     # Sample dataset (30 examples)
├── models/
│   └── tfidf_model/               # Trained model files
├── train_and_predict.py           # Main script for training and prediction
├── simple_classifier.py           # Core TF-IDF classifier
├── bert_classifier.py             # Advanced BERT classifier (optional)
├── requirements.txt               # Dependencies
├── QUICK_START.md                 # Quick usage guide
└── README.md                      # This file
```

## Usage Examples

### Training on Your Data
```python
from simple_classifier import SimpleRequirementClassifier

# Load your data
classifier = SimpleRequirementClassifier()
df = classifier.load_data("data/your_dataset.csv")
X, y = classifier.preprocess_data(df)

# Train and evaluate
results = classifier.train_models(X, y)
classifier.save_model("models/my_model")
```

### Making Predictions
```python
# Load trained model
classifier = SimpleRequirementClassifier()
classifier.load_model("models/tfidf_model")

# Predict new requirements
new_requirements = [
    "Implement data encryption for customer records",
    "Create real-time fraud detection system",
    "Build executive dashboard for KPIs"
]

predictions = classifier.predict(new_requirements)
probabilities = classifier.predict_proba(new_requirements)

for req, pred, prob in zip(new_requirements, predictions, probabilities):
    confidence = max(prob)
    print(f"'{req}' → {pred} (confidence: {confidence:.3f})")
```

## Performance Tips

1. **For best results**: Use your full 2000+ requirement dataset
2. **For quick testing**: Use the provided sample data
3. **For production**: Train once with full data, then use saved model
4. **For higher accuracy**: Consider the BERT approach (bert_classifier.py)

## Expected Results

With your 2000+ requirement dataset, you can expect:
- **TF-IDF Approach**: 75-85% accuracy
- **BERT Approach**: 85-95% accuracy (requires additional setup)

The small sample (30 examples) shows lower accuracy due to limited training data.

## Next Steps

1. **Replace sample data** with your 2000+ requirements CSV
2. **Run `python train_and_predict.py`** to train on your full dataset
3. **Test predictions** interactively
4. **Use the saved model** for production predictions