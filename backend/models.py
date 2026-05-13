from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Persona(BaseModel):
    cedula: str
    nombres: str
    apellidos: str
    carrera: str
    facultad: str
    grupo: str
    huella_id: Optional[int] = None
    qr_id: Optional[str] = None
    dentro: bool = False
    activo: bool = True
    fecha_registro: datetime = datetime.utcnow()
