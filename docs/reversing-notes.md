# Reverse-engineering notes

## Verified executable facts

- 16-bit DOS MZ executable.
- Exact supported SHA-256: `f497c6ffe5a6b729d3c48c431a1285b1b6c1e890313b9d5081b4f4cba399dd0a`
- File size: 621,735 bytes.
- Root MZ image size from page fields: 183,134 bytes.
- Appended region: 438,601 bytes.
- Root header reports 2,372 relocations.
- Resource strings found at file offsets:
  - Place Fences: 0x551B0
  - Water Trough for Animals: 0x55204
  - Feed for Animals: 0x5532A
  - Severe Drought: 0x55452
  - Horse: 0x8CA62
  - Sheep: 0x8CA77

## Important correction

A raw scan of this SimFarm build does **not** show literal `CD 3F` bytes in the complete file, so the overlay mechanism must not be assumed solely from generic Microsoft C overlay documentation. The appended region needs to be mapped from this executable's own structures/references.

## Next targets

- Determine appended-region record/container boundaries.
- Locate code/data references to livestock object IDs and feed/trough resource records.
- Identify the animal needs update routine and hand-tool object eligibility routine.
- Build patches only after instruction-level preimages are verified.


## Overlay manager decoded

The resident overlay-manager descriptor table begins at file offset `0x2A903`.
Descriptors are 18 bytes (9 little-endian words). For the normal overlays:

- word 0: overlay file offset in paragraphs
- word 2: in-memory image size in paragraphs
- word 3: relocation count
- word 4: `0xFFFF` marker
- word 5: overlay number
- word 6: file-backed image size/copy field
- word 7: load segment
- word 8: overlay-manager segment

Normal overlays contain a relocation table first (`relocation_count * 4` bytes), followed by their image. Calculated boundaries match the next descriptor to within alignment padding.

The root executable also contains 10-byte overlay thunks around `0x2AC04`:

`E8 <loader-rel16> EA <target-off16> 56 2A <overlay-id16>`

The far jump targets the common overlay load segment `2A56h`; the trailing word identifies which overlay must be loaded. This gives us a reliable map from resident callers to individual overlay functions.

## Livestock / movable-object lead

The permanent data image begins after the large relocation block at approximately `0x53C6C`.

Verified livestock-adjacent data:

- `Horse`, `Cow`, `Pig`, `Sheep`
- individual names `Rascal`, `Missy`, `Stella`, `Bogie`
- animal VOC names (`cow%d.voc`, `pig.voc`, `sheep%d.voc`, `horse1.voc`)
- a compact numeric definition table immediately before the species strings.

Resident code around file offset `0x102EA` creates entries in a 127-slot object pool. Each object record is `0x38` bytes. The routine initializes coordinates, flags/state, timestamps and type-derived fields from an 18-byte definition table. A companion routine around `0x1027E` releases an object. A search/place routine around `0x1226E` scans the same pool, filters object flags/type, finds an eligible nearby object or creates one, and is called from numerous tool/simulation paths.

Several callers pass explicit type IDs including `4`, `5` and `7`; these are now priority candidates for the livestock/tool path and will be verified against the animal definition table before patching.

A resident routine references data segment `654Ah` offset `237Eh`, which maps exactly into the livestock-name block. This confirms that the runtime segment mapping for the permanent data image is understood well enough to make code/data cross-references.
