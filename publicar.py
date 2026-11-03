#!/usr/bin/env python3
"""Publica en SlimefunNewHorizons un addon ya portado a 1.21.11.

No se hace fork: se crea un repositorio nuevo con el codigo integrado al ecosistema Drake, y se
acredita al autor original en el README y en un fichero aparte, como exige la GPL y como
corresponde con quien hizo el trabajo.

El historial de git se rehace desde cero a proposito. Arrastrar el del upstream daria a entender
que esto es su repositorio, y no lo es: es una adaptacion nuestra.
"""
import pathlib
import shutil
import subprocess
import sys

ORG = "SlimefunNewHorizons"


def sh(*args, cwd=None, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()


def origen(repo):
    """De donde vino, para acreditarlo."""
    try:
        return sh("git", "-C", str(repo), "remote", "get-url", "origin")
    except Exception:
        return "desconocido"


def licencia(repo):
    for n in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        f = repo / n
        if f.exists():
            t = f.read_text(encoding="utf-8", errors="replace")[:400].upper()
            if "GNU GENERAL PUBLIC" in t:
                return "GPL-3.0"
            if "MIT LICENSE" in t or "PERMISSION IS HEREBY GRANTED" in t:
                return "MIT"
            return "otra"
    return "sin licencia declarada"


def readme(repo, nombre, desc, items, clases, upstream, lic):
    return f"""# {nombre}

{desc}

Adaptación de DrakesCraft para **Paper/Purpur 1.21.11** y Java 21.

## Qué es

{desc}

Aporta **{items} objetos** repartidos en {clases} clases.

## Qué cambiamos

Este repositorio **no es un fork**: es el código original integrado en el ecosistema de
DrakesCraft. Los cambios son de compatibilidad, no de contenido:

- Los paquetes de Slimefun pasan de `io.github.thebusybiscuit` a `com.github.drakescraft_labs`,
  que es como está repaquetado nuestro core. Sin eso, el addon no encuentra ni una clase.
- Compila contra Java 21 y `paper-api` 1.21.1, en vez de las versiones de su época.
- Se actualizan dependencias que vivían en repositorios de Maven que ya no responden.

El paquete propio del addon y sus nombres de clase **se dejan intactos**, para que las
actualizaciones de arriba sigan siendo legibles y se pueda comparar con el original.

## Instalación

Necesita Slimefun de DrakesCraft (`Slimefun4-Drake`). Se pone el jar en `plugins/` y listo.

## Crédito

El trabajo de fondo es de los autores originales. Nosotros solo lo hemos adaptado.

- Origen: {upstream}
- Licencia: **{lic}**

La licencia original se conserva sin tocar en este repositorio. Si eres el autor y prefieres
que retiremos esta adaptación, escríbenos y se quita.
"""


def main():
    if len(sys.argv) < 3:
        print("uso: publicar.py <carpeta> <descripcion> [--crear]")
        return 1

    repo = pathlib.Path(sys.argv[1]).resolve()
    desc = sys.argv[2]
    crear = "--crear" in sys.argv
    nombre = repo.name

    java = [f for f in repo.rglob("*.java") if "/target/" not in str(f)]
    fuente = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in java)
    import re
    items = len(set(re.findall(r'"([A-Z][A-Z_0-9]{3,})"\s*,', fuente)))

    up = origen(repo)
    lic = licencia(repo)

    (repo / "README.md").write_text(
        readme(repo, nombre, desc, items, len(java), up, lic), encoding="utf-8")
    (repo / "UPSTREAM.md").write_text(
        f"""# Procedencia

Este repositorio es una adaptación a Paper/Purpur 1.21.11 de:

    {up}

Licencia original: **{lic}**, conservada sin modificar.

Los cambios de DrakesCraft son de compatibilidad (paquetes, versión de Java, dependencias).
El contenido, las mecánicas y el diseño son de sus autores.
""", encoding="utf-8")

    print(f"  {nombre}: README y UPSTREAM escritos ({items} items, {len(java)} clases, {lic})")

    if not crear:
        return 0

    shutil.rmtree(repo / ".git", ignore_errors=True)
    sh("git", "init", "-q", "-b", "main", cwd=repo)
    sh("git", "add", "-A", cwd=repo)
    sh("git", "-c", "user.name=Jack", "-c", "user.email=jackstar6677@users.noreply.github.com",
       "commit", "-q", "-m",
       f"{nombre} adaptado a 1.21.11\n\n"
       f"Codigo original de {up} ({lic}), integrado en el ecosistema DrakesCraft.\n"
       f"Los cambios son de compatibilidad: paquetes de Slimefun a com.github.drakescraft_labs,\n"
       f"Java 21, y dependencias que vivian en repos de Maven ya caidos.\n\n"
       f"Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>", cwd=repo)

    try:
        sh("gh", "repo", "create", f"{ORG}/{nombre}", "--public",
           "--description", f"{desc} — adaptado a 1.21.11 por DrakesCraft",
           "--source", str(repo), "--push")
        print(f"  publicado: https://github.com/{ORG}/{nombre}")
    except RuntimeError as e:
        print(f"  no se pudo publicar: {str(e)[:120]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
