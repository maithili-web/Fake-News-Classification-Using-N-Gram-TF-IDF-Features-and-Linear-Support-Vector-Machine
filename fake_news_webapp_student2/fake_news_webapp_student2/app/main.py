"""FastAPI backend: JSON API under /api and the web interface at /."""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints

from . import database
from .model import HeadlineClassifier

Headline = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
STATIC_DIR = Path(__file__).resolve().parent.parent / 'static'


class PredictRequest(BaseModel):
    headline: Headline


class BatchRequest(BaseModel):
    headlines: list[Headline] = Field(min_length=1, max_length=200)


@asynccontextmanager
async def lifespan(app):
    database.init_db()
    app.state.classifier = HeadlineClassifier()
    yield


app = FastAPI(title='IFND Headline Checker API', version='1.0.0', lifespan=lifespan)


@app.get('/api/health')
def health():
    return {'status': 'ok'}


@app.post('/api/predict')
def predict(body: PredictRequest, request: Request):
    """Classify one headline and save it to the history."""
    result = request.app.state.classifier.predict(body.headline)
    if result['label']:
        database.add_check(body.headline, result['label'], result['margin'])
    return result


@app.post('/api/predict/batch')
def predict_batch(body: BatchRequest, request: Request):
    """Classify up to 200 headlines. Batch results are not saved to the history."""
    classifier = request.app.state.classifier
    results = [classifier.predict(h) for h in body.headlines]
    labels = [r['label'] for r in results]
    return {'results': results,
            'summary': {'total': len(results), 'fake': labels.count('fake'),
                        'real': labels.count('real'), 'no_result': labels.count(None)}}


@app.get('/api/samples/random')
def random_sample(request: Request):
    """Return an unseen test headline with its dataset label."""
    return request.app.state.classifier.random_sample()


@app.get('/api/history')
def history(limit: int = Query(default=50, ge=1, le=500)):
    return {'checks': database.list_checks(limit)}


@app.delete('/api/history')
def clear_history():
    database.clear_checks()
    return {'status': 'cleared'}


@app.get('/api/model')
def model_report(request: Request):
    return request.app.state.classifier.report


app.mount('/', StaticFiles(directory=STATIC_DIR, html=True), name='static')
