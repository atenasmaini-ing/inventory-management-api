from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from config import settings
from models import MaterialCreate, ErrorResponse
import materials

# Inicializamos la aplicación usando la configuración centralizada
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# ========== EXCEPTION HANDLERS ==========

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Formatea cualquier HTTPException (p.ej., 404 del GET-by-id) a nuestro JSON estándar.
    """
    msg = exc.detail if isinstance(exc.detail, str) else "Error en la solicitud"
    payload = ErrorResponse(
        success=False,
        message=msg,
        error_code=f"HTTP_{exc.status_code}",
        details=None
    ).model_dump()
    return JSONResponse(status_code=exc.status_code, content=payload)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Captura errores de validación de FastAPI/Pydantic (422) y los centra en un formato uniforme.
    """
    # Procesar errores eliminando completamente los objetos no serializables
    errors_list = []
    
    for error in exc.errors():
        # Crear un nuevo diccionario con solo strings
        clean_error = {
            "field": " -> ".join(str(x) for x in error.get("loc", [])),
            "message": str(error.get("msg", "")),
            "type": str(error.get("type", ""))
            # NO incluimos 'input', 'ctx', ni 'url' - solo campos string
        }
        errors_list.append(clean_error)
    
    # Crear payload completamente limpio
    payload = {
        "success": False,
        "message": "Error de validación en la solicitud",
        "error_code": "VALIDATION_ERROR",
        "details": {"errors": errors_list}
    }
    
    return JSONResponse(status_code=422, content=payload)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Fallback para cualquier error no controlado (500).
    """
    payload = ErrorResponse(
        success=False,
        message="Error interno del servidor",
        error_code="INTERNAL_SERVER_ERROR",
        details=None
    ).model_dump()
    return JSONResponse(status_code=500, content=payload)

# ========== ENDPOINTS ==========

@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {"message": "Bienvenido al Sistema de Gestión de Inventario 🏗️"}

@app.post("/materials")
def create_material(payload: MaterialCreate):
    """Endpoint para crear un nuevo material (aún sin persistencia)"""
    return {
        "success": True,
        "message": "Material recibido (aún sin guardar)",
        "data": payload.model_dump()
    }

