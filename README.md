# SimFarm Livestock Mod

Reverse-engineering and patch tooling for a user-owned copy of **SimFarm (DOS, 1993)**.

This repository does **not** contain the commercial SimFarm game files.

## Target executable

SHA-256:

`f497c6ffe5a6b729d3c48c431a1285b1b6c1e890313b9d5081b4f4cba399dd0a`

## Intended gameplay changes

1. Allow the existing hand/grab tool to relocate livestock between valid paddocks.
2. Livestock graze available paddock grass/pasture before consuming supplemental feed.
3. Grazing depletes pasture; pasture recovery remains tied to viable conditions.
4. Drought reduces/stops pasture availability so existing animal feed becomes necessary.
5. Livestock can drink from accessible natural lake/river water; existing troughs remain the fallback where natural water is unavailable.
6. Preserve the original SimFarm UI, graphics, crops, buildings, economy, weather and other gameplay.

## Method

The supplied executable is a 16-bit DOS MZ program with substantial appended data/overlay content. Analysis therefore starts by mapping the MZ image, appended regions, strings, relocations and executable references before any binary patch is emitted.

Useful upstream reverse-engineering references:
- fenugrec/overlazy — Microsoft C overlay analysis/flattening
- neuviemeporte/mzretools — MZ/8086 analysis tools

## Safety rule

The patcher must verify the exact SHA-256 above before modifying a user's executable. It must never silently patch an unknown SimFarm version.
