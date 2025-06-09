import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    TrainingPipelineConfig
)


if __name__=='__main__':
    try:
        trainingpipelineconfig=TrainingPipelineConfig()
        
        logging.info("Initiate the data ingestion")
        dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
        data_ingestion=DataIngestion(dataingestionconfig)
        data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
        logging.info(f"Data Ingestion completed and artifact: {data_ingestion_artifact}")
        
        logging.info("Initiate the data Validation")
        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        data_validation=DataValidation(data_ingestion_artifact,data_validation_config)
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info(f"Data Validation completed and artifact: {data_validation_artifact}")
        
        logging.info("data Transformation started")
        data_transformation_config=DataTransformationConfig(trainingpipelineconfig)
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        logging.info(f"Data Transformation completed and artifact: {data_transformation_artifact}")
        
        logging.info("Model Training started")
        model_trainer_config=ModelTrainerConfig(trainingpipelineconfig)
        model_trainer=ModelTrainer(data_transformation_artifact,model_trainer_config)
        model_trainer_artifact=model_trainer.initiate_model_trainer()
        logging.info(f"Model Training completed and artifact: {model_trainer_artifact}")
        
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
