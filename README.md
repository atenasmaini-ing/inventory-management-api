# 🏗️ Sistema de Gestión de Inventario de Materiales de Construcción

API REST desarrollada con FastAPI para gestionar inventarios de materiales de construcción, con validaciones automáticas, persistencia en JSON y documentación interactiva.

## 🚀 Características

- ✅ **CRUD completo** - Crear, leer, actualizar y eliminar materiales
- ✅ **Validaciones robustas** - Usando Pydantic con validadores personalizados
- ✅ **Persistencia de datos** - Almacenamiento en archivo JSON
- ✅ **Documentación automática** - Swagger UI y ReDoc
- ✅ **Manejo centralizado de errores** - Respuestas estandarizadas
- ✅ **Arquitectura modular** - Código organizado y mantenible

## 📋 Campos del Inventario

Cada material incluye:
- **Información básica**: Nombre, categoría, descripción
- **Inventario**: Cantidad, unidad de medida, stock mínimo
- **Financiero**: Precio unitario
- **Logística**: Proveedor, ubicación en bodega, proyecto asignado
- **Gestión**: Responsable, SKU, fecha de ingreso, estado

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **Pydantic** - Validación de datos y settings
- **Uvicorn** - Servidor ASGI
- **Python 3.14** - Lenguaje de programación

## 📦 Instalación

### Requisitos previos
- Python 3.10 o superior
- pip

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/atenasmaini-ing/inventory-management-api.git
cd inventory-management-api
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
```

3. **Activar entorno virtual**

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Ejecutar el servidor**
```bash
uvicorn main:app --reload
```

6. **Acceder a la documentación**
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 📖 Uso de la API

### Endpoints disponibles

#### Crear material
```http
POST /api/v1/materials
Content-Type: application/json

{
  "name": "Cemento Portland",
  "category": "Estructural",
  "quantity": 50,
  "unit": "bolsa",
  "unit_price": 450.50,
  "supplier": "Cementos del Norte"
}
```

#### Listar todos los materiales
```http
GET /api/v1/materials
```

#### Obtener material por ID
```http
GET /api/v1/materials/{material_id}
```

#### Actualizar material
```http
PUT /api/v1/materials/{material_id}
Content-Type: application/json

{
  "quantity": 100,
  "location": "Bodega A"
}
```

#### Eliminar material
```http
DELETE /api/v1/materials/{material_id}
```

## 🔧 Estructura del Proyecto
```
inventory-management-api/
├── main.py              # Punto de entrada de la aplicación
├── materials.py         # Router con endpoints CRUD
├── models.py            # Modelos Pydantic
├── database.py          # Lógica de persistencia
├── config.py            # Configuración centralizada
├── requirements.txt     # Dependencias
├── inventory.json       # Base de datos (generado automáticamente)
└── README.md           # Este archivo
```

## ✅ Validaciones Implementadas

- Nombres y categorías no vacíos
- Cantidades y precios no negativos
- Fechas de ingreso no futuras
- Estados predefinidos (activo, obsoleto, en espera)
- Validadores personalizados con mensajes claros

## 📝 Formato de Respuestas

### Éxito
```json
{
  "success": true,
  "message": "Material creado correctamente",
  "data": { ... }
}
```

### Error
```json
{
  "success": false,
  "message": "Error de validación",
  "error_code": "VALIDATION_ERROR",
  "details": { ... }
}
```

## 🎯 Próximas Mejoras

- [ ] Base de datos PostgreSQL
- [ ] Autenticación y autorización
- [ ] Paginación en listados
- [ ] Filtros y búsqueda avanzada
- [ ] Reportes y estadísticas
- [ ] Deploy en Render/Railway

## 👤 Autor

**Atenas Maini**
- GitHub: [@atenasmaini-ing](https://github.com/atenasmaini-ing)

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la Licencia MIT.