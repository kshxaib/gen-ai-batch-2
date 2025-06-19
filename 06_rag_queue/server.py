# flake8: noqa

from fastapi import FastAPI, Query
from .queue.connection import queue
from .queue.worker import process_query

app = FastAPI()

@app.get('/')
def root():
    return {"status": 'Server is up and running'}

@app.post('/')
def chat(query: str = Query(..., description="Chat Message")):

    # query ko queue me dal do
    job = queue.enqueue(process_query, query)
    print("query sended")

    # user ko response return karo ki query received 
    return {"status": "queued", "job_id": job.id}