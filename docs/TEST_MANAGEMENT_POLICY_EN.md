# FileNexusSuite — Test Management Policy

**English** | [한국어](./TEST_MANAGEMENT_POLICY.md)

**Established**: 2026-04-22 (during v1.0.7 pre-release work, Session 3)
**Status**: Active — permanently applied across the entire project

---

## 1. Background

During v1.0.7 Sessions 2 and 3, an accumulation of 17 orphaned translation keys was discovered (15 of which were ultimately confirmed dead).

**Structural cause**: The invariant test series (`test_all_langs_have_vXXX_keys`) had been operated on a "version snapshot" basis — key additions were captured but no convention existed for key removal. Only 2 keys were enforced as invariants; the remaining 13 were unregistered, leaving them in a state where automated tests could never detect them as orphaned.

This policy aims to prevent recurrence of the same problem. As a result of executing Session 3, the following were established:
- Full restructuring of the invariant architecture (version snapshot → 10 tab-based functional areas)
- Addition of "preemptive verification of invariant registration" to the dead-code criteria (§4.2)
- Codification of the through-line: *"History is the responsibility of Git logs and the CHANGELOG; tests are maintained as the specification of what is currently alive."*

**v1.1.0 modularization track update (2026-05-09)**: The modularization track introduced module-level test classes (`TestFnsTheme` (with the `fns_theme.py` extraction), `TestFnsTranslations` (with the i18n migration to Qt Linguist)) as a complement to the tab-based functional invariants. The two axes are independent — module classes verify the extracted-module surface and package shape, while tab-based macro-categories verify cross-language translation invariants regardless of where the data physically lives. When module extraction breaks the premise of an existing source-grep test (the parsed definition no longer lives in the main module), the test is either rewritten as source-grep against the new module or excised entirely if equivalent runtime coverage already exists elsewhere.

---

## 2. The Two Layers of Testing

### 2.1 Automated Tests (`test_file_nexus.py`)

**Role**: Defense against repetitive, structural defects

- Consistency of function inputs and outputs
- Signal symmetry (connect ↔ disconnect pairs)
- Translation key completeness (key-count parity across 5 languages, presence of required keys per major category)
- `retranslate` chain integrity (regression prevention against undefined attribute references)
- Configuration persistence (JSON save/load round-trip)

Characteristics: Mechanically repeatable; identical results expected on both CI and local environments.

### 2.2 Manual QA (Hands-on Scenarios)

**Role**: Defense against judgment, visual, and flow defects

- Layout, color, contrast, timing
- Naturalness of user flow
- Final adjudication of "is this what the user actually wants?"
- Perceived responsiveness in exceptional cases (e.g. no freezing when dragging a large file)

Characteristics: Human judgment is essential; the central challenge is documenting reproducible scenarios.

### 2.3 The Relationship Between the Two Layers

- **Substitutive ❌** / **Complementary ✅**
- Expanding automation does not imply reducing manual QA
- Defects repeatedly detected in manual QA are reviewed for promotion to automated tests
- Visual and flow defects unreachable by automation are codified as manual QA scenarios

---

## 3. The Five Principles

1. **Automated tests catch repetitive, structural defects.**
2. **Manual QA catches judgment, visual, and flow defects.**
3. **The two layers are complementary, not substitutive; expanding automation does not mean shrinking manual QA.**
4. **When adding a new feature, both automated and manual coverage are explicitly specified.**
5. **When removing a feature, both automated tests and manual scenarios are updated.**

---

## 4. Invariant Test Design Principles

### 4.1 Tab-Based Functional Area Structure

Translation key invariants are organized around **10 major categories** (see §5). Each category is paired with a single test method that verifies the core representative keys for that area.

This is not exhaustive key validation but rather a "minimum-evidence" set proving that the functional area is alive. When new keys are added, they are incorporated into the relevant category test as representative keys when warranted; when features are removed, the corresponding entries are immediately deleted from the same category test.

### 4.2 Dead-Code Criteria (Strengthened in v1.0.7 Session 3)

Before declaring a translation key or code element dead, all five of the following criteria must be confirmed:

1. **Zero static references** — `grep` confirms no calls anywhere in the file
2. **Dynamic dispatch ruled out** — the key is not generated dynamically via `getattr` or f-string concatenation
3. **No intentional reservation in documentation** — no comments in source or design documents marking the element as "reserved for future use" or "temporarily held"
4. **No evidence of executable reachability** — no execution scenario can reach the dead-code path
5. **Invariant registration status in the test file** — if registered, removing the source must be accompanied by updating the test (otherwise FAIL is triggered)

Criterion 5 was derived from the `tf_dlg_overwrite` rollback case in v1.0.7 Session 2. If the source is removed but the invariant is left untouched, the automated test will block the removal; preemptive verification of criterion 5 prevents incomplete cleanups.

### 4.3 Through-Line

> **History is the responsibility of Git logs and the CHANGELOG; tests are maintained as the specification of what is currently alive.**

A test file is not "yesterday's snapshot" but "today's specification." The fact that a key was added in a past version is sufficiently traced via `git blame` and the CHANGELOG, so the convention of embedding version numbers in test method names is hereby retired.

### 4.4 Prohibitions

- ❌ **No new adoption of version-snapshot patterns** — patterns such as `test_all_langs_have_vXXX_keys` are subject to recurrence prevention
- ❌ **No accumulation of historical artifacts in tests** — past version markers are not left in test code
- ❌ **No invariants persisting for removed features** — when a feature is removed, its invariants are simultaneously updated
- ❌ **No retention of source-grep tests broken by module extraction** — when a definition migrates to `fns_<module>.py`, source-grep tests that parsed the main module's source are either rewritten against the new module or removed (v1.1.0 modularization track)
- ❌ **No retention of source-grep tests when equivalent runtime coverage exists** — if the invariant is also enforced by a module-load test, a new `TestFns*` class, or cross-language symmetry, the source-grep version is removed

### 4.5 Recommendations

- ✅ Maintain invariant tests per functional area (the 10-category basis)
- ✅ When adding a new key, review whether to update the representative-key set of the corresponding category test
- ✅ When removing a feature, immediately delete the entry from the same category test
- ✅ For keys with ambiguous category boundaries: assign to the **first UI tab in which the key appears** preferentially; if used commonly across tabs, place under `common`; remaining edge cases under `misc` (target: minimization)
- ✅ **`TestFns<Module>` class pattern for module-track regressions** — when a module is extracted, add a dedicated test class covering: (a) module surface (public dicts, functions, constants), (b) package shape if the extraction includes a sub-package (sub-files present, each file exposes its expected variable), (c) source-grep invariants on the new module (import statements, composition patterns), (d) main-module integration (import block present, old definitions absent)
- ✅ **Prefer module-load tests over source-grep tests** when both express the same invariant — module-load is more stable across formatting changes
- ✅ **Source-only invariants may be retired** when data moves to per-language files where the same property is caught at PR-review time via `git diff` (e.g., duplicate keys in a Python dict literal that the runtime silently overwrites)

---

## 5. The 10 Major Categories (Confirmed 2026-04-22)

| # | Category | Corresponding UI Area | Prefix Examples | Test Method |
|---|---|---|---|---|
| 1 | `common` | Cross-tab common dialogs and buttons | `dlg_*`, `btn_*` (selected) | `test_all_langs_have_common_dialog_keys` |
| 2 | `text_merger` | Text Merger tab | `merge_*`, `sm_*` | `test_all_langs_have_text_merger_keys` |
| 3 | `text_converter` | Text Converter tab | `conv_*`, `tc_*` | `test_all_langs_have_text_converter_keys` |
| 4 | `tag_editor` | Tag Editor tab | `tag_*` | `test_all_langs_have_tag_editor_keys` |
| 5 | `batch_renamer` | Batch Renamer tab | `batch_*` + `rename_*` (unified) | `test_all_langs_have_batch_renamer_keys` |
| 6 | `text_fixer` | Text Fixer tab | `tf_*` | `test_all_langs_have_text_fixer_keys` |
| 7 | `bulk_fixer` | Bulk Fixer tab | `bulk_*` | `test_all_langs_have_bulk_fixer_keys` |
| 8 | `settings` | Settings dialog | `settings_*`, `license_*` | `test_all_langs_have_settings_keys` |
| 9 | `shortcut` | Shortcut system | `sc_*` | `test_all_langs_have_shortcut_keys` |
| 10 | `misc` | Anything not belonging to the above | — | `test_all_langs_have_misc_keys` |

### 5.1 Handling Boundary-Ambiguous Cases

1. Assign to the **UI tab where the key first appears** preferentially
2. Keys **used in common across multiple tabs** belong under the `common` category
3. Keys exclusive to a particular feature group belong to that functional area
4. Keys that fit nowhere are assigned to `misc` — with minimization as the goal

### 5.2 Rationale for Unifying the Two Prefixes Under `batch_renamer`

Investigation of the original `folder_renamer.py` v2.1.0 (the standalone program prior to integration) revealed:
- **`batch_*`** ← derived from the original class name `BatchRenamer` → applied to the tab UI and options
- **`rename_*`** ← derived from the original method names `_do_rename` / `_confirm_rename` → applied to status and feedback for the rename action

The distinction between these two prefixes is not a refactoring residue but a sound design decision; therefore, they are operated under a single unified category.

---

## 6. Future Expansion Candidates (v1.0.8+)

Out of scope at the time this policy was established, but areas to be considered for future adoption:

- **GUI test automation** (pytest-qt based) — verification of signal/widget interactions
- **AST-based signal symmetry verification** — to replace the current manual `grep` approach
- **Visual regression testing** — to automatically detect layout and color changes, partially replacing manual QA
- **Comprehensive test-quality audit** — eliminating false positives/negatives and redundant tests

Even when these are adopted, the Five Principles in §3 and the through-line in §4 remain unchanged.

---

## 7. Change Log

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-22 | Initial draft — v1.0.7 Session 3. Codified as the result of cleaning up 15 orphaned translation keys and restructuring invariants. |
| v2 | 2026-05-09 | v1.1.0 modularization track — added module-level test class pattern (`TestFnsTheme` (with the `fns_theme.py` extraction), `TestFnsTranslations` (with the i18n migration to Qt Linguist)). Source-grep tests broken by module extraction are subject to surgical excision when equivalent coverage exists elsewhere (§4.4 / §4.5 expanded). To be revised to v3 in a subsequent update with `TestFnsUtils` (`fns_utils.py` extraction backfill) and any future package-track conventions. |
