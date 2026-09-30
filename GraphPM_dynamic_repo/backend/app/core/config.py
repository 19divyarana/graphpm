from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "GraphPM API"
    database_url: str = "sqlite:///./graphpm.db"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "graphpm"
    model_path: str = "./artifacts/risk_model.joblib"
    cors_origin: str = "*"

settings = Settings()
