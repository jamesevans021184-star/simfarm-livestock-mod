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


## Livestock IDs and record pool confirmed

Static analysis now confirms that livestock item IDs are the contiguous range `0xDC..0xDF`.

The purchase/placement dispatcher explicitly tests this range and calls far routine `12EE:0054`. That routine is a dedicated livestock allocator:

- 127 possible slots (indices 1..126)
- record size: `0x14` bytes
- item/type word at record +0
- active flags at +2 (bit `0x20`)
- map X/Y bytes at +5/+6
- state byte at +4
- linked 0x38-byte moving-object index at +0x10

The paired delete routine is `12EE:00D4`.

The livestock state-update routine begins at root-image offset approximately `0x1316A`. It iterates the 0x14-byte livestock pool and manages a linked 0x38-byte moving object while the animal changes movement states.

## Existing relocation support

The generic map-object relocation/update code already has explicit branches for `0xDC..0xDF`. When that type range is selected, it updates the livestock record's X/Y bytes and relocation flag. This is strong evidence that moving livestock does not require a new object format or renderer: the engine already has a relocation path for livestock records.

External documentation for the original game says the Move Object tool selects machines, feed and troughs, but not livestock. This matches the requested mod: the patch target is the selection/eligibility path that feeds the existing relocation routine, rather than rewriting animal movement from scratch.

## Original feeding behaviour reference

Original-game documentation confirms:
- livestock require feed and water;
- feed bales are consumed over time;
- troughs are replenished through the water system;
- barns reduce food/water consumption;
- rivers/lakes/ditches can form pen boundaries but are not treated as direct drinking sources in the stock game.

This gives a behavioural baseline for the grazing/natural-water patch.


## Placement validator narrowed

Further disassembly identifies a common placement validator beginning near flat root-image address `0x1ED68`.

The routine explicitly accepts these item families for object-aware placement checks:

- `0x0000..0x003F`
- `0x00C0..0x00D7`
- livestock `0x00DC..0x00DF`
- special item `0x012C`

For accepted items it resolves the item's footprint/definition and validates the target rectangle against the map. This confirms that **livestock are already legal inputs to the stock placement machinery**.

Together with the previously confirmed relocation writer at `0x1C63C`, the Move Object modification can be narrowed to the pick-up/selection path: once a livestock record is selected, the original engine already knows how to validate its destination and commit the new X/Y position.

## Livestock update state-machine observations

The dedicated 0x14-byte livestock pool contains:

- +0x00 item/species ID
- +0x02 flags (active bit 0x20; relocation/dirty bit 0x04 observed)
- +0x03 map X
- +0x04 map Y
- +0x10 linked 0x38-byte moving-object index

The state machine at `0x1576A` is movement/rendering-oriented. It creates a linked moving object, advances it, commits the final tile back to +3/+4, updates the map tile's livestock marker, then releases the linked moving object. Food/water consumption therefore lives outside this movement state machine and should not be patched here.
