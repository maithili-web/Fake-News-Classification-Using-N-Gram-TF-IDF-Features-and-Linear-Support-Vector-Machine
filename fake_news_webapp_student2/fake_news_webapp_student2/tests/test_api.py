import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.model import DATA_DIR


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('FAKE_NEWS_DB', str(tmp_path / 'test.db'))
    with TestClient(app) as test_client:
        yield test_client


def test_home_page_and_health(client):
    assert 'IFND Headline Checker' in client.get('/').text
    assert client.get('/api/health').json() == {'status': 'ok'}


def test_predict_fake_and_real(client):
    fake = client.post('/api/predict', json={'headline': 'Viral video claims free phones for students'}).json()
    real = client.post('/api/predict', json={'headline': 'Supreme Court seeks response from Centre on plea'}).json()
    assert fake['label'] == 'fake' and fake['margin'] > 0 and fake['has_giveaway_words']
    assert real['label'] == 'real' and real['margin'] < 0 and not real['has_giveaway_words']
    assert fake['terms'] and {'term', 'effect'} <= set(fake['terms'][0])


def test_unknown_words_give_no_result(client):
    result = client.post('/api/predict', json={'headline': 'क्या है'}).json()
    assert result['label'] is None and result['margin'] is None
    assert client.get('/api/history').json()['checks'] == []


@pytest.mark.parametrize('headline', ['', '    ', 'x' * 2001])
def test_invalid_headlines_are_rejected(client, headline):
    assert client.post('/api/predict', json={'headline': headline}).status_code == 422


def test_batch(client):
    body = {'headlines': ['Viral video claims free phones', 'Supreme Court seeks response from Centre', 'क्या']}
    assert client.post('/api/predict/batch', json=body).json()['summary'] == {
        'total': 3, 'fake': 1, 'real': 1, 'no_result': 1}
    assert client.post('/api/predict/batch', json={'headlines': []}).status_code == 422
    assert client.post('/api/predict/batch', json={'headlines': ['a'] * 201}).status_code == 422
    assert client.get('/api/history').json()['checks'] == []


def test_history_saves_newest_first_and_clears(client):
    client.post('/api/predict', json={'headline': 'First court headline'})
    client.post('/api/predict', json={'headline': 'Second court headline'})
    checks = client.get('/api/history').json()['checks']
    assert [c['headline'] for c in checks] == ['Second court headline', 'First court headline']
    client.delete('/api/history')
    assert client.get('/api/history').json()['checks'] == []


def test_sample_and_model_report(client):
    assert client.get('/api/samples/random').json()['label'] in {'fake', 'real'}
    report = client.get('/api/model').json()
    matrix = report['confusion_matrix']
    results = pd.read_csv(DATA_DIR / 'student_2_test_predictions.csv')
    assert sum(matrix.values()) == len(results)
    correct = matrix['real_as_real'] + matrix['fake_as_fake']
    assert correct / len(results) == pytest.approx(report['test_metrics']['accuracy'])
