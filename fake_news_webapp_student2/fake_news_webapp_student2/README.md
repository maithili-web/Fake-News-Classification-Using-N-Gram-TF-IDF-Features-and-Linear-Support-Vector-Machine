# IFND Headline Checker

A web app for testing Student 2's TF-IDF + Linear SVM fake news model.

## Run it
You need Python 3.10 or newer. In this folder, run:

```
pip install -r requirements.txt
python run.py
```

The app opens at http://127.0.0.1:8000. Press Ctrl+C in the terminal to stop it.

The first start needs internet access to download the WordNet word list used for lemmatization.

An SVM gives a margin score rather than a probability. Positive means Fake, negative means Real, and a
larger distance from 0 means the headline is further from the decision boundary.

## What's inside
- `app/main.py`: FastAPI routes
- `app/model.py`: model loading and prediction
- `app/database.py`: SQLite check history, stored in `data/history.db`
- `static/`: web interface (HTML, CSS, JavaScript)
- `tests/`: API tests; run them with `python -m pytest`

## API
Interactive API documentation is at http://127.0.0.1:8000/docs.

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/predict` | Check one headline and save it to the history |
| POST | `/api/predict/batch` | Check up to 200 headlines |
| GET | `/api/samples/random` | Get an unseen test headline with its label |
| GET | `/api/history` | List saved checks |
| DELETE | `/api/history` | Delete saved checks |
| GET | `/api/model` | Get model details and test results |
| GET | `/api/health` | Confirm the server is running |

## Limits of the model
The model learned the wording of the IFND dataset. It does not check facts. Words common on
fact-checking sites, such as "fact check" and "viral", push a headline towards Fake, so its
results should not be used to decide whether a claim is true.

IFND is for research use only. Cite: Sharma, D. K., & Garg, S. (2021). IFND: a benchmark dataset
for fake news detection. Complex & Intelligent Systems.
