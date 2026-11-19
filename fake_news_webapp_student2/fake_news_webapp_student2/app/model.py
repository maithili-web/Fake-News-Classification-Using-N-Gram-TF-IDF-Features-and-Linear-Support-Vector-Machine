"""Loads Student 2's trained pipeline and runs predictions on headlines."""
import json
import re
import warnings
from pathlib import Path

import joblib
import nltk
import numpy as np
import pandas as pd
from nltk.stem import WordNetLemmatizer

BASE = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE / 'models' / 'tfidf_svm.joblib'
DATA_DIR = BASE / 'data'

APOSTROPHES = ['\x92', '\xd5', '\x89\xdb\xaa', '\xe2\x80\x99', '\xef\xbf\xbd']
GIVEAWAY = re.compile(
    r'\b(?:fact check|factcheck|fake|false|falsely|viral|claim|claims|claimed|misleading|hoax|'
    r'rumou?r|debunk|no this|not a|shared as|shared with|morphed|doctored|old video|old photo|'
    r'video|photo|image|picture)\b')


def repair_text(text):
    """Same text repair as the training notebook."""
    for broken in APOSTROPHES:
        text = text.replace(broken, "'")
    text = re.sub(r'[^\x00-\x7f]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def load_lemmatizer():
    """Load WordNet, downloading it the first time the app runs."""
    lemmatizer = WordNetLemmatizer()
    try:
        lemmatizer.lemmatize('videos')
    except LookupError:
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        try:
            lemmatizer = WordNetLemmatizer()
            lemmatizer.lemmatize('videos')
        except LookupError as error:
            raise RuntimeError('Could not download the WordNet word list. Connect to the internet '
                               'and start the app again.') from error
    return lemmatizer


class HeadlineClassifier:
    def __init__(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')  # the model was saved with scikit-learn 1.6.1
            self.pipeline = joblib.load(MODEL_PATH)
        self.tfidf = self.pipeline.named_steps['tfidf']
        self.coef = self.pipeline.named_steps['clf'].coef_[0]
        self.terms = self.tfidf.get_feature_names_out()
        self.lemmatizer = load_lemmatizer()
        self.samples = pd.read_csv(DATA_DIR / 'test_headlines.csv')
        self.report = self._build_report()

    def preprocess(self, text):
        """Same normalization as the training notebook: lowercase, num token, lemmatize."""
        tokens = re.findall(r'[a-z]+|\d+', repair_text(text).lower())
        return ' '.join('num' if t.isdigit() else self.lemmatizer.lemmatize(t) for t in tokens)

    def predict(self, headline, top_terms=8):
        cleaned = self.preprocess(headline)
        vector = self.tfidf.transform([cleaned]).tocoo()
        key = re.sub(r'[^a-z0-9]+', ' ', repair_text(headline).lower()).strip()
        result = {'headline': headline, 'label': None, 'margin': None, 'terms': [],
                  'has_giveaway_words': bool(GIVEAWAY.search(key))}
        if vector.nnz == 0:
            return result  # the model knows none of these words
        margin = float(self.pipeline.decision_function([cleaned])[0])
        effects = [{'term': str(self.terms[i]), 'effect': round(float(v * self.coef[i]), 4)}
                   for i, v in zip(vector.col, vector.data)]
        effects.sort(key=lambda e: abs(e['effect']), reverse=True)
        result.update(label='fake' if margin > 0 else 'real',
                      margin=round(margin, 4), terms=effects[:top_terms])
        return result

    def random_sample(self):
        row = self.samples.sample(1).iloc[0]
        return {'headline': row['headline'], 'label': 'fake' if row['label'] == 1 else 'real'}

    def _build_report(self):
        saved = json.loads((DATA_DIR / 'student_2_metrics.json').read_text(encoding='utf-8'))
        results = pd.read_csv(DATA_DIR / 'student_2_test_predictions.csv')
        actual, predicted = results['label'], results['prediction']
        order = np.argsort(self.coef)
        return {
            'algorithm': saved['algorithm'],
            'test_metrics': saved['test_metrics'],
            'robustness': saved['robustness'],
            'best_params': saved['details']['best_params'],
            'cv_f1': saved['details']['cv_f1'],
            'vocabulary_size': len(self.terms),
            'confusion_matrix': {
                'real_as_real': int(((actual == 0) & (predicted == 0)).sum()),
                'real_as_fake': int(((actual == 0) & (predicted == 1)).sum()),
                'fake_as_real': int(((actual == 1) & (predicted == 0)).sum()),
                'fake_as_fake': int(((actual == 1) & (predicted == 1)).sum()),
            },
            'top_fake_terms': [str(self.terms[i]) for i in order[-15:][::-1]],
            'top_real_terms': [str(self.terms[i]) for i in order[:15]],
        }
