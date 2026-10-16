from database import SessionLocal, Herramienta
from generar_excel import herramientas_organizadas

# Lista de compatibilidad
datos_herramientas = [
    {
        "clave": item["clave"],
        "descripcion": f"{item['nombre']} - {item['descripcion']}",
        "ubicacion": item["ubicacion"],
        "cantidad": item["cantidad"]
    }
    for item in herramientas_organizadas
]

def cargar_datos():
    db = SessionLocal()
    print("Iniciando la actualización y reorganización de las 57 herramientas en los 3 estantes...")
    
    agregadas = 0
    actualizadas = 0
    
    for item in datos_herramientas:
        existe = db.query(Herramienta).filter(Herramienta.clave == item["clave"]).first()
        
        if not existe:
            nueva = Herramienta(
                clave=item["clave"],
                descripcion=item["descripcion"],
                ubicacion=item["ubicacion"],
                cantidad_total=item["cantidad"],
                cantidad_disponible=item["cantidad"],
                foto_url=""
            )
            db.add(nueva)
            agregadas += 1
            print(f"[+] Agregada: {item['clave']} -> {item['ubicacion']}")
        else:
            existe.descripcion = item["descripcion"]
            existe.ubicacion = item["ubicacion"]
            existe.cantidad_total = item["cantidad"]
            actualizadas += 1
            print(f"[*] Reubicada: {item['clave']} -> {item['ubicacion']}")
            
    db.commit()
    db.close()
    print(f"\n¡Listo! {actualizadas} herramientas reubicadas y actualizadas con descripciones amigables.")

if __name__ == "__main__":
    cargar_datos()