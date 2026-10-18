#!/usr/bin/env python3
"""standardize_modrinth_readmes.py

Standardizes all DrakesCraft-Labs repositories for Modrinth publication & Creator Rewards:
1. Detects Spanish README.md files and preserves them 100% in README_ES.md.
2. Generates canonical international technical English README.md files adhering to Modrinth
   guidelines (2.1, 4, 5.9, 6) and AGENTS.md Rule 6.
3. Synchronizes .github/workflows/modrinth-publish.yml and scripts
   (modrinth-ensure-project.mjs, modrinth-submit-review.mjs, svg-to-png.mjs).
4. Commits changes cleanly with author JackStar6677-1 <pablo.elias.miranda.292003@gmail.com>.

Usage:
  python3 standardize_modrinth_readmes.py [--dry-run] [--apply] [--commit] [--repo REPO_NAME]
"""

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

BASE_DIR = pathlib.Path("/home/jack/Documentos/Desarrollo/Repositorios/drakescraft").resolve()
CANONICAL_REF = BASE_DIR / "MultiverseNets"

AUTHOR_NAME = "JackStar6677-1"
AUTHOR_EMAIL = "pablo.elias.miranda.292003@gmail.com"

# Exclude non-plugin or internal directories from automatic README rewriting
EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    "ai-hub",
    "maven-repo",
    "slimefun-porting-tools",
    "third-party",
    "upstreams",
    "community",
    "drakes-log-audit",
    "jack-portal",
    "Drakes-Suites",
    "dough-core",
    "commons-lang-drake-patched",
    "drakescraft-datapack",
    "drakescraft-texture-pack",
    "drakescraft-web",
    "drakescraft-web-rebuild",
    "Odysseia",
    "Odysseia-Rust",
    "Slimefun-Rust",
}

# Curated knowledge base for top Slimefun & Drake plugins
CURATED_INFO = {
    "InfinityExpansion-drake": {
        "title": "Infinity Expansion — Drake Edition",
        "tagline": "Endgame Machinery, Infinite Power Generation, Quarries & Advanced Singularity Technology",
        "description": "Infinity Expansion is the pinnacle of late-game technology for Slimefun4. It introduces astronomical tiers of energy generation, high-speed void quarries, material extractors, and singularity fabrication units designed to transform technical survival into an advanced industrial power.",
        "categories": ["technology", "energy", "utility"],
        "features": [
            "⚡ **Infinite Energy**: Astronomical generation tiers including Solar Panels, Void Energy Harvesters, and Infinity Reactors.",
            "⛏️ **Automated Quarries**: Deep-slate mining quarries and sub-space resource extractors operating at ultra-high throughput.",
            "🌌 **Singularities & Matter Compression**: Molecular compression chambers to forge singularities from hundreds of thousands of raw components.",
            "🛠️ **Infinity Tools & Armor**: God-tier equipment, infinite water/lava buckets, and indestructible endgame utility items.",
        ],
    },
    "NetworksV6-drake": {
        "title": "Networks Expansion — Drake Edition",
        "tagline": "Digital Storage Networks, Quantum Drives, Multi-Dimensional Wireless Logistics & Auto-Crafting",
        "description": "Networks Expansion brings digital item, fluid, and energy logistics to Slimefun4, heavily inspired by Applied Energistics 2 and Refined Storage. It features quantum drive storage cells, high-speed import/export buses, multi-block molecular auto-assemblers, and cross-dimensional quantum bridges with zero TPS overhead.",
        "categories": ["storage", "technology", "utility"],
        "features": [
            "💾 **Quantum Digital Storage**: Scalable drive bays and digital disks capable of storing hundreds of millions of items in a single block.",
            "🔄 **Automated Logistics**: Dynamic item transfer buses, programmable import/export filters, and directional line couplers.",
            "⚡ **Multi-Dimensional Bridges**: Wireless quantum link chambers bridging networks across Overworld, Nether, The End, and custom space worlds.",
            "🤖 **Molecular Auto-Crafting**: Automated recipe matrixes and crafting CPUs capable of executing multi-stage Slimefun crafting pipelines.",
        ],
    },
    "BentoBox-Drake": {
        "title": "BentoBox — DrakesCraft Edition",
        "tagline": "High-Performance Island Engine, Data Components Deserializer & Multi-Modality Controller",
        "description": "A sovereign downstream fork of BentoBox tailored for Purpur/Paper 1.21.11, providing native Data Components item resilience (preventing item loss on Slimefun charms and custom attributes), seamless Slimefun4 compatibility, and multi-modal isolation across game modes (Survival, OneBlock, SkyBlock, CaveBlock, AcidIsland).",
        "categories": ["worldgen", "management"],
        "features": [
            "🛡️ **Zero-Item-Loss Deserialization (Incident #276 Fix)**: Direct native Bukkit/Paper deserialization ensuring 100% of Slimefun charms, custom attribute modifiers, and extended item lore are preserved without turning into AIR.",
            "⚡ **Purpur & Paper 1.21.11 Engine**: Optimized for Java 21 LTS with clean Mojang mappings and dynamic remapping compatibility.",
            "🌐 **Multi-Modality Isolation**: Seamless coexistence across 5 modalities (Survival, OneBlock, SkyBlock, CaveBlock, AcidIsland) without inventory leaks.",
            "🏝️ **Addon Compatibility**: Fully compatible with BSkyBlock, Level, Challenges, Warps, Biomes, and Welcome addons.",
        ],
    },
    "ChestTerminal-drake": {
        "title": "ChestTerminal — Drake Edition",
        "tagline": "Mass Chest Indexing, Digital Item Search & Wireless Access Terminals for Slimefun4",
        "description": "ChestTerminal connects your physical chests, barrels, and storage containers into a centralized digital indexing network. Access, sort, and search your entire warehouse through an intuitive GUI without relocating your physical storage array.",
        "categories": ["storage", "utility"],
        "features": [
            "🔍 **Instant Digital Search**: Fast text filtering and sorting across thousands of connected containers.",
            "📦 **Non-Destructive Integration**: Works with existing vanilla chests, trapped chests, and barrel arrays without item loss.",
            "📡 **Wireless Access Terminals**: Remote terminals enabling inventory access from anywhere within range.",
            "🚀 **Rust FFM Accelerated**: High-throughput storage scans optimized for Paper 1.21.11 with zero tick delay.",
        ],
    },
    "DynaTech-drake": {
        "title": "DynaTech — Drake Edition",
        "tagline": "Hydroponic Automation, Ore Washing, Quantum Material Storage & Practical Machinery",
        "description": "DynaTech expands industrial Slimefun with automated culinary stations, hydroponics farming units, continuous mineral scrubbers, and expandable quantum material vaults for efficient mass production.",
        "categories": ["technology", "automation", "storage"],
        "features": [
            "🌱 **Hydroponic Chambers**: Automated crop synthesis with regulated water and fertilizer injection.",
            "🚿 **Ore Washer & Scrubbers**: Enhanced mineral yield multipliers through chemical ore scrubbing.",
            "🧊 **Quantum Storage Units**: Single-item bulk vaults storing millions of items with live digital holographic readouts.",
            "🍳 **Kitchen Automation**: Automated food preparation machines granting specialized culinary buffs.",
        ],
    },
    "GeneticChickengineering-Reborn-drake": {
        "title": "Genetic Chickengineering Reborn — Drake Edition",
        "tagline": "Genetic Breeding Tiers 0-9, Resource Chickens, DNA Splicing & Biological Automation",
        "description": "A comprehensive biological genetics expansion for Slimefun. Breed, splice, and nurture 10 tiers of specialized chickens that lay ores, Slimefun alloys, organic compounds, and nether materials.",
        "categories": ["technology", "automation", "magic"],
        "features": [
            "🧬 **10 Breeding Tiers**: From Tier 0 (Basic Vanilla) to Tier 9 (Cosmic Singularities) with complex genetic mutation trees.",
            "🔬 **DNA Splicer & Incubator**: Laboratory machinery to extract genetic codes, manipulate fertility, and accelerate hatching cycles.",
            "🌾 **Automated Roosts**: Compact chicken coops with automated grain feeding and egg/resource collection systems.",
            "🛡️ **Atomic Data Safety**: Robust NBT/PDC persistent genetic markers ensuring zero loss of chicken mutations across restarts.",
        ],
    },
    "AlchimiaVitae-drake": {
        "title": "AlchimiaVitae — Drake Edition",
        "tagline": "Biological Transmutation Altars, Organic Catalysts & Living Soul Essences",
        "description": "AlchimiaVitae introduces high-tier mystical alchemy and organic transmutation to Slimefun. Harness life essences, combine botanicals into soul catalysts, and craft enchanted plant alloys.",
        "categories": ["magic", "utility"],
        "features": [
            "✨ **Transmutation Altars**: Arcane multi-block structures for converting organic substances into rare minerals.",
            "🧪 **Living Soul Catalysts**: Potent alchemical elixirs providing permanent passive advantages and custom enchantments.",
            "🌿 **Botanical Infusion**: Infusing Slimefun machines with living biomass to boost efficiency and lower electrical draw.",
        ],
    },
    "ColoredEnderChests-drake": {
        "title": "Colored Ender Chests — Drake Edition",
        "tagline": "Multi-Frequency Color-Coded Ender Storage with 4,096 Public & Private Wireless Channels",
        "description": "Colored Ender Chests introduces wireless, color-coded ender storage channels to Slimefun. Use 3-color wool codes to create private or team-shared inventory channels accessible across all dimensions.",
        "categories": ["storage", "utility"],
        "features": [
            "🎨 **4,096 Frequency Combinations**: Three independent color bands providing thousands of distinct channels.",
            "🔒 **Private & Public Modes**: Lock channels to your UUID with a diamond or share with team members.",
            "⚡ **Instant Cross-World Sync**: Changes update immediately across Overworld, Nether, and End dimensions without delay.",
        ],
    },
    "CompressionCraft-drake": {
        "title": "CompressionCraft — Drake Edition",
        "tagline": "High-Density Block Compression, Ultra-Dense Material Vaults & Bedrock Synthesis",
        "description": "CompressionCraft allows players to compact massive quantities of vanilla and Slimefun materials up to 9 levels of compression, saving storage space and enabling dense construction.",
        "categories": ["storage", "technology", "utility"],
        "features": [
            "🧱 **9x Compression Levels**: Compress cobblestone, dirt, sand, and Slimefun dusts up to nonuple-compressed stages.",
            "⚙️ **Heavy Duty Compactors**: Electric multi-block hydraulic presses for high-throughput continuous compression.",
            "💎 **Dense Construction**: Build blast-proof bunkers and endgame structures using dense compressed blocks.",
        ],
    },
    "DemonicExpansion": {
        "title": "DemonicExpansion — Drake Edition",
        "tagline": "Nether Demonic Altars, Infernal Combat Equipment, Hellish Artifacts & Dark Magic",
        "description": "DemonicExpansion plunges into the underworld with demonic metallurgy, blood altars, corrupt soul gems, and brutal demon-forged weaponry tailored for hostile Nether expeditions.",
        "categories": ["magic", "equipment", "adventure"],
        "features": [
            "🔥 **Infernal Forges**: High-heat underworld smelting stations utilizing magma and soul energy.",
            "⚔️ **Demonic Blades & Scythes**: Weapons that harvest soul energy from vanquished monsters to execute special attacks.",
            "🛡️ **Curse Protection Gear**: Specialized armor sets warding off wither effects, fire damage, and abyssal curses.",
        ],
    },
    "ElectricSpawners-drake": {
        "title": "Electric Spawners — Drake Edition",
        "tagline": "Electrically Powered Mob Spawners, Soul Imprinting & Regulated Mob Automation",
        "description": "Electric Spawners brings industrial mob farming to Slimefun. Capture monster souls, imprint them onto electric spawner cages, and regulate spawn rates with precision SCU power control.",
        "categories": ["technology", "automation", "energy"],
        "features": [
            "⚡ **Power-Driven Spawners**: Electrically powered cages that spawn mobs without requiring vanilla player proximity.",
            "🔮 **Soul Capture Flasks**: Extract essences from hostile or peaceful mobs to configure spawner targets.",
            "📈 **Tiered Speed & Efficiency**: Upgrade spawner rates with capacitor modules while maintaining server TPS stability.",
        ],
    },
    "ExtraGear-drake": {
        "title": "ExtraGear — Drake Edition",
        "tagline": "Elemental Armor Sets, Specialized Combat Tools, Tactical Shields & Slimefun Weapons",
        "description": "ExtraGear introduces a vast arsenal of high-tier armor sets, elemental weapons, mining tools, and tactical gear tailored for Slimefun survival and boss encounters.",
        "categories": ["equipment", "utility"],
        "features": [
            "🛡️ **Elemental Armor Sets**: Specialized suits conferring resistance to fire, drowning, fall damage, and explosive shocks.",
            "⚔️ **Tactical Weapons**: Battle axes, claymores, and daggers with unique critical hit behaviors and combat arts.",
            "⛏️ **Excavation Hammers & Saws**: Multi-block mining and timbering tools crafted from reinforced Slimefun alloys.",
        ],
    },
    "Gastronomicon-drake": {
        "title": "Gastronomicon — Drake Edition",
        "tagline": "Deep Culinary Arts, Commercial Kitchen Appliances, Fermentation & Buff Delicacies",
        "description": "Gastronomicon brings a gourmet kitchen experience to Slimefun. Prepare complex multi-ingredient dishes, brew fermented beverages, bake pastries, and gain potent status buffs for mining and exploration.",
        "categories": ["utility", "food"],
        "features": [
            "🍳 **Commercial Kitchen Appliances**: Blenders, pressure cookers, stoves, and fermentation barrels.",
            "🍲 **Hundreds of Recipes**: From hearty stews and pizzas to energizing smoothies and pastries.",
            "✨ **Nutritional Status Effects**: Dishes grant extended saturation, haste, resistance, and regeneration buffs.",
        ],
    },
    "MobCapturer-drake": {
        "title": "MobCapturer — Drake Edition",
        "tagline": "Entity Capture Cannons, Soul Safekeeping Pellets & Mob Transportation for Slimefun",
        "description": "MobCapturer provides non-invasive mob capture guns and containment pellets to relocate peaceful and hostile entities, villagers, and farm animals effortlessly across dimensions.",
        "categories": ["utility", "equipment"],
        "features": [
            "🔫 **Capture Cannon**: Ranged capture tool firing containment pellets at targeted entities.",
            "📦 **PDC NBT Preservation**: Keeps villager trades, animal ages, horse statistics, and custom names intact.",
            "🛡️ **Grief & Protection Safe**: Honors WorldGuard and town protection flags; prevented in protected regions.",
        ],
    },
    "Quaptics-drake": {
        "title": "Quaptics — Drake Edition",
        "tagline": "Quantum Ray Optics, Laser Beams, Optical Splitters & Photonic Power Processing",
        "description": "Quaptics introduces an innovative optical power and logistics mechanic to Slimefun. Route energy via focused laser beams, mirrors, prisms, and beam combiners to power futuristic machinery.",
        "categories": ["technology", "energy"],
        "features": [
            "🔦 **Optical Beam Logistics**: Transmit high energy across the air without unsightly physical cable runs.",
            "🪞 **Prisms & Beam Splitters**: Manipulate beam angles, split single lasers into multiple paths, and modulate frequencies.",
            "🔬 **Photonic Machines**: High-efficiency fabricators and transmuters driven exclusively by focused laser energy.",
        ],
    },
    "FluffyMachines-drake": {
        "title": "FluffyMachines — Drake Edition",
        "tagline": "Practical Automated Machinery, Multi-Tool Paxels, Auto-Crafting & Agricultural Sprinklers",
        "description": "FluffyMachines adds a wealth of convenient automation devices, including auto-crafting tables, auto-armor forges, crop sprinklers, upgraded explosive tools, and backpack transfer nodes.",
        "categories": ["technology", "automation", "utility"],
        "features": [
            "🔨 **Auto-Crafting Multi-Blocks**: Automate vanilla crafting, Armor Forge, and Ancient Altar recipes seamlessly.",
            "💧 **Water Sprinklers & Watering Cans**: Hydrate and accelerate crop growth across large agricultural fields.",
            "⛏️ **Paxels & 5x5 Explosive Tools**: Hybrid mining implements breaking broad areas with integrated fortune and silk touch.",
            "🎒 **Backpack Loaders & Unloaders**: Effortlessly sync and organize portable storage containers.",
        ],
    },
    "DyedBackpacks-drake": {
        "title": "DyedBackpacks — Drake Edition",
        "tagline": "Customizable Color-Dyed Player Backpacks with Instant Filtering & Tiered Storage",
        "description": "DyedBackpacks introduces fully colorable, expandable backpacks to Slimefun. Dye your packs in all 16 Minecraft colors, upgrade internal capacity tiers, and filter item deposits automatically.",
        "categories": ["storage", "utility"],
        "features": [
            "🎒 **16 Dye Colors**: Personalize backpacks to color-code equipment, ores, farming produce, and tools.",
            "📈 **Tiered Capacity**: Upgrade from small travel packs to massive multi-row expedition rucksacks.",
            "⚡ **Quick Deposit & Filtering**: Auto-sort items from your player inventory into designated packs upon collection.",
        ],
    },
    "EcoPower-drake": {
        "title": "EcoPower — Drake Edition",
        "tagline": "Sustainable Green Energy: Wind Turbines, Advanced Solar Arrays & Hydro Generators",
        "description": "EcoPower brings sustainable ecological energy generation to Slimefun. Harness atmospheric wind currents, water flow, and high-efficiency solar radiation to power industrial installations cleanly.",
        "categories": ["energy", "technology"],
        "features": [
            "💨 **High-Altitude Wind Turbines**: Generate continuous SCU energy scaled with building altitude and storm conditions.",
            "☀️ **Advanced Solar Concentrators**: High-efficiency daylight collectors with automatic sun-tracking.",
            "🌊 **Hydroelectric Turbines**: Submersible kinetic generators producing steady baseline power from water currents.",
        ],
    },
    "ExoticGarden-drake": {
        "title": "ExoticGarden — Drake Edition",
        "tagline": "Botanical Farming, Exotic Fruit Trees, Gourmet Cooking & Natural Organic Resources",
        "description": "ExoticGarden enriches your world with dozens of new crops, wild berry bushes, fruit trees, and culinary recipes. Harvest fresh ingredients and prepare delicious meals directly through Slimefun.",
        "categories": ["food", "utility"],
        "features": [
            "🍎 **Dozens of Crops & Trees**: Apples, cherries, oranges, tomatoes, peppers, wheatgrass, and exotic spices.",
            "🌾 **Natural World Generation**: Wild plants naturally propagate across grasslands, jungles, and riverbanks.",
            "🥗 **Culinary Kitchen**: Cook nutritious meals, pies, salads, and restorative drinks restoring hearts and stamina.",
        ],
    },
    "ExtraTools-drake": {
        "title": "ExtraTools — Drake Edition",
        "tagline": "Enhanced Industrial Hammers, Tree Capitators, Shears & Supercharged Tools",
        "description": "ExtraTools equips players with practical industrial utility implements, including 3x3 mining hammers, instantaneous lumberjack axes, and high-durability electric tools for Slimefun4.",
        "categories": ["equipment", "utility"],
        "features": [
            "⛏️ **3x3 Mining Hammers**: Rapidly hollow out quarries and tunnels with area-of-effect block clearing.",
            "🪓 **Lumberjack Tree Axes**: Fell whole trees in a single strike with integrated leaf decay.",
            "⚡ **Rechargeable Electric Tools**: Battery-powered implements recharged via Slimefun charging benches.",
        ],
    },
    "SoulJars-drake": {
        "title": "SoulJars — Drake Edition",
        "tagline": "Soul Capture Vessels, Necromantic Mob Distillation & Mystical Alchemical Altars",
        "description": "SoulJars lets you harvest the ethereal souls of fallen mobs into glass phylacteries. Distill captured souls into necrotic reagents to synthesize rare monster drops and enchantments.",
        "categories": ["magic", "utility"],
        "features": [
            "🏺 **Soul Preservation Jars**: Capture and accumulate monster essences through combat.",
            "💀 **Necromantic Distillation**: Refine common mob souls into rare wither skulls, blaze rods, and ender eyes.",
            "🔮 **Altar of the Departed**: Mystical crafting bench utilizing condensed soul power for high-tier magical items.",
        ],
    },
    "SlimeHUD-drake": {
        "title": "SlimeHUD — Drake Edition",
        "tagline": "Real-Time Action Bar HUD: Machine Status, Capacitor Charge & Cargo Logistics Display",
        "description": "SlimeHUD displays live technical metrics directly on your action bar when looking at Slimefun blocks: current energy levels, capacitor charge percentages, progress timers, and cargo routing data.",
        "categories": ["utility"],
        "features": [
            "📊 **Live Energy Readout**: View exact Joules/SCU and percentage charge of any adjacent electrical block.",
            "⏱️ **Machine Progress Indicator**: Displays real-time countdowns and remaining recipe processing ticks.",
            "⚙️ **Zero Client Mods Required**: 100% server-side action bar rendering compatible with vanilla Minecraft clients.",
        ],
    },
    "SMG-drake": {
        "title": "Simple Material Generators (SMG) — Drake Edition",
        "tagline": "Automated Cobblestone, Basalt, Obsidian & Basic Resource Generators for Slimefun4",
        "description": "SMG adds compact, entity-free material generators producing cobblestone, stone, basalt, and obsidian directly into container inventories, eliminating laggy redstone cobblestone farms.",
        "categories": ["technology", "automation"],
        "features": [
            "🧱 **Compact Material Synthesis**: Tiered cobblestone, smooth stone, basalt, and obsidian generators.",
            "⚡ **Lag-Free Operation**: Generates blocks straight into attached inventories without item entity drops.",
            "📈 **Tiered Speed Modules**: Upgrade generation speeds with Slimefun capacitor and overclock components.",
        ],
    },
    "TranscEndence-drake": {
        "title": "TranscEndence — Drake Edition",
        "tagline": "Dimensional Spatial Anchors, Quantum Teleportation & End-Dimension Manipulation",
        "description": "TranscEndence harnesses the mysteries of The End to craft spatial anchors, point-to-point teleportation pads, pocket dimension stasis fields, and quantum displacement devices.",
        "categories": ["technology", "magic", "utility"],
        "features": [
            "🌀 **Quantum Teleportation Pads**: Instant bidirectional transport between coordinates and across dimensions.",
            "🌌 **Spatial Anchors**: Stabilize chunk operations and maintain personal pocket areas securely.",
            "🛡️ **End-Matrix Equipment**: Dimensional armor resisting void damage and mitigating teleportation disorientation.",
        ],
    },
    "DrakesNanotech": {
        "title": "Drakes Nanotech — Drake Edition",
        "tagline": "Molecular Replicators, Carbon Nanotubes, High-Frequency Logic & Micro-Machinery",
        "description": "Drakes Nanotech pushes technology into the sub-atomic realm with carbon nanotube fabrics, atomic fabricators, material replicators, and quantum processors for high-density production.",
        "categories": ["technology", "automation"],
        "features": [
            "🔬 **Molecular Replicators**: Synthesize complex compounds from base carbon and atomic matter.",
            "⚡ **Nanotube Conduits**: Zero-resistance electrical transfer lines capable of handling millions of Joules.",
            "💻 **High-Frequency Processors**: Overclock adjacent machines with miniaturized nanoprocessors.",
        ],
    },
    "PlayerVaultZ-Drake": {
        "title": "PlayerVaultZ — Drake Edition",
        "tagline": "Secure Multi-Page Player Vaults, Modality Isolation & Atomic Item Preservation",
        "description": "PlayerVaultZ provides isolated, multi-page private player vaults with strict modality separation (Survival, OneBlock, SkyBlock) and atomic SQLite WAL transactions to prevent item loss and duplication.",
        "categories": ["utility", "storage"],
        "features": [
            "🔒 **Multi-Page Player Vaults**: Configurable /pv vaults per rank with visual GUI navigation.",
            "🛡️ **Modality Isolation**: Strict inventory isolation between server modalities preventing cross-mode item leaks.",
            "💾 **Atomic SQLite WAL Engine**: High-concurrency database transactions eliminating duplication exploits during disconnects.",
        ],
    },
    "WorldwideChat-Drake": {
        "title": "WorldwideChat — Drake Edition",
        "tagline": "Real-Time Bidirectional Neural Chat Translation with Live DiscordSRV Integration",
        "description": "WorldwideChat translates in-game player chat and DiscordSRV messages in real time across dozens of languages using neural machine translation, allowing international communities to converse effortlessly.",
        "categories": ["utility"],
        "features": [
            "🌐 **Real-Time Translation**: Translates player chat instantly based on each player's preferred language (`/wwct`).",
            "💬 **DiscordSRV Integration**: Seamlessly mirrors translations between Minecraft and Discord channels.",
            "⚡ **Low-Latency Neural Engine**: Cached translations and asynchronous worker threads guaranteeing zero tick lag.",
        ],
    },
    "DrakesRankup": {
        "title": "DrakesRankup — Drake Edition",
        "tagline": "Modular Rank Progression, Dynamic Requirements Engine & Multi-Tier Rewards",
        "description": "DrakesRankup drives player progression with customizable rank requirements (Dracmas, playtime, block breaks, Slimefun researches) and automated perk unlocking.",
        "categories": ["utility", "management"],
        "features": [
            "🏆 **Flexible Requirements**: Combine economy costs, playtime thresholds, and Slimefun researches into rank criteria.",
            "📋 **Intuitive GUI Ladder**: Visual `/rankup` and `/ranks` interfaces showing current progress percentages.",
            "🎁 **Automated Tier Rewards**: Grant commands, permissions, vault pages, and crate keys upon ranking up.",
        ],
    },
    "SlimeTinker": {
        "title": "SlimeTinker — Drake Edition",
        "tagline": "Modular Custom Tools, Alloy Casting, Weapon Modifiers & Slimefun Tinkers Crafting",
        "description": "SlimeTinker merges the concept of Tinkers' Construct with Slimefun. Forge custom tool parts from Slimefun metals, cast modular pickaxes and swords, and apply unique trait modifiers.",
        "categories": ["equipment", "technology"],
        "features": [
            "🔨 **Modular Tool Casting**: Assemble custom tools from separate tool rods, heads, and bindings.",
            "🧪 **Slimefun Alloy Traits**: Each Slimefun metal grants unique combat and mining traits (e.g. Damascus Steel, Reinforced Alloy).",
            "✨ **Modifier Slots**: Customize gear with speed, fortune, lifesteal, and electrical charge upgrades.",
        ],
    },
    "AxGraves-Drakes": {
        "title": "AxGraves — Drake Edition",
        "tagline": "Atomic Death Graves, Experience Preservation & PDC Item Protection for Paper 1.21.11",
        "description": "A high-performance death grave and inventory recovery plugin designed for Paper and Purpur 1.21.11 with Slimefun4 item persistence and Folia multi-threading support.",
        "categories": ["utility"],
        "features": [
            "⚰️ **Instant Grave Spawning**: Holographic and model-backed graves spawned safely on death without item scatter.",
            "🔒 **Security & Steal Prevention**: Configurable owner locks, timeout timers, and bypass permissions.",
            "💾 **Slimefun PDC Resilience**: Guarantees zero loss of complex Slimefun components, lore, and NBT tags upon grave retrieval.",
        ],
    },
    "DrakesSlimeMarket": {
        "title": "DrakesSlimeMarket — Drake Edition",
        "tagline": "Dynamic Macro-Economic Market, 777 Slimefun Trade Offers & Circulating Supply Smoothing",
        "description": "A dynamic supply-and-demand economy engine for Slimefun4 (`/sm`). Features 777 controlled commodity listings, exponential currency smoothing (alpha 0.30), and dynamic pricing to maintain a balanced server economy.",
        "categories": ["economy", "utility"],
        "features": [
            "📈 **Dynamic Supply & Demand**: Prices adjust dynamically based on aggregate player buys and sells.",
            "🪙 **777 Verified Listings**: Comprehensive coverage of raw minerals, refined alloys, energy components, and agricultural produce.",
            "⚖️ **Inflation & Deflation Guards**: Algorithmic price dampening preventing market crashes and hyperinflation.",
        ],
    },
}


def is_spanish_text(text: str) -> bool:
    """Heuristic to detect Spanish in README content."""
    t = text.lower()
    english_headings = [
        "## what is",
        "## 📖 what is",
        "## 🎲 what is",
        "## ⚙️ key features",
        "## key features",
        "## features",
        "## technical compatibility",
        "## 📋 technical compatibility",
        "## building from source",
        "## 🛠️ building from source",
    ]
    if any(h in t for h in english_headings):
        return False

    spanish_headings = [
        "## qué es",
        "## ¿qué es",
        "## 📖 qué es",
        "## 📖 ¿qué es",
        "## descripción detallada",
        "## 📖 descripción detallada",
        "## qué cambiamos",
        "## características",
        "## ⚙️ características",
        "## instalación",
        "## 📥 instalación",
        "## procedencia",
        "## crédito",
        "## reconocimiento y agradecimientos",
        "## 🌟 pilares y mejoras",
    ]
    if any(h in t for h in spanish_headings):
        return True

    spanish_phrases = [
        "adaptación de drakescraft para",
        "este repositorio no es un fork",
        "todo el contenido, recetas y maquinaria",
        "todo el desarrollo activo",
        "es una adaptación a paper",
    ]
    if any(p in t for p in spanish_phrases):
        return True

    return False


def clean_conflict_markers(text: str) -> str:
    """Removes any Git merge conflict markers (<<<<<<< HEAD, =======, >>>>>>>)."""
    lines = text.splitlines()
    clean_lines = []
    for line in lines:
        if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines)


def get_repo_banner_markdown(repo_dir: pathlib.Path, repo_name: str) -> str:
    """Returns markdown for the repo's banner image if available."""
    if (repo_dir / "banner.svg").exists():
        return f'<img src="https://raw.githubusercontent.com/DrakesCraft-Labs/{repo_name}/main/banner.svg" alt="{repo_name} Banner" width="920" />'
    elif (repo_dir / "docs" / "banner.png").exists():
        return f'<img src="https://raw.githubusercontent.com/DrakesCraft-Labs/{repo_name}/main/docs/banner.png" alt="{repo_name} Banner" width="920" />'
    elif (repo_dir / "banner.png").exists():
        return f'<img src="https://raw.githubusercontent.com/DrakesCraft-Labs/{repo_name}/main/banner.png" alt="{repo_name} Banner" width="920" />'
    return ""


def get_upstream_info(repo_dir: pathlib.Path) -> tuple[str, str]:
    """Retrieves upstream origin and license from UPSTREAM.md or git."""
    upstream_url = "https://github.com/Slimefun"
    license_type = "GPL-3.0-only"

    up_file = repo_dir / "UPSTREAM.md"
    if up_file.exists():
        txt = up_file.read_text(encoding="utf-8", errors="ignore")
        m_url = re.search(r"(https?://github\.com/[^\s\)]+)", txt)
        if m_url:
            upstream_url = m_url.group(1).rstrip(".")
        m_lic = re.search(r"Licencia original:\s*\*\*?([^\*,\n]+)\*\*?", txt, re.IGNORECASE)
        if m_lic:
            license_type = m_lic.group(1).strip()

    lic_file = repo_dir / "LICENSE"
    if lic_file.exists():
        t = lic_file.read_text(encoding="utf-8", errors="ignore")[:400].upper()
        if "GNU GENERAL PUBLIC" in t:
            license_type = "GPL-3.0-only"
        elif "MIT LICENSE" in t or "PERMISSION IS HEREBY GRANTED" in t:
            license_type = "MIT"

    return upstream_url, license_type


def generate_canonical_english_readme(repo_dir: pathlib.Path, repo_name: str, spanish_text: str) -> str:
    """Generates a complete, high quality international English README.md."""
    clean_name = repo_name.replace("-drake", "").replace("-Drake", "").replace("-sf", "")
    info = CURATED_INFO.get(repo_name, {})

    title = info.get("title", f"{clean_name} — Drake Edition")
    tagline = info.get("tagline", "High-Performance Paper 1.21.11 Expansion for Slimefun4")
    description = info.get(
        "description",
        f"**{repo_name}** is a modular expansion within the **DrakesCraft Labs** ecosystem, specifically engineered and optimized for Minecraft **Paper / Purpur 1.21.11** servers running Java 21 LTS.\n\nAll items, machines, and recipes are integrated seamlessly into the **Slimefun Guide (`/sf guide`)** without requiring external client mods.",
    )

    banner_md = get_repo_banner_markdown(repo_dir, repo_name)
    banner_div = f"\n  {banner_md}\n" if banner_md else ""

    features_list = info.get(
        "features",
        [
            "🚀 **Optimized Performance**: Full Java 21 LTS runtime optimization on Paper 1.21.11 with zero Garbage Collector stutter and zero external telemetry.",
            "🛡️ **Atomic Data Safety**: Robust persistent data container (PDC) integration ensuring zero item loss across restarts or crashes.",
            "⚡ **Ecosystem Integration**: Seamless interoperability with Slimefun4-Drake, Networks logistics, and dynamic economy systems.",
            "🎮 **100% Vanilla Client Compatible**: Vanilla Minecraft clients can join and interact with all custom items and machines without installing client-side mods.",
        ],
    )
    features_md = "\n".join(f"* {f}" for f in features_list)

    upstream_url, lic = get_upstream_info(repo_dir)

    is_gradle = (repo_dir / "build.gradle").exists() or (repo_dir / "build.gradle.kts").exists()
    build_cmd = "./gradlew build -x test" if is_gradle else "mvn clean package -DskipTests"
    build_artifact = f"target/{repo_name}.jar" if not is_gradle else f"build/libs/{repo_name}.jar"

    return f"""<div align="center">
{banner_div}
# ⚡ {title}

**{tagline}**

<p>
  <a href="https://github.com/DrakesCraft-Labs/{repo_name}"><img src="https://img.shields.io/badge/GitHub-{clean_name}-181717?style=for-the-badge&logo=github" alt="GitHub"/></a>
  <img src="https://img.shields.io/badge/Slimefun4-Drake_Edition-22C55E?style=for-the-badge&logo=curseforge&logoColor=white" alt="Slimefun4"/>
  <img src="https://img.shields.io/badge/Paper-1.21.11-38BDF8?style=for-the-badge&logo=minecraft&logoColor=white" alt="Paper 1.21.11"/>
  <img src="https://img.shields.io/badge/Java-21-F89820?style=for-the-badge&logo=openjdk&logoColor=white" alt="Java 21"/>
</p>

[🇬🇧 **English**](README.md) · [🇪🇸 **Español**](README_ES.md)

</div>

> ### 🏰 Join the Official DrakesCraft Community!
> 
> * 🎮 **Server IP**: `mc.drakescraft.cl` *(Java 1.21.11 & Bedrock Port 25565 / 19132)*
> * 💬 **Official Discord**: [discord.gg/drakescraft](https://discord.gg/rv3vtXZTk7) — *Check out `#general-english`!*
> * 🌐 **Website & Guides**: [web.drakescraft.cl](https://web.drakescraft.cl) — 🛒 **Store**: [web.drakescraft.cl/store](https://web.drakescraft.cl/store.html)
> 
> *Play with this addon alongside 80+ optimized expansions live on our technical survival network!*

---

## 📖 What is {clean_name}?

{description}

---

## ⚙️ Key Features & Systems

{features_md}

---

## 📋 Technical Compatibility

| Parameter | Requirement |
|---|---|
| **Server Software** | Paper / Purpur / Folia **1.21.11** |
| **Java Runtime** | **Java 21** LTS |
| **Required Core** | [Slimefun4-Drake](https://github.com/DrakesCraft-Labs/Slimefun4-Drake) |
| **Architecture** | 100% Server-Side (Vanilla Minecraft clients can join without installing client mods) |

---

## 📥 Installation

1. Download the latest release `.jar` from the [Releases](https://github.com/DrakesCraft-Labs/{repo_name}/releases) tab or [Modrinth](https://modrinth.com/organization/drakescraft-labs).
2. Place the `.jar` into your server's `plugins/` directory alongside `Slimefun4-Drake.jar`.
3. Start or restart your server. Recipes and machines will appear automatically in the Slimefun guide (`/sf guide`).

---

## 🛠️ Building from Source

```bash
git clone https://github.com/DrakesCraft-Labs/{repo_name}.git
cd {repo_name}
{build_cmd}
```

The compiled artifact will be located under `{build_artifact}`.

---

<div align="center">

**Developed and Maintained by [DrakesCraft Labs](https://github.com/DrakesCraft-Labs)**  
Licensed under **{lic}**.

</div>

---

## 📄 License & Upstream Attribution

This project is a sovereign fork maintained by [**JackStar6677-1**](https://github.com/JackStar6677-1) under [**DrakesCraft Labs**](https://github.com/DrakesCraft-Labs).

- **Original Project:** Created by the upstream authors and the open-source community ([Upstream Repository]({upstream_url})).
- **DrakesCraft Optimizations:** Modernized for Paper/Purpur 1.21.11+, Java 21 LTS, high concurrency, asynchronous safety, and exploit/duplication prevention.
- **License:** Distributed under the original **{lic}** license terms. See the [LICENSE](LICENSE) file for complete details.
"""


def format_spanish_readme(existing_content: str, repo_name: str) -> str:
    """Cleans up and formats the Spanish README_ES.md content."""
    content = clean_conflict_markers(existing_content)

    # Ensure language switcher exists
    switcher = "[🇬🇧 **English**](README.md) · [🇪🇸 **Español**](README_ES.md)"
    if switcher not in content:
        if "</p>" in content:
            content = content.replace("</p>", f"</p>\n\n{switcher}\n", 1)
        else:
            content = f"{switcher}\n\n{content}"

    # Update server IP and domains to canonical ones
    content = re.sub(r"play\.drakescraft\.net", "mc.drakescraft.cl", content)
    content = re.sub(r"drakescraft\.net", "web.drakescraft.cl", content)
    content = re.sub(r"tienda\.drakescraft\.net", "web.drakescraft.cl/store", content)

    return content


def sync_ci_files(repo_dir: pathlib.Path, repo_name: str, apply: bool) -> list[str]:
    """Ensures .github/workflows/modrinth-publish.yml and .github/scripts/ are up to date."""
    changes = []
    wf_dir = repo_dir / ".github" / "workflows"
    scripts_dir = repo_dir / ".github" / "scripts"

    target_wf = wf_dir / "modrinth-publish.yml"
    ref_wf = CANONICAL_REF / ".github" / "workflows" / "modrinth-publish.yml"

    # 1. Workflow
    if ref_wf.exists():
        ref_wf_content = ref_wf.read_text(encoding="utf-8")
        if not target_wf.exists() or target_wf.read_text(encoding="utf-8") != ref_wf_content:
            changes.append("modrinth-publish.yml")
            if apply:
                wf_dir.mkdir(parents=True, exist_ok=True)
                target_wf.write_text(ref_wf_content, encoding="utf-8")

    # 2. Scripts
    ref_scripts_dir = CANONICAL_REF / ".github" / "scripts"
    for script_name in ["modrinth-ensure-project.mjs", "modrinth-submit-review.mjs", "svg-to-png.mjs"]:
        src_script = ref_scripts_dir / script_name
        dst_script = scripts_dir / script_name
        if src_script.exists():
            script_text = src_script.read_text(encoding="utf-8")
            # Customize fallback summary and categories in ensure-project
            if script_name == "modrinth-ensure-project.mjs":
                script_text = re.sub(
                    r"const RESUMEN = \(process\.env\.PROJECT_SUMMARY \|\| '[^']+'\)\.slice\(0, 256\);",
                    f"const RESUMEN = (process.env.PROJECT_SUMMARY || '{repo_name} - High performance Paper 1.21.11 expansion for Slimefun4.').slice(0, 256);",
                    script_text,
                )
                info = CURATED_INFO.get(repo_name, {})
                if "categories" in info:
                    cats_str = str(info["categories"])
                    script_text = re.sub(
                        r"categories:\s*\[[^\]]+\]",
                        f"categories: {cats_str}",
                        script_text,
                    )
            if not dst_script.exists() or dst_script.read_text(encoding="utf-8") != script_text:
                changes.append(f".github/scripts/{script_name}")
                if apply:
                    scripts_dir.mkdir(parents=True, exist_ok=True)
                    dst_script.write_text(script_text, encoding="utf-8")

    return changes


def git_commit(repo_dir: pathlib.Path, message: str) -> bool:
    """Commits changes in the target repository using the canonical git identity."""
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, check=True)
    # Check if there is anything staged
    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True)
    if not status.stdout.strip():
        return False

    cmd = [
        "git",
        "-c", f"user.name={AUTHOR_NAME}",
        "-c", f"user.email={AUTHOR_EMAIL}",
        "commit",
        "-m", message,
    ]
    subprocess.run(cmd, cwd=repo_dir, check=True)
    return True


def process_repository(
    repo_name: str,
    dry_run: bool,
    apply: bool,
    commit: bool,
    sync_ci_only: bool,
    readmes_only: bool,
) -> dict:
    repo_dir = BASE_DIR / repo_name
    result = {
        "repo": repo_name,
        "readme_changed": False,
        "readme_es_created": False,
        "ci_synced": [],
        "committed": False,
        "error": None,
    }

    try:
        has_build_file = (
            (repo_dir / "pom.xml").exists()
            or (repo_dir / "build.gradle").exists()
            or (repo_dir / "build.gradle.kts").exists()
        )

        readme_file = repo_dir / "README.md"
        readme_es_file = repo_dir / "README_ES.md"

        # Step 1: Handle READMEs
        if not sync_ci_only and readme_file.exists():
            current_readme = readme_file.read_text(encoding="utf-8", errors="replace")
            if is_spanish_text(current_readme):
                # Preserve Spanish content in README_ES.md
                formatted_es = format_spanish_readme(current_readme, repo_name)
                if not readme_es_file.exists() or readme_es_file.read_text(encoding="utf-8", errors="replace") != formatted_es:
                    result["readme_es_created"] = True
                    if apply:
                        readme_es_file.write_text(formatted_es, encoding="utf-8")

                # Generate new English README.md
                english_readme = generate_canonical_english_readme(repo_dir, repo_name, current_readme)
                if current_readme != english_readme:
                    result["readme_changed"] = True
                    if apply:
                        readme_file.write_text(english_readme, encoding="utf-8")

        # Step 2: Handle CI Synchronization
        if not readmes_only and has_build_file:
            ci_changes = sync_ci_files(repo_dir, repo_name, apply)
            if ci_changes:
                result["ci_synced"] = ci_changes

        # Step 3: Git Commit
        if apply and commit and (result["readme_changed"] or result["readme_es_created"] or result["ci_synced"]):
            summary_parts = []
            if result["readme_changed"]:
                summary_parts.append("standardize README to English")
            if result["readme_es_created"]:
                summary_parts.append("preserve Spanish documentation in README_ES")
            if result["ci_synced"]:
                summary_parts.append("sync Modrinth publish CI & scripts")
            msg = f"docs(modrinth): {', '.join(summary_parts)} [RELEASE]\n\nStandardize repository for Modrinth Creator Rewards compliance.\nCanonical English README with language toggle.\nFull Spanish documentation preserved in README_ES.md.\n\nCo-Authored-By: Antigravity <antigravity@google.com>"
            result["committed"] = git_commit(repo_dir, msg)

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(description="Standardize Modrinth READMEs and CI across DrakesCraft-Labs")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without modifying files")
    parser.add_argument("--apply", action="store_true", help="Apply modifications to files")
    parser.add_argument("--commit", action="store_true", help="Commit changes via Git")
    parser.add_argument("--repo", type=str, help="Process a single specific repository")
    parser.add_argument("--sync-ci-only", action="store_true", help="Only synchronize CI workflows & scripts")
    parser.add_argument("--readmes-only", action="store_true", help="Only standardize README files")

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Please specify either --dry-run or --apply.")
        sys.exit(1)

    repos_to_scan = []
    if args.repo:
        repos_to_scan = [args.repo]
    else:
        for entry in sorted(os.listdir(BASE_DIR)):
            p = BASE_DIR / entry
            if p.is_dir() and entry not in EXCLUDED_DIRS and not entry.startswith("."):
                repos_to_scan.append(entry)

    print(f"Scanning {len(repos_to_scan)} repositories (dry_run={args.dry_run}, apply={args.apply}, commit={args.commit})...\n")

    readme_changes_count = 0
    ci_synced_count = 0
    errors_count = 0

    for r in repos_to_scan:
        res = process_repository(
            r,
            dry_run=args.dry_run,
            apply=args.apply,
            commit=args.commit,
            sync_ci_only=args.sync_ci_only,
            readmes_only=args.readmes_only,
        )

        if res["error"]:
            print(f"❌ {r}: ERROR - {res['error']}")
            errors_count += 1
            continue

        actions = []
        if res["readme_changed"]:
            actions.append("README.md ➔ English")
            readme_changes_count += 1
        if res["readme_es_created"]:
            actions.append("README_ES.md preserved")
        if res["ci_synced"]:
            actions.append(f"CI synced ({len(res['ci_synced'])} files)")
            ci_synced_count += 1
        if res["committed"]:
            actions.append("Git committed")

        if actions:
            print(f"✔ {r}: {', '.join(actions)}")

    print("\n--- Summary ---")
    print(f"Repositories scanned: {len(repos_to_scan)}")
    print(f"READMEs standardized to English: {readme_changes_count}")
    print(f"Modrinth CI workflows/scripts synced: {ci_synced_count}")
    print(f"Errors encountered: {errors_count}")


if __name__ == "__main__":
    main()
