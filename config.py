from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List

class Settings(BaseSettings):
    """Configuración base del proyecto"""
    
    # Información general
    app_name: str = "Inventory Management API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Archivo de base de datos
    database_file: str = "inventory.json"
    
    # Documentación
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Configuración interna de Pydantic
    model_config = ConfigDict(
        case_sensitive=False,
        extra="ignore"
    )

# Instancia global de configuración
settings = Settings()

def get_config_summary() -> dict:
    """Devuelve un resumen simple de la configuración actual."""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug
    }