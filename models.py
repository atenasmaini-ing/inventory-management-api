from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import date

class MaterialBase(BaseModel):
    # Nombre del material. Obligatorio.
    name: str = Field(..., min_length=1, max_length=200,
                      description="Nombre del material")
    
    # Categoría del material. Ejemplo: Estructural, Hidráulica, Eléctrica, etc.
    category: str = Field(..., min_length=1, max_length=100,
                          description="Categoría del material")
    
    # Cantidad disponible. Obligatorio.
    quantity: float = Field(..., ge=0, description="Cantidad disponible")
    
    # Unidad de medida. Ejemplo: m, kg, unidad, m², litros, etc.
    unit: str = Field(..., min_length=1, max_length=20,
                      description="Unidad de medida")
    
    # Precio unitario. Obligatorio, debe ser mayor o igual a 0.
    unit_price: float = Field(..., ge=0.0, description="Precio unitario")
    
    # Proveedor del material. Obligatorio.
    supplier: str = Field(..., min_length=1, max_length=150,
                          description="Nombre del proveedor")
    
    # Descripción opcional del material.
    description: Optional[str] = Field(
        None, max_length=1000, description="Descripción del material")
    
    # Nivel mínimo de stock. Opcional.
    minimum_stock: Optional[float] = Field(
        None, ge=0, description="Nivel mínimo de stock para alertas")
    
    # Ubicación en bodega. Opcional.
    location: Optional[str] = Field(
        None, max_length=100, description="Ubicación en bodega")
    
    # Obra o proyecto asignado. Opcional.
    project: Optional[str] = Field(
        None, max_length=150, description="Obra o proyecto al que pertenece")
    
    # Responsable del material. Opcional.
    responsible: Optional[str] = Field(
        None, max_length=100, description="Persona responsable del material")
    
    # Código interno (SKU). Opcional.
    sku: Optional[str] = Field(
        None, max_length=50, description="Código interno o SKU")
    
    # Fecha de ingreso. Opcional.
    entry_date: Optional[date] = Field(
        None, description="Fecha de ingreso al inventario")
    
    # Estado del material. Por defecto "activo".
    status: str = Field(
        default="activo", max_length=20, 
        description="Estado del material (activo, obsoleto, en espera)")
    
    # --- VALIDACIONES PERSONALIZADAS ---
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """El nombre no puede estar vacío ni solo contener espacios."""
        if not value.strip():
            raise ValueError("El nombre no puede estar vacío o solo con espacios.")
        return value.strip()
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, value: str) -> str:
        """La categoría no puede estar vacía."""
        if not value.strip():
            raise ValueError("La categoría no puede estar vacía o solo con espacios.")
        return value.strip()
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, value: float) -> float:
        """La cantidad debe ser un número positivo o cero."""
        if value < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        return value
    
    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, value: float) -> float:
        """El precio unitario debe ser positivo."""
        if value < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        return value
    
    @field_validator('entry_date')
    @classmethod
    def validate_entry_date(cls, value: Optional[date]) -> Optional[date]:
        """La fecha de ingreso no puede ser futura."""
        if value and value > date.today():
            raise ValueError("La fecha de ingreso no puede ser en el futuro.")
        return value
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, value: str) -> str:
        """El estado debe ser uno de los valores permitidos."""
        allowed_statuses = ['activo', 'obsoleto', 'en espera']
        if value.lower() not in allowed_statuses:
            raise ValueError(f"El estado debe ser uno de: {', '.join(allowed_statuses)}")
        return value.lower()

class MaterialCreate(MaterialBase):
    """Modelo usado para crear un nuevo material (POST)."""
    pass
from fastapi import APIRouter, HTTPException
from database import MaterialDatabase
from models import MaterialCreate  # ← AGREGA ESTA LÍNEA

router = APIRouter(tags=["materials"])
db = MaterialDatabase()

@router.post("/materials", status_code=201)
def create_material(material: MaterialCreate):
    """
    Crea un nuevo material en el inventario usando un modelo Pydantic.
    - Validación automática (FastAPI + Pydantic).
    - Asigna un ID incremental.
    - Persiste el nuevo material en inventory.json.
    """
    # Convertimos el modelo validado a dict
    data = material.model_dump()
    
    # Guardado en memoria + persistencia
    created = db.add_material(data)
    db.save_data()
    
    return {
        "success": True,
        "message": "Material creado correctamente",
        "data": created
    }
class MaterialUpdate(BaseModel):
    """Modelo usado para actualizar parcialmente un material existente."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    unit_price: Optional[float] = Field(None, ge=0.0)
    supplier: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    minimum_stock: Optional[float] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=100)
    project: Optional[str] = Field(None, max_length=150)
    responsible: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    entry_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=20)

@router.get("/materials")
def list_materials():
    """
    Endpoint para listar todos los materiales.
    Retorna una lista de diccionarios con los datos actuales del inventario.
    """
    return db.list_materials()

@router.get("/materials/{material_id}")
def get_material(material_id: int):
    """
    Devuelve un material por su ID.
    - Si existe, retorna el objeto (dict) con sus campos.
    - Si no existe, lanza un 404 con un mensaje claro.
    """
    material = db.get_material(material_id)
    if material is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Material con ID {material_id} no encontrado"
        )
    return material

@router.put("/materials/{material_id}")
def update_material(material_id: int, payload: dict):
    """
    Actualiza los datos de un material existente.
    - Busca el ID.
    - Aplica solo los campos enviados.
    - Guarda los cambios en el JSON.
    """
    material = db.get_material(material_id)
    if material is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Material con ID {material_id} no encontrado"
        )
    
    material.update(payload)
    db.materials[material_id] = material
    db.save_data()
    
    return {
        "success": True,
        "message": f"Material con ID {material_id} actualizado correctamente",
        "data": material
    }

@router.delete("/materials/{material_id}")
def delete_material(material_id: int):
    """
    Elimina un material por ID.
    - Si existe: lo borra del diccionario en memoria y persiste el cambio en JSON.
    - Si no existe: responde 404.
    """
    material = db.get_material(material_id)
    if material is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Material con ID {material_id} no encontrado"
        )
    
    del db.materials[material_id]
    db.save_data()
    
    return {
        "success": True,
        "message": f"Material con ID {material_id} eliminado correctamente"
    }
class MaterialResponse(BaseModel):
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje breve para el cliente")
    data: Optional[dict] = Field(
        None,
        description="Material devuelto (dict) o None si no aplica"
    )
class MaterialListResponse(BaseModel):
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje para el cliente")
    data: List[dict] = Field(
        default_factory=list,
        description="Listado de materiales (dict) en este paso"
    )
    total: int = Field(..., description="Cantidad total de elementos devueltos")
class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Siempre False en errores")
    message: str = Field(..., description="Mensaje breve para el cliente")
    error_code: Optional[str] = Field(None, description="Código interno opcional")
    details: Optional[dict] = Field(None, description="Metadatos del error (opcional)")