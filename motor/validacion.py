"""Validación del contenido de una historia (datos ya leídos de un archivo)."""


def _faltantes(obj, campos):
    return [c for c in campos if c not in obj]


def validar(datos):
    """Devuelve la lista de errores encontrados (vacía si el contenido es válido)."""
    if not isinstance(datos, dict):
        return ["Estructura incorrecta: la raíz debe ser un objeto con titulo, inicio, variables y escenas."]

    errores = []
    for c in _faltantes(datos, ("titulo", "inicio", "variables", "escenas")):
        errores.append(f"Campo obligatorio ausente en la historia: '{c}'.")

    variables = datos.get("variables")
    declaradas = set()
    if "variables" in datos:
        if not isinstance(variables, dict):
            errores.append("El campo 'variables' debe ser un mapa de booleanos.")
        else:
            for nombre, valor in variables.items():
                if not isinstance(valor, bool):
                    errores.append(f"variables.{nombre}: el valor inicial debe ser booleano.")
                declaradas.add(nombre)

    escenas = datos.get("escenas")
    if "escenas" not in datos:
        return errores
    if not isinstance(escenas, list):
        errores.append("El campo 'escenas' debe ser una lista.")
        return errores

    # Primera pasada: ids de escenas
    ids, vistos = set(), set()
    for i, esc in enumerate(escenas):
        if not isinstance(esc, dict):
            errores.append(f"escenas[{i}]: debe ser un objeto.")
            continue
        eid = esc.get("id")
        if not isinstance(eid, str) or not eid:
            errores.append(f"escenas[{i}]: falta el campo obligatorio 'id' (texto).")
            continue
        if eid in vistos:
            errores.append(f"Escena duplicada: el id '{eid}' se repite.")
        vistos.add(eid)
        ids.add(eid)

    if "inicio" in datos and datos["inicio"] not in ids:
        errores.append(f"inicio: la escena inicial '{datos['inicio']}' no existe.")

    # Segunda pasada: contenido de cada escena
    for i, esc in enumerate(escenas):
        if not isinstance(esc, dict) or not isinstance(esc.get("id"), str):
            continue
        eid = esc["id"]
        for c in _faltantes(esc, ("texto", "final", "opciones")):
            errores.append(f"Escena '{eid}': campo obligatorio ausente '{c}'.")
        if "final" in esc and not isinstance(esc["final"], bool):
            errores.append(f"Escena '{eid}': 'final' debe ser booleano.")
        opciones = esc.get("opciones")
        if "opciones" not in esc:
            continue
        if not isinstance(opciones, list):
            errores.append(f"Escena '{eid}': 'opciones' debe ser una lista.")
            continue

        if esc.get("final") is True and len(opciones) != 0:
            errores.append(f"Escena '{eid}': es final y debe tener cero opciones (tiene {len(opciones)}).")
        if esc.get("final") is False and len(opciones) == 0:
            errores.append(f"Escena '{eid}': no es final y debe tener al menos una opción.")

        oids = set()
        for j, op in enumerate(opciones):
            if not isinstance(op, dict):
                errores.append(f"Escena '{eid}', opciones[{j}]: debe ser un objeto.")
                continue
            for c in _faltantes(op, ("id", "texto", "destino")):
                errores.append(f"Escena '{eid}', opción {op.get('id', j)!r}: campo obligatorio ausente '{c}'.")
            oid = op.get("id")
            if isinstance(oid, str):
                if oid in oids:
                    errores.append(f"Escena '{eid}': la opción '{oid}' está duplicada.")
                oids.add(oid)
            etiqueta = oid if oid is not None else j
            if "destino" in op and op["destino"] not in ids:
                errores.append(f"Escena '{eid}', opción '{etiqueta}': el destino '{op['destino']}' no existe.")
            for campo in ("condiciones", "efectos"):
                mapa = op.get(campo, {})
                if not isinstance(mapa, dict):
                    errores.append(f"Escena '{eid}', opción '{etiqueta}': '{campo}' debe ser un mapa.")
                    continue
                for var, valor in mapa.items():
                    if var not in declaradas:
                        errores.append(f"Escena '{eid}', opción '{etiqueta}': {campo} usa la variable no declarada '{var}'.")
                    if not isinstance(valor, bool):
                        errores.append(f"Escena '{eid}', opción '{etiqueta}': {campo}.{var} debe ser booleano.")
    return errores
