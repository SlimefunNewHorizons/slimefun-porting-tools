#!/usr/bin/env python3
"""Trae la capa de almacenamiento SQL del fork chino al core de DrakesCraft.

POR QUE ASI Y NO CAMBIANDO DE CORE

Ya se intento adoptar su core entero y se cayeron los addons: nuestro fork repaqueto Slimefun a
`com.github.drakescraft_labs` y los ~40 addons de SlimefunNewHorizons estan compilados contra esos
nombres. Traer la capa DENTRO de nuestro core mantiene la ABI intacta y nadie se entera.

QUE SE TRAE

  com.xzavier0722.mc.plugin.slimefun4.storage.*   la capa en si (76 ficheros)
  city.norain.slimefun4.*                          las 8 clases de apoyo que usa

Ambos conservan su paquete de origen. No se repaquetan a cl.jackstar a proposito: asi se puede
comparar con el upstream y traer sus arreglos mas adelante. Lo que si se reescribe son sus
referencias a Slimefun, que apuntan a io.github.thebusybiscuit y aqui viven en otro sitio.

Este script SOLO copia y reescribe. No reconecta el core con la capa nueva: eso son 89 puntos
de llamada y va aparte, revisado a mano.
"""
import pathlib
import re
import shutil
import sys

GUGU = pathlib.Path("/tmp/gugu-sf/src/main/java")
DRAKE = pathlib.Path("/home/jack/workspace/drakescraft/Slimefun4-Drake/src/main/java")

# Como se llaman en su arbol -> como se llaman en el nuestro.
REMAPEOS = [
    ("io.github.thebusybiscuit.slimefun4", "com.github.drakescraft_labs.slimefun4"),
    ("me.mrCookieSlime.Slimefun", "com.github.drakescraft_labs.slimefun4.legacy.Slimefun"),
    ("me.mrCookieSlime.CSCoreLibPlugin", "com.github.drakescraft_labs.slimefun4.legacy.CSCoreLibPlugin"),
]

PAQUETES = ["com/xzavier0722", "city/norain"]


def remapear(texto):
    for viejo, nuevo in REMAPEOS:
        texto = re.sub(r"\b" + re.escape(viejo) + r"\b", nuevo, texto)
    return texto


def main():
    escribir = "--escribir" in sys.argv
    if not GUGU.exists():
        print("falta el clon del fork chino en /tmp/gugu-sf")
        return 1

    copiados = 0
    for paquete in PAQUETES:
        origen = GUGU / paquete
        if not origen.exists():
            print(f"  no existe: {paquete}")
            continue

        for f in origen.rglob("*.java"):
            rel = f.relative_to(GUGU)
            destino = DRAKE / rel
            texto = remapear(f.read_text(encoding="utf-8", errors="replace"))
            if escribir:
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(texto, encoding="utf-8")
            copiados += 1
        print(f"  {paquete}: {sum(1 for _ in origen.rglob('*.java'))} ficheros")

    print(f"\n{'copiados' if escribir else 'se copiarian'}: {copiados}")

    # Que referencias quedan sin resolver: son las que habra que mirar a mano.
    if escribir:
        pendientes = set()
        for paquete in PAQUETES:
            for f in (DRAKE / paquete).rglob("*.java"):
                texto = f.read_text(encoding="utf-8", errors="replace")
                for m in re.finditer(r"^import (?:static )?([a-z][a-zA-Z0-9_.]+)\.[A-Z]", texto, re.M):
                    pkg = m.group(1)
                    if pkg.startswith(("java.", "javax.", "org.bukkit", "com.github.drakescraft_labs",
                                       "com.xzavier0722", "city.norain", "org.jetbrains",
                                       "com.google", "org.apache", "io.papermc")):
                        continue
                    pendientes.add(pkg)
        if pendientes:
            print("\nimports externos que habra que resolver en el pom:")
            for p in sorted(pendientes):
                print(f"  {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
