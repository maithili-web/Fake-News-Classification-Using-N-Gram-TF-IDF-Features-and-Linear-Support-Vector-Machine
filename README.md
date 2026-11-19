# Fake News Detection Using Machine Learning

### TF-IDF + Linear Support Vector Machine (SVM)

A machine learning-powered web application designed to classify news headlines as **Real or Fake** using Natural Language Processing (NLP), TF-IDF feature extraction, and a Linear Support Vector Machine classifier.

The project uses the **Indian Fake News Dataset (IFND)** and provides an interactive dashboard, prediction analysis, batch classification, and prediction history.

## Project Overview

Fake news and misinformation are major challenges in today's digital world. This project implements a supervised machine learning approach to analyze textual patterns in news headlines and classify them into Real and Fake categories.

The application integrates machine learning with a FastAPI backend and a responsive web interface.

**Core Technologies:**

- Python
- Natural Language Processing (NLP)
- TF-IDF Vectorization
- Linear Support Vector Machine (SVM)
- Scikit-learn
- NLTK WordNet Lemmatization
- FastAPI
- SQLite
- HTML, CSS, and JavaScript

## Key Features

- **Fake News Classification:** Predict whether a headline resembles Real or Fake news in the training dataset.
- **Linear SVM Classifier:** Uses a trained Support Vector Machine model for text classification.
- **TF-IDF Feature Extraction:** Converts text into numerical feature vectors.
- **Text Preprocessing:** Includes text normalization, tokenization, and lemmatization.
- **Single Headline Prediction:** Analyze individual headlines.
- **Batch Classification:** Process up to 200 headlines in one request.
- **Decision Margin Analysis:** Display the SVM classification margin.
- **Feature Contribution Analysis:** Identify influential terms in predictions.
- **Prediction History:** Store and retrieve previous predictions using SQLite.
- **Random Test Samples:** Retrieve unseen test headlines for evaluation.
- **Model Performance Report:** View evaluation metrics and confusion matrix data.
- **Interactive Web Dashboard:** User-friendly frontend for headline analysis.
- **REST API:** FastAPI endpoints for external integration.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Machine Learning | Scikit-learn |
| Classification Algorithm | Linear SVM |
| Feature Extraction | TF-IDF |
| NLP Library | NLTK |
| Text Processing | WordNet Lemmatizer |
| Data Analysis | Pandas, NumPy |
| Model Serialization | Joblib |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Web Server | Uvicorn |
| API Testing | Pytest, HTTPX |

## Project Structure

The following is a proposed cleaned repository structure:

```text
fake-news-detection/
│
├── dataset/
│   └── IFND.csv
│
├── notebooks/
│   └── TFIDF_LinearSVM.ipynb
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── model.py
│   └── database.py
│
├── static/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── models/
│   └── tfidf_svm.joblib
│
├── data/
│   ├── history.db
│   ├── test_headlines.csv
│   ├── model_metrics.json
│   └── test_predictions.csv
│
├── tests/
│   └── test_api.py
│
├── requirements.txt
├── run.py
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/fake-news-detection.git
cd fake-news-detection
```

### 2. Create a Virtual Environment

Python 3.10 or newer is required.

```bash
python -m venv venv
```

Activate on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Application

```bash
python run.py
```

The application automatically opens in your browser.

### 5. Access the Dashboard

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

**Note:** Internet access is required during the first startup to download the NLTK WordNet resources used for lemmatization.

## Machine Learning Methodology

The project implements a supervised text classification pipeline.

```text
        News Headline
              |
              v
       Text Normalization
              |
              v
     Tokenization & Lemmatization
              |
              v
       TF-IDF Vectorization
              |
              v
        Linear SVM Model
              |
              v
       Decision Margin Score
              |
              v
      Real / Fake Prediction
              |
              v
        Web Dashboard
              |
              v
      SQLite Prediction History
```

### 1. Text Preprocessing

Input headlines undergo normalization, tokenization, numerical token replacement, and WordNet lemmatization.

### 2. TF-IDF Vectorization

Term Frequency–Inverse Document Frequency converts processed headlines into numerical vectors representing textual features.

### 3. Linear Support Vector Machine

The Linear SVM classifier learns a decision boundary between the two classes.

The application interprets the decision margin as follows:

- **Positive margin:** Fake
- **Negative margin:** Real
- **Larger absolute margin:** Greater distance from the decision boundary

The SVM decision margin is not a calibrated probability or a guarantee of factual correctness.

### 4. Prediction Analysis

The system identifies influential TF-IDF terms contributing to classification and returns up to eight terms for each prediction.

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/predict` | Classify a single headline |
| POST | `/api/predict/batch` | Classify up to 200 headlines |
| GET | `/api/samples/random` | Retrieve an unseen test sample |
| GET | `/api/history` | Retrieve saved prediction history |
| DELETE | `/api/history` | Clear prediction history |
| GET | `/api/model` | Retrieve model information and evaluation results |
| GET | `/api/health` | Check server health |

## API Example

**Request:**

```http
POST /api/predict
Content-Type: application/json
```

```json
{
  "headline": "Government announces a new education policy"
}
```

**Response Structure:**

```json
{
  "headline": "Government announces a new education policy",
  "label": "real",
  "margin": -0.85,
  "terms": [],
  "has_giveaway_words": false
}
```

*The response above is illustrative, not an actual prediction. The label, margin, and terms depend on the trained model.*

## Model Evaluation

The project includes saved evaluation artifacts:

- `model_metrics.json`
- `test_predictions.csv`

The model information API provides:

- Test evaluation metrics
- Cross-validation F1 score
- Best hyperparameters
- Vocabulary size
- Confusion matrix
- Robustness evaluation
- Influential Real and Fake terms

### Model Performance

| Metric | Score |
|---|---|
| Accuracy | 96.94% |
| Precision | 97.42% |
| Recall | 93.11% |
| F1 Score | 95.21% |

Evaluated on 7,185 test headlines. These results describe performance on the test dataset and do not guarantee real-world fact-checking accuracy.

## Testing

Execute the automated API tests using:

```bash
python -m pytest
```

## Applications

- Academic machine learning projects
- Natural Language Processing research
- News headline classification
- Educational misinformation analysis
- Text classification experiments
- Machine learning API development

## Limitations

- The model learns textual patterns from the IFND dataset.
- It does not verify claims against external factual sources.
- Some words commonly used in fact-checking articles may influence predictions.
- Performance may vary on headlines outside the training dataset.
- The SVM margin should not be interpreted as a confidence percentage.

## Future Enhancements

- Transformer-based classification models
- Multilingual fake news analysis
- Integration with fact-checking APIs
- Explainable AI visualizations
- Advanced performance dashboards
- Cloud deployment
- Real-time news monitoring

## Dataset Reference

Sharma, D. K., & Garg, S. (2021). *IFND: A benchmark dataset for fake news detection*. Complex & Intelligent Systems.

The dataset is intended for research use. Review its licensing and redistribution conditions before publishing it.

## License

No software license is currently specified. Add an appropriate LICENSE file if you intend to permit redistribution and reuse.

---

**Project Category:** Machine Learning | NLP | Linear SVM | Fake News Detection | Web Development

**Developed for academic and research purposes.**
