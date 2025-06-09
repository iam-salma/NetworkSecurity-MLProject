import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.main_utils.utils import (save_object, load_object, load_numpy_array_data, evaluate_models)
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)

from urllib.parse import urlparse
import mlflow
import dagshub
dagshub.init(repo_owner='salmasyed1360', repo_name='NetworkSecurity-MLProject', mlflow=True)

# os.environ["MLFLOW_TRACKING_URI"]="https://dagshub.com/salmasyed1360/NetworkSecurity-MLProject.mlflow"
# os.environ["MLFLOW_TRACKING_USERNAME"]="salmasyed1360"
# os.environ["MLFLOW_TRACKING_PASSWORD"]="7104284f1bb44ece21e0e2adb4e36a250ae3251f"


class ModelTrainer:
    def __init__(self,data_transformation_artifact:DataTransformationArtifact,
                model_trainer_config:ModelTrainerConfig):
        try:
            self.model_trainer_config:DataTransformationArtifact=model_trainer_config
            self.data_transformation_artifact:ModelTrainerConfig=data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
        
    # >mlflow ui
    def track_mlflow(self,best_model,best_model_name,classificationmetric):
        mlflow.set_registry_uri("https://dagshub.com/salmasyed1360/NetworkSecurity-MLProject.mlflow")
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
        
        with mlflow.start_run():
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score
            
            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision",precision_score)
            mlflow.log_metric("recall_score",recall_score)
            mlflow.sklearn.log_model(best_model,"model")
            # Model registry does not work with file store
            if tracking_url_type_store != "file":
                # Register the model
                # There are other ways to use the Model Registry, which depends on the use case,
                # please refer to the doc for more information:
                # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                mlflow.sklearn.log_model(best_model, "model", registered_model_name=best_model_name)
            else:
                mlflow.sklearn.log_model(best_model, "model")


        
    def train_model(self,X_train,y_train,x_test,y_test):
        models = {
                "Random Forest": RandomForestClassifier(),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(algorithm='SAMME'),
            }
        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32,128,256]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            }
        }
        model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=x_test,y_test=y_test,
                                            models=models,param=params)
        
        ## To get best model score from dict
        best_model_score = max(sorted(model_report.values()))
        
        ## To get best model name from dict
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]
        
        y_train_pred=best_model.predict(X_train)
        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)
        ## Track the experiements with mlflow
        self.track_mlflow(best_model,best_model_name,classification_train_metric)
        
        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)
        ## Track the experiements with mlflow
        self.track_mlflow(best_model,best_model_name,classification_test_metric)
        
        logging.info("done testing preds")
        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
        logging.info("before saving model")
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)
        logging.info(f"Created directory? Exists? {os.path.exists(model_dir_path)} at {model_dir_path}")
        
        logging.info(f"model_path: {self.model_trainer_config.trained_model_file_path}")
        
        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        logging.info(f"model: {type(Network_Model)}")
        save_object(file_path=self.model_trainer_config.trained_model_file_path,obj=Network_Model)
        logging.info("after saving model")
        #model pusher
        save_object(file_path="final_model/model.pkl",obj=best_model)
        logging.info("after pushing model")
        ## Model Trainer Artifact
        model_trainer_artifact=ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact


    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            
            #loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)
            
            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )
            
            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            return model_trainer_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
