Title: Buddy Repository Unspaghetti & Function Merge (Exact Rules, No Guessing)

Goal
- Clean and optimize the Buddy repository without losing a single feature or changing visible behavior:
  - Archive all Python files that are not used in any call chain from the entrypoint(s).
  - Merge duplicate or overlapping functions into a single canonical definition per feature—keep the smartest, most complete version, integrate missing pieces from weaker versions.
  - Update all imports and call sites to point to the canonical version.
- End result: minimal file count, no dead code, no function conflicts, identical (or smarter) runtime behavior.

Do not guess
- If any ambiguity is found (e.g., two near-duplicates with divergent behavior), stop and ask for clarification in the PR.
- Do not change prompts, voices, ports, or user-facing strings.
- No deletions of logic: weaker duplicates must have their unique behavior merged into the strongest version when applicable.

Entry points (build the graph from these only)
- main.py
- runner_clean.py (if present)

Step 1 — Identify the active dependency tree (static reachability)
1) For each .py file in the repo (excluding /archive, /tests, /tools), extract imports.
2) Resolve relative imports to absolute module paths.
3) Recursively follow imports starting from the entry points to produce the set of reachable files.
4) Any .py file outside this set is “unused (static)”.
5) Action: Move unused files into /archive/unused_static/ (preserve folder structure). Do not delete.

Step 2 — Detect duplicate functions
1) Parse all reachable .py files (from Step 1).
2) For each function, collect:
   - name, file path
   - AST signature (parameters, default values)
   - normalized AST of body (ignore local var names/formatting)
3) Group functions into:
   - Exact duplicates — identical logic and name
   - Near-duplicates — same name, similar logic
   - Same-name, different logic — require merge or disambiguation

Step 3 — Merge duplicate functions (rules)
- Keep the “strongest” version: most complete/feature-rich (more parameters, more branches, fuller docstring/comments).
- Integrate unique useful logic from weaker versions into the strongest version.
- If a weaker function is entirely redundant, remove it.
- Update all imports and call sites to point to the canonical function location.
- Special case: If same-name functions are used for different contexts (e.g., STT vs TTS), rename one clearly (e.g., _stt, _tts) and update all references.

Step 4 — Verify no overwriting occurs
1) Scan each file for multiple definitions of the same function name.
2) If duplicates exist in a single file:
   - If identical, keep a single definition (prefer the last if order-dependent).
   - If different, merge logic so only one remains with complete behavior.

Step 5 — Update repository imports
1) After merges, update all import and from ... import ... statements to the canonical locations.
2) Repo-wide check (AST or grep) to ensure no stale function names remain.

Step 6 — Final cleanup and verification
1) Remove empty files/folders created by merges/moves.
2) Update requirements.txt to remove packages only used by archived files.
3) Run all Buddy startup flows to confirm parity:
   - Wake word → STT → LLM → TTS
   - Memory injection/extraction
   - Emotional context
   - Background processing
4) Confirm identical or better behavior (no regressions).

Safety constraints
- No deletions of archived files: move to /archive/unused_static/.
- Preserve behavior, prompts, voices, ports, and visible strings.
- Keep original main.py functioning.
- If any endpoint/schema mismatch is detected, ask for clarification.

Outputs to produce in the PR
- archive/unused_static/ (with preserved structure)
- reports/unused_static.json — list of archived files (with reasons and original paths)
- reports/duplicates_map.json — groups of duplicate/near-duplicate functions with chosen canonical target
- reports/import_updates.json — mapping of old → new import paths
- Summary note in the PR description with:
  - Count of archived files
  - Count of merged function groups
  - Any renames (context-specific disambiguation)

Acceptance criteria
- No duplicate functions remain in the reachable set.
- Each feature has exactly one canonical definition and all references point to it.
- Buddy runs with identical or improved behavior (no user-visible regressions).
- /archive/unused_static/ contains all files not in the dependency graph.
- requirements.txt reflects only needed packages.
- CI/tests/dry-run pass without hangs; timeouts recover gracefully.

Execution order
1) Build reachability set from entry points; archive unused to /archive/unused_static/.
2) Detect duplicates/near-duplicates; pick strongest version per group.
3) Merge unique logic into strongest; remove weaker duplicates.
4) Update imports and call sites repo-wide to the canonical functions.
5) Clean empty files/folders; update requirements.txt.
6) Run tests/dry-run; fix any regressions; update reports/*; finalize PR summary.