from fastapi import APIRouter, HTTPException
from database import MaterialDatabase
from models import MaterialCreate, MaterialUpdate, MaterialResponse, MaterialListResponse
router = APIRouter(tags=["materials"])
db = MaterialDatabase()

@router.post("/materials", status_code=201, response_model=MaterialResponse)
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

@router.get("/materials", response_model=MaterialListResponse)
def list_materials():
    items = db.list_materials()
    return {
        "success": True,
        "message": f"Se encontraron {len(items)} materiales",
        "data": items,
        "total": len(items)
    }

@router.get("/materials/{material_id}", response_model=MaterialResponse)
def get_material(material_id: int):
    material = db.get_material(material_id)
    if material is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Material con ID {material_id} no encontrado"
        )
    return {
        "success": True,
        "message": "Material encontrado correctamente",
        "data": material
    }

@router.put("/materials/{material_id}", response_model=MaterialResponse)
def update_material(material_id: int, changes: MaterialUpdate):
    """
    Actualiza los datos de un material existente usando MaterialUpdate (Pydantic).
    - Aplica solo los campos enviados (parcial).
    - Valida tipos y rangos automáticamente.
    - Persiste el cambio en inventory.json.
    """
    # 1) Buscar el material
    material = db.get_material(material_id)
    if material is None:
        raise HTTPException(
            status_code=404,
            detail=f"Material con ID {material_id} no encontrado"
        )
    
    # 2) Tomar únicamente los campos provistos en el body
    update_data = changes.model_dump(exclude_unset=True)
    
    # 3) Aplicar los cambios en memoria
    material.update(update_data)
    db.materials[material_id] = material
    
    # 4) Guardar los cambios en el archivo JSON
    db.save_data()
    
    # 5) Responder al cliente
    return {
        "success": True,
        "message": f"Material con ID {material_id} actualizado correctamente",
        "data": material
    }

@router.delete("/materials/{material_id}", response_model=MaterialResponse)
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
    "message": f"Material con ID {material_id} eliminado correctamente",
    "data": None
}