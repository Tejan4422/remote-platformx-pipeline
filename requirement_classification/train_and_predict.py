#!/usr/bin/env python3
"""
Reliable main interface using TF-IDF approach
This version always works without dependency issues
"""

import os
import sys
import pandas as pd
from simple_classifier import SimpleRequirementClassifier

def main():
    print("=== Requirement Classification System ===")
    print("Using TF-IDF features + Traditional ML Classifiers")
    print("(Reliable approach that works without complex dependencies)")
    print("=" * 60)
    
    # Configuration
    DATA_FILE = input("\nEnter path to your CSV file (or press Enter for sample data): ").strip()
    if not DATA_FILE:
        DATA_FILE = "data/sample_requirements.csv"
        print(f"Using sample data: {DATA_FILE}")
    
    if not os.path.exists(DATA_FILE):
        print(f"Error: File '{DATA_FILE}' not found!")
        print("Make sure your CSV file has columns: requirement, label")
        print("Sample format:")
        print("requirement,label")
        print("\"Implement GDPR compliance\",Compliance")
        print("\"Create loan approval system\",Functional")
        return
    
    MODEL_DIR = "models/tfidf_model"
    
    # Initialize classifier
    print("\nInitializing TF-IDF classifier...")
    classifier = SimpleRequirementClassifier(max_features=2000)
    
    # Load and preprocess data
    print(f"\n1. Loading data from {DATA_FILE}...")
    df = classifier.load_data(DATA_FILE)
    if df is None:
        return
    
    print("2. Generating TF-IDF features...")
    X, y = classifier.preprocess_data(df)
    
    # Train models
    print("3. Training and comparing classifiers...")
    results = classifier.train_models(X, y, test_size=0.2)
    
    # Show results
    print("\n" + "=" * 50)
    print("TRAINING RESULTS")
    print("=" * 50)
    for name, result in results.items():
        print(f"{name}:")
        print(f"  Test Accuracy: {result['accuracy']:.4f}")
        print(f"  CV Score: {result['cv_mean']:.4f} (+/- {result['cv_std'] * 2:.4f})")
        print()
    
    print(f"🏆 Best Model: {classifier.best_classifier_name}")
    
    # Save model
    print("4. Saving model...")
    classifier.save_model(MODEL_DIR)
    print(f"✓ Model saved to: {MODEL_DIR}")
    
    # Show detailed classification report for best model
    best_result = results[classifier.best_classifier_name]
    print(f"\nDetailed Performance Report for {classifier.best_classifier_name}:")
    print(best_result['classification_report'])
    
    # Interactive prediction
    print("\n" + "=" * 50)
    print("5. INTERACTIVE PREDICTION MODE")
    print("=" * 50)
    print("Test your trained model with new requirements!")
    
    while True:
        print("\nEnter a requirement to classify (or 'quit' to exit):")
        print("Examples:")
        print("- 'Implement data encryption for user passwords'")
        print("- 'Create real-time performance dashboard'")
        print("- 'Build machine learning model for fraud detection'")
        
        requirement = input("\n> ").strip()
        
        if requirement.lower() in ['quit', 'exit', 'q', '']:
            break
        
        try:
            prediction = classifier.predict([requirement])
            probabilities = classifier.predict_proba([requirement])
            
            print(f"\n📝 Requirement: {requirement}")
            print(f"🎯 Predicted Category: {prediction[0]}")
            
            # Show confidence scores for all categories
            print("\n📊 Confidence Scores:")
            prob_dict = dict(zip(classifier.label_encoder.classes_, probabilities[0]))
            sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
            
            for i, (category, prob) in enumerate(sorted_probs):
                if i == 0:  # Best prediction
                    print(f"  🥇 {category}: {prob:.3f} ⭐")
                else:
                    print(f"     {category}: {prob:.3f}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TRAINING COMPLETED SUCCESSFULLY!")
    print(f"📁 Model saved to: {MODEL_DIR}")
    print("📈 Performance summary:")
    print(f"   Best classifier: {classifier.best_classifier_name}")
    print(f"   Test accuracy: {results[classifier.best_classifier_name]['accuracy']:.3f}")
    print("💡 Next steps:")
    print("   1. Use your full 2000+ requirements dataset for better accuracy")
    print("   2. Run this script again with your complete data")
    print("   3. Use the saved model for production predictions")
    print("=" * 60)

def batch_predict_demo():
    """Demo function for batch predictions"""
    MODEL_DIR = "models/tfidf_model"
    
    if not os.path.exists(MODEL_DIR):
        print("❌ No trained model found. Please run training first.")
        return
    
    print("=== Batch Prediction Demo ===")
    
    # Load model
    classifier = SimpleRequirementClassifier()
    classifier.load_model(MODEL_DIR)
    
    # Sample requirements for batch prediction
    test_requirements = [
        "Implement GDPR compliance for customer data processing",
        "Create automated loan approval workflow system", 
        "Build predictive analytics model for customer churn",
        "Ensure system response time under 2 seconds",
        "Generate executive dashboard for monthly KPIs",
        "Integrate with external credit scoring APIs",
        "Implement role-based access control system",
        "Create machine learning fraud detection engine",
        "Build real-time reporting dashboard",
        "Ensure 99.9% system availability"
    ]
    
    print(f"Classifying {len(test_requirements)} requirements...")
    
    predictions = classifier.predict(test_requirements)
    probabilities = classifier.predict_proba(test_requirements)
    
    print("\n" + "=" * 80)
    print("BATCH PREDICTION RESULTS")
    print("=" * 80)
    
    for i, (req, pred, prob) in enumerate(zip(test_requirements, predictions, probabilities), 1):
        confidence = max(prob)
        print(f"{i:2d}. {req}")
        print(f"    → {pred} (confidence: {confidence:.3f})")
        print()
    
    # Save results
    results_df = pd.DataFrame({
        'requirement': test_requirements,
        'predicted_category': predictions,
        'confidence': [max(prob) for prob in probabilities]
    })
    
    output_file = "batch_predictions.csv"
    results_df.to_csv(output_file, index=False)
    print(f"💾 Results saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        batch_predict_demo()
    else:
        main()