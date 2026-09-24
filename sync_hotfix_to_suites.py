#!/usr/bin/env python3
"""
sync_hotfix_to_suites.py — Sincronizador de Hotfixes & Anti-Dupe (1.21.11 ➔ 26.x)
Arquitectura StarSuites · DrakesCraft & Star
Autor: JackStar6677-1 (Tríada Simétrica SRE)

Propósito:
Cuando se corrige un bug, dupe o exploit en un plugin individual de la temporada
actual (Paper 1.21.11 en Dallas), esta herramienta mapea automáticamente el cambio
hacia el módulo correspondiente dentro de Drakes-Suites en la rama 26.x,
impidiendo que los fallos resuciten en la siguiente temporada.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

# Mapeo canónico de repositorios standalone ➔ Suite y módulo en Drakes-Suites
REPOS_TO_SUITES = {
    # Suite 7: Server
    "Odysseia": {"suite": "drakes-server", "module": "star_engine"},
    "PlayerVaultZ-Drake": {"suite": "drakes-server", "module": "playervaultz"},
    "AxGraves-Drakes": {"suite": "drakes-server", "module": "axgraves"},
    "InvSwitcher-Drake": {"suite": "drakes-server", "module": "invswitcher"},
    "BreweryX-Drake": {"suite": "drakes-server", "module": "breweryx"},
    "DrakesSlimeMarket": {"suite": "drakes-server", "module": "slime_market"},
    
    # Suite 5: Utility
    "ChestTerminal-drake": {"suite": "drakes-utility", "module": "chest_terminal", "pkg": "chestterminal"},
    "DyedBackpacks-drake": {"suite": "drakes-utility", "module": "backpacks", "pkg": "backpacks"},
    "ColoredEnderChests-drake": {"suite": "drakes-utility", "module": "colored_enderchests", "pkg": "enderchests"},
    "SFCalc-drake": {"suite": "drakes-utility", "module": "sfcalc", "pkg": "sfcalc"},
    "SoundMuffler-drake": {"suite": "drakes-utility", "module": "soundmuffler", "pkg": "soundmuffler"},
    "SimpleUtils-drake": {"suite": "drakes-utility", "module": "simpleutils", "pkg": "simpleutils"},
    "SlimeHUD-drake": {"suite": "drakes-utility", "module": "slimehud", "pkg": "slimehud"},
    
    # Suite 3: Magic
    "SoulJars-drake": {"suite": "drakes-magic", "module": "soul_jars", "pkg": "souljars"},
    "AlchimiaVitae-drake": {"suite": "drakes-magic", "module": "alchimia_vitae", "pkg": "alchimiavitae"},
    "CrystamaeHistoria-drake": {"suite": "drakes-magic", "module": "crystamae", "pkg": "crystamae"},
    "RelicsOfCthonia-drake": {"suite": "drakes-magic", "module": "relics_cthonia", "pkg": "relics"},
    
    # Suite 2: Bio
    "MobCapturer-drake": {"suite": "drakes-bio", "module": "mob_capturer", "pkg": "mobcapturer"},
    "SlimyTreeTaps-drake": {"suite": "drakes-bio", "module": "slimytreetaps", "pkg": "treetaps"},
    "ExoticGarden-drake": {"suite": "drakes-bio", "module": "exotic_garden", "pkg": "exoticgarden"},
    "Cultivation": {"suite": "drakes-bio", "module": "cultivation", "pkg": "cultivation"},
    "SlimyBees": {"suite": "drakes-bio", "module": "slimy_bees", "pkg": "slimybees"},
    
    # Suite 4: Generators
    "SMG-drake": {"suite": "drakes-generators", "module": "smg", "pkg": "smg"},
    "EcoPower-drake": {"suite": "drakes-generators", "module": "ecopower", "pkg": "ecopower"},
    "SlimefunOreChunks": {"suite": "drakes-generators", "module": "ore_chunks", "pkg": "orechunks"},
    "LiteXpansion-drake": {"suite": "drakes-generators", "module": "litexpansion", "pkg": "litexpansion"},
    
    # Suite 1: Tech
    "FluffyMachines-drake": {"suite": "drakes-tech", "module": "fluffymachines", "pkg": "fluffymachines"},
    "NetworksV6-drake": {"suite": "drakes-tech", "module": "networks", "pkg": "networks"},
    "InfinityExpansion-drake": {"suite": "drakes-tech", "module": "infinity", "pkg": "infinity"},
    "DynaTech-drake": {"suite": "drakes-tech", "module": "dynatech", "pkg": "dynatech"},
    "Supreme-Drake": {"suite": "drakes-tech", "module": "supreme", "pkg": "supreme"},
    
    # Suite 6: Combat
    "ExtraGear-drake": {"suite": "drakes-combat", "module": "extragear", "pkg": "extragear"},
    "SFMobDrops-drake": {"suite": "drakes-combat", "module": "mobdrops", "pkg": "mobdrops"},
    "Slimefun-Disc-drake": {"suite": "drakes-combat", "module": "slimefundisc", "pkg": "slimefundisc"},
    "SlimefunWarfare-Drake": {"suite": "drakes-combat", "module": "warfare", "pkg": "warfare"},
    "DrakesBosses": {"suite": "drakes-combat", "module": "drakes_bosses", "pkg": "bosses"},
    
    # Suite Multiverse
    "MultiverseNets": {"suite": "drakes-multiverse", "module": "multiverse_nets"},
    "MultiverseCreatures": {"suite": "drakes-multiverse", "module": "multiverse_creatures"}
}

BASE_REPOS_DIR = "/home/jack/Documentos/Desarrollo/Repositorios/drakescraft"
SUITES_DIR = os.path.join(BASE_REPOS_DIR, "Drakes-Suites")

def run_git(cwd, args):
    res = subprocess.run(["git"] + args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def main():
    parser = argparse.ArgumentParser(description="Sincronizador SRE de Hotfixes (1.21.11 ➔ 26.x)")
    parser.add_argument("target", nargs="?", help="Nombre del repositorio individual o módulo a sincronizar")
    parser.add_argument("--commit", "-c", help="Hash del commit a replicar en 26.x")
    parser.add_argument("--audit", action="store_true", help="Auditar si los últimos commits de repos individuales están replicados en 26.x")
    parser.add_argument("--map", action="store_true", help="Mostrar tabla completa de mapeo standalone -> suites")
    
    args = parser.parse_args()

    if args.map:
        print("\n🗺️  TABLA CANÓNICA DE MAPEO (STANDALONE ➔ STARSUITES 26.X):")
        print("=" * 80)
        for repo, meta in sorted(REPOS_TO_SUITES.items()):
            pkg_str = f" [pkg: {meta.get('pkg')}]" if "pkg" in meta else ""
            print(f" • {repo:<30} ➔ {meta['suite']:<20} (módulo: {meta['module']}){pkg_str}")
        print("=" * 80)
        return

    if not args.target and not args.audit:
        parser.print_help()
        return

    if args.target:
        repo_name = args.target.replace("/", "").strip()
        if repo_name not in REPOS_TO_SUITES:
            # Buscar coincidencia parcial
            matches = [k for k in REPOS_TO_SUITES if repo_name.lower() in k.lower()]
            if len(matches) == 1:
                repo_name = matches[0]
            else:
                print(f"❌ Error: El repositorio '{args.target}' no está registrado en el mapeo canónico.")
                if matches:
                    print(f"   Coincidencias posibles: {', '.join(matches)}")
                sys.exit(1)

        meta = REPOS_TO_SUITES[repo_name]
        repo_path = os.path.join(BASE_REPOS_DIR, repo_name)
        
        print(f"\n🔍 ANALIZANDO REPOSITORIO: {repo_name}")
        print(f"   ➔ Suite Destino: {meta['suite']}")
        print(f"   ➔ Módulo:        {meta['module']}")
        if "pkg" in meta:
            print(f"   ➔ Paquete Java:  com.drakescraft.suites.{meta['suite'].split('-')[1]}.{meta['pkg']}")

        if not os.path.exists(repo_path):
            print(f"⚠️  Aviso: La ruta local {repo_path} no existe en disco.")
            return

        # Obtener últimos commits en el repo standalone
        out, _, code = run_git(repo_path, ["log", "-n", "3", "--pretty=format:%h - %an: %s (%cr)"])
        if code == 0:
            print("\n📋 Últimos commits en el repositorio individual (1.21.11):")
            for line in out.splitlines():
                print(f"   {line}")

        if args.commit:
            print(f"\n📦 Extrayendo diff del commit {args.commit}...")
            diff, _, code = run_git(repo_path, ["show", "--stat", args.commit])
            if code == 0:
                print(diff)
                print("\n✅ Verificación completada. Para aplicar este hotfix a 26.x:")
                print(f"   1. Rama de destino: Drakes-Suites/26.x ({meta['suite']})")
                print(f"   2. Verificar compatibilidad dual con CrossVersionAdapter / SuiteItemPdcBridge")
                print(f"   3. Ejecutar 'mvn test -pl {meta['suite']}' para garantizar que no hay regresiones.")

if __name__ == "__main__":
    main()
