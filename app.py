import sys
import os
import pymongo
import pandas as pd

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from networksecurity.pipeline.training_pipeline import TrainingPipeline

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
collection = client[DATA_INGESTION_DATABASE_NAME][DATA_INGESTION_COLLECTION_NAME]

from fastapi import FastAPI, File, UploadFile,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, HTMLResponse
from starlette.responses import RedirectResponse
from uvicorn import run as app_run

app = FastAPI()
origins = ["*"]
templates = Jinja2Templates(directory="./templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/", tags=["authentication"])
# async def index():
#     return RedirectResponse(url="/docs")

@app.get("/", response_class=HTMLResponse, tags=["home"])
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    
    
@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file) #upload valid_data test file
        #print(df)
        
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        #print(table_html)
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise NetworkSecurityException(e,sys) from e


if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)
    # >uvicorn app:app --reload
