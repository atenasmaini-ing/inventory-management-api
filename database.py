"""
Persistencia con JSON (fase 1):
- Prepara y resuelve la ruta del archivo de datos (inventory.json).
- Crea el archivo si no existe.
- Implementa carga (load_data) y guardado (save_data) del catálogo.
- Mantiene la estructura en memoria como dicts simples (aún no Pydantic Models).
"""

from pathlib import Path
import json
from typing import Dict, List, Optional


DEFAULT_DB_FILE = "inventory.json"

# Ruta absoluta segura al JSON, al lado de este archivo .py
DB_PATH: Path = Path(__file__).with_name(DEFAULT_DB_FILE)


def get_db_path() -> Path:
    """Devuelve la ruta absoluta del archivo de base de datos."""
    return DB_PATH


def ensure_db_file_exists() -> Path:
    """
    Crea el archivo inventory.json si no existe.
    No escribe datos todavía, solo garantiza que el archivo esté presente.
    """
    path = get_db_path()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        # Inicializamos con una estructura mínima válida
        path.write_text(json.dumps({"materials": [], "next_id": 1}, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


class MaterialDatabase:
    """
    Clase que actúa como base de datos en memoria para el inventario de materiales.
    Ahora incluye persistencia: load/save en inventory.json.
    - Estructura en memoria: dict[int, dict]
    - Formato en disco: {"materials": [ {...}, {...} ], "next_id": N}
    """

    def __init__(self, file_path: Optional[str] = None):
        # Diccionario interno para almacenar materiales en memoria
        self.materials: Dict[int, Dict] = {}
        self.next_id: int = 1  # ID incremental para nuevos materiales

        # Ruta del archivo; si no te pasan una, usamos la por defecto
        self._file_path: Path = Path(file_path) if file_path else get_db_path()
        ensure_db_file_exists()  # Garantiza que el archivo exista con estructura básica
        self.load_data()         # Hidrata la memoria con lo que haya en disco

    # ---------------------------------------------------------------------
    # Persistencia
    # ---------------------------------------------------------------------
    def load_data(self) -> None:
        """
        Lee el archivo JSON y carga los materiales en memoria.
        Espera un JSON con llaves: "materials" (lista) y "next_id" (int).
        Si el archivo está vacío o corrupto, re-inicializa estructura.
        """
        try:
            text = self._file_path.read_text(encoding="utf-8").strip()
            if not text:
                # Si está vacío, inicializamos estructura básica
                self.materials = {}
                self.next_id = 1
                self.save_data()
                return

            data = json.loads(text)

            # Validación mínima de estructura
            materials_list: List[Dict] = data.get("materials", [])
            next_id_val: int = data.get("next_id", 1)

            # Cargar en memoria como dict {id: dict_material}
            self.materials = {}
            for item in materials_list:
                # Validación básica de que tenga id
                material_id = item.get("id")
                if isinstance(material_id, int):
                    self.materials[material_id] = item

            # Si no viene next_id, lo calculamos como max_id + 1
            if isinstance(next_id_val, int) and next_id_val > 0:
                self.next_id = next_id_val
            else:
                self.next_id = (max(self.materials.keys()) + 1) if self.materials else 1

        except Exception as e:
            # Si algo falla (JSON malformado, etc.), re-inicializamos seguro
            print(f"[MaterialDatabase.load_data] Error al cargar datos: {e}")
            self.materials = {}
            self.next_id = 1
            self.save_data()

    def save_data(self) -> None:
        """
        Vuelca el estado actual a disco en formato JSON.
        Estructura:
        {
          "materials": [ {...}, {...} ],
          "next_id": <int>
        }
        """
        try:
            data = {
                "materials": list(self.materials.values()),
                "next_id": self.next_id
            }
            self._file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"[MaterialDatabase.save_data] Error al guardar datos: {e}")

    # ---------------------------------------------------------------------
    # Operaciones en memoria (con persistencia automática)
    # ---------------------------------------------------------------------
    def add_material(self, material_data: Dict) -> Dict:
        """
        Agrega un nuevo material al inventario.
        Persistencia: guarda inmediatamente tras agregar.
        """
        material_id = self.next_id
        record = {"id": material_id, **material_data}
        self.materials[material_id] = record
        self.next_id += 1

        # Guardamos tras cada cambio
        self.save_data()
        return record

    def list_materials(self) -> List[Dict]:
        """Devuelve todos los materiales actualmente en memoria."""
        return list(self.materials.values())

    def get_material(self, material_id: int) -> Optional[Dict]:
        """Devuelve un material específico por ID (o None si no existe)."""
        return self.materials.get(material_id)