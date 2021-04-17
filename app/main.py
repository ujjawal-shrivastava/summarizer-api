from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .worker import worker

import json

from pydantic import BaseModel, Field
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv() 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ok")
async def ok():
    return "OK"

API_TOKEN=os.environ["API_TOKEN"]
SUMMARY_ENDPOINT=os.environ["SUMMARY_ENDPOINT"]
PARAPHRASE_ENDPOINT=os.environ["PARAPHRASE_ENDPOINT"]

class Modes(str, Enum):
    SUMMARY = "SUMMARY"
    PARAPHRASE = "PARAPHRASE"
    BOTH = "BOTH"

class SummarizeData(BaseModel):
    text:str
    mode:Modes = Field(None, alias='mode')

def sendError(msg:str):
    return {
        "error":True,
        "message":msg
    }

@app.post("/summarize")
async def summarize(summarize_data:SummarizeData):

    if len(summarize_data.text)>1000:
        return sendError("Given text has length greater then the limit of 500 characters!")

    if summarize_data.mode == Modes.SUMMARY:
        processed_text = await worker(summarize_data.text, token=API_TOKEN, endpoint=SUMMARY_ENDPOINT, flag=True)
    elif summarize_data.mode == Modes.PARAPHRASE:
        processed_text = await worker(summarize_data.text, token=API_TOKEN, endpoint=PARAPHRASE_ENDPOINT)
    elif summarize_data.mode == Modes.BOTH:
        processed_text = await worker(summarize_data.text, token=API_TOKEN, endpoint=SUMMARY_ENDPOINT, flag=True)
        processed_text = await worker(processed_text, token=API_TOKEN, endpoint=PARAPHRASE_ENDPOINT)
    else:
        return sendError("Invalid Mode Type!")

    result = {
        "original_text":summarize_data.text,
        "mode":summarize_data.mode,
        "processed_text": processed_text
    }

    return result
    