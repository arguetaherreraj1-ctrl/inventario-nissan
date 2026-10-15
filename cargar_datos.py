from database import SessionLocal, Herramienta

# Lista completa de las 57 piezas del inventario físico Nissan
datos_herramientas = [
    {"clave": "NI-50190-C", "descripcion": "TIRE PRESSURE MONITOR TESTER", "ubicacion": "A1", "cantidad": 1},
    {"clave": "CPX900PLNIMX", "descripcion": "BATTERY ELECTRICAL NISSAN", "ubicacion": "C2", "cantidad": 1},
    {"clave": "BK5700", "descripcion": "ASSY BK5700 UNIT PACK", "ubicacion": "A2", "cantidad": 1},
    {"clave": "NI-53380", "descripcion": "NISSAN DTS 4425A DTS 4425A", "ubicacion": "A1", "cantidad": 1},
    {"clave": "NI51980A", "descripcion": "VALVE STEM PULLER", "ubicacion": "A1", "cantidad": 1},
    {"clave": "BAH2820VG10", "descripcion": "1000V GLOVES 1000V", "ubicacion": "A2", "cantidad": 1},
    {"clave": "CY10440A", "descripcion": "HARD HAT HAND FACE SHIELD", "ubicacion": "A2", "cantidad": 1},
    {"clave": "BAHBH6FC2000", "descripcion": "2 TON FOLDABLE CRANE", "ubicacion": "D1", "cantidad": 1},
    {"clave": "1409L", "descripcion": "KV311039S0 NISSAN CVT ALTERNAT", "ubicacion": "A5B4", "cantidad": 1},
    {"clave": "NI-52584", "descripcion": "CHARGE PIPE ADAPTER KIT", "ubicacion": "A5B3", "cantidad": 1},
    {"clave": "A91F", "descripcion": "STRAP WRENCH", "ubicacion": "A4", "cantidad": 1},
    {"clave": "NI-46532", "descripcion": "BRAKE HEIGHT TOOL", "ubicacion": "A4", "cantidad": 1},
    {"clave": "NI-45747", "descripcion": "WRENCH LOCK RING", "ubicacion": "A4", "cantidad": 1},
    {"clave": "NI-46214", "descripcion": "WRENCH FUEL TANK LOCK RING", "ubicacion": "A4", "cantidad": 1},
    {"clave": "NI-53166", "descripcion": "DIREC INJECTION 1.5L", "ubicacion": "A5", "cantidad": 1},
    {"clave": "NI-44321-B", "descripcion": "FUEL PRESSURE TEST KIT", "ubicacion": "A3", "cantidad": 1},
    {"clave": "NI-51875A", "descripcion": "EVAP SERVICE TOOL", "ubicacion": "A5B4", "cantidad": 1},
    {"clave": "S6176", "descripcion": "DADO SENSOR DE OXIGENO", "ubicacion": "A5D1", "cantidad": 1},
    {"clave": "NI-45488", "descripcion": "FUEL LINE DISCONNECT TOOL 2PC", "ubicacion": "A5C3", "cantidad": 2},
    {"clave": "NI-44626", "descripcion": "SOCKET22MM OFFSET", "ubicacion": "A3", "cantidad": 1},
    {"clave": "NI-45695-A", "descripcion": "COOLANT REFIL TOOL", "ubicacion": "A3", "cantidad": 1},
    {"clave": "NI-51771", "descripcion": "RADIATOR PRESSURE TESTER", "ubicacion": "C3", "cantidad": 1},
    {"clave": "SVTS272A", "descripcion": "COOLING SYSTEM PRESSURE TESTER", "ubicacion": "A5", "cantidad": 1},
    {"clave": "NI-54466", "descripcion": "5025 DEF REFRACTOMETER", "ubicacion": "A4", "cantidad": 1},
    {"clave": "CNT3M301A", "descripcion": "IN ELECTRONIC DIGITAL", "ubicacion": "C3", "cantidad": 1},
    {"clave": "FBST338", "descripcion": "STRAIGHT 38 BLADE SET", "ubicacion": "A5A1", "cantidad": 1},
    {"clave": "FRHM17", "descripcion": "3/8DR 17MM FLRNT 6PT C/", "ubicacion": "A5A2", "cantidad": 1},
    {"clave": "QJRXSM10A", "descripcion": "TORQ ADAPT 10MM 6-PT FL", "ubicacion": "A5A3", "cantidad": 1},
    {"clave": "SVT262-28A", "descripcion": "32X16MM DEEP RAD ADAPTR", "ubicacion": "A4", "cantidad": 1},
    {"clave": "SVT262-29", "descripcion": "ADAPTADOR RADIATOR CAP 45MM RED CAP DAP", "ubicacion": "A4", "cantidad": 1},
    {"clave": "ACTUVITE", "descripcion": "INJECTNGUN/LTKITBR134A/", "ubicacion": "A4", "cantidad": 1},
    {"clave": "EEPD501", "descripcion": "DIESEL COMPRESSION TEST", "ubicacion": "A2", "cantidad": 1},
    {"clave": "ACT825", "descripcion": "SAE J2791 Y 2913 CERT LEA", "ubicacion": "A1", "cantidad": 1},
    {"clave": "NI-28431-B", "descripcion": "FLOURESCENT DYE ADDITIV", "ubicacion": "A4", "cantidad": 1},
    {"clave": "NI-48817-8", "descripcion": "AL CRIMPING PLIETT", "ubicacion": "A4", "cantidad": 1},
    {"clave": "NI-48891", "descripcion": "SOCKET 14MM SPARK PLUG", "ubicacion": "A3", "cantidad": 1},
    {"clave": "NI-51001-B", "descripcion": "NS-3 TRANSMISSION OIL FIL KIT", "ubicacion": "C1", "cantidad": 1},
    {"clave": "NI-52982", "descripcion": "LOCK NUT CAPE CHISEL", "ubicacion": "A3", "cantidad": 1},
    {"clave": "NI-42909", "descripcion": "EVAP KIT", "ubicacion": "A3", "cantidad": 1},
    {"clave": "CTECH1JM240", "descripcion": "CTECH MICRO 240IN-LB J", "ubicacion": "A4", "cantidad": 1},
    {"clave": "NI-45722", "descripcion": "LOCK RING TOOL 130MM", "ubicacion": "A4", "cantidad": 1},
    {"clave": "NI-24460-92", "descripcion": "COOLING SYSTEM ADAPTER", "ubicacion": "A4", "cantidad": 1},
    {"clave": "GLASS60R", "descripcion": "RED FRAME CLEAR LENS SFTY GLAS", "ubicacion": "A1", "cantidad": 1},
    {"clave": "YA427B", "descripcion": "WELDERS GLOVE", "ubicacion": "A2", "cantidad": 1},
    {"clave": "NI-52972", "descripcion": "RQ TRANS FILL KIT", "ubicacion": "A5", "cantidad": 1},
    {"clave": "GA3640A", "descripcion": "MAGNETIC DIAL INDICATOR SET", "ubicacion": "A3", "cantidad": 1},
    {"clave": "PBN500", "descripcion": "SPC NON/MAR'PRYBR SET", "ubicacion": "A3", "cantidad": 1},
    {"clave": "YA6930", "descripcion": "ENGINE OIL PRESSURE SET", "ubicacion": "B3", "cantidad": 1},
    {"clave": "RC50C", "descripcion": "COMPRESOR DE ANILLOS 2 BANDAS", "ubicacion": "A5", "cantidad": 1},
    {"clave": "NI-37228", "descripcion": "SEAL CUTTER", "ubicacion": "A4", "cantidad": 1},
    {"clave": "EEPV509", "descripcion": "CYLINDER LEAKAGE TESTER", "ubicacion": "A5", "cantidad": 1},
    {"clave": "RTEMP8", "descripcion": "MULTI-LASER INFRARED THERM", "ubicacion": "B3", "cantidad": 1},
    {"clave": "EEPV507", "descripcion": "SET DE INDICADOR DE PRESION DE ACEITE 0-100 PSI", "ubicacion": "A3", "cantidad": 1},
    {"clave": "GA424A", "descripcion": "INDICADOR DE CARATULA DE LA TENSION DE BAND", "ubicacion": "A5", "cantidad": 1},
    {"clave": "KVMR001511", "descripcion": "FITTING VALVE STEM SEALS", "ubicacion": "A3", "cantidad": 1},
    {"clave": "KVMR001335", "descripcion": "PLIERS", "ubicacion": "A3", "cantidad": 1},
    {"clave": "KV10100QAB", "descripcion": "BELT FITTING TOOL", "ubicacion": "A5A4", "cantidad": 1},
]

def cargar_datos():
    db = SessionLocal()
    print("Iniciando la carga de datos del catálogo físico Nissan (57 piezas)...")
    
    agregadas = 0
    actualizadas = 0
    
    for item in datos_herramientas:
        existe = db.query(Herramienta).filter(Herramienta.clave == item["clave"]).first()
        
        if not existe:
            nueva_herramienta = Herramienta(
                clave=item["clave"],
                descripcion=item["descripcion"],
                ubicacion=item["ubicacion"],
                cantidad_total=item["cantidad"],
                cantidad_disponible=item["cantidad"],
                foto_url=""
            )
            db.add(nueva_herramienta)
            agregadas += 1
            print(f"[+] Agregada: {item['clave']} - {item['descripcion']} ({item['ubicacion']})")
        else:
            # Actualizamos descripción y ubicación si cambiaron
            existe.descripcion = item["descripcion"]
            existe.ubicacion = item["ubicacion"]
            existe.cantidad_total = item["cantidad"]
            actualizadas += 1
            print(f"[*] Actualizada: {item['clave']}")
            
    db.commit()
    db.close()
    print(f"\n¡Listo! Agregadas: {agregadas}, Actualizadas: {actualizadas}. Total en inventario: {agregadas + actualizadas}")

if __name__ == "__main__":
    cargar_datos()