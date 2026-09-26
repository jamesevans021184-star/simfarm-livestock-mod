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
