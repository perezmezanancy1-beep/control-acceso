from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Persona(BaseModel):
    cedula: str
    nombres: str
    apellidos: str
    carrera: str
    huella_id: Optional[int] = None
    qr_id: Optional[str] = None
    grupo: str
    dentro: bool = False
    activo: bool = True
    fecha_registro: datetime = datetime.utcnow()