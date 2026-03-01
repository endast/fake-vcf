# Code Review: fake-vcf

## Overview

**fake-vcf** is a well-structured Python CLI tool that generates synthetic VCF
(Variant Call Format) files for testing bioinformatics pipelines. It uses Typer
for CLI, PyArrow for Parquet-based reference data, and supports phased/unphased
genotypes with optional reference integration.

The project has solid fundamentals: good test coverage, CI/CD, linting setup,
and a clean iterator-based generation pattern. However, there are several bugs
and quality issues worth addressing.

---

## Bugs

### 1. Metadata key mismatch — VCF header always shows fallback value

**Files:** `vcf_faker.py:60`, `vcf_reference.py:77`

`vcf_faker.py:60` reads key `'source_reference_file'`, but `vcf_reference.py:77`
writes key `'reference_file'`:

```python
# vcf_faker.py:60 — reads a key that never exists
self.reference_metadata.get('source_reference_file', 'sample.fa')

# vcf_reference.py:77 — stores under a different key
sequence_metadata = {
    "reference_file": file_path.name,  # <-- mismatch
    ...
}
```

**Impact:** The `##reference=` line in the VCF header always falls back to
`ftp://ftp.example.com/sample.fa` even when real reference data is loaded.

### 2. Input validation happens after side effects

**File:** `vcf_faker.py:79`

The `ValueError` check for `num_samples < 1 or num_rows < 1` occurs *after*
`_setup_reference_data()` has already run (line 51), the header string has been
built, and sample weights have been calculated. If `num_rows=0` is passed with
a valid reference directory, `_setup_reference_data()` opens and parses JSON
metadata files before the validation rejects the input.

```python
# Line 51 — runs first, may do file I/O
self._setup_reference_data()

# ... header construction, weight calculation ...

# Line 79 — validation happens too late
if num_samples < 1 or num_rows < 1:
    raise ValueError(...)
```

**Fix:** Move the validation to the top of `__init__`.

### 3. Zero weights produce degenerate sample distributions

**File:** `vcf_faker.py:89-93`

For `num_samples < 500` (phased), the non-ref weights are all 0:

```python
self.sample_value_weights = [
    num_samples * 10,        # e.g., 100 for 10 samples
    int(num_samples / 500),  # 0 for num_samples < 500
    int(num_samples / 500),  # 0
    int(num_samples / 300),  # 0 for num_samples < 300
]
```

`random.choices` with zero weights means non-ref genotypes are **never**
selected. The fallback at lines 128-141 forces exactly one sample to be
non-ref, but this means only 1 out of N samples per row carries a variant — a
very unrealistic distribution for most use cases. For the common case of
generating test data with 10-100 samples, the data is almost entirely
homozygous reference.

### 4. Redundant `random.choice` from single-element list

**File:** `vcf_faker.py:233`

```python
filt = self.random.choice(["PASS"])  # Always returns "PASS"
```

This is a no-op. Could simply be `filt = "PASS"`. If the intent was to
eventually support multiple filter values, a `# TODO` would clarify this.

---

## Code Quality Issues

### 5. Typo in CLI help text

**File:** `__main__.py:129`

```python
help="Path to imported refernce directory.",
#                       ^^^^^^^^ should be "reference"
```

### 6. Wrong Python target version in tooling config

**File:** `pyproject.toml:85,106`

Black and isort are configured for Python 3.8, but the project requires 3.9+:

```toml
[tool.black]
target-version = ["py38"]  # should be ["py39"]

[tool.isort]
py_version = 38  # should be 39
```

### 7. Duplicate dev dependency sections

**File:** `pyproject.toml`

Dev dependencies are defined in both the legacy `[tool.poetry.dev-dependencies]`
(line 42) and the modern `[tool.poetry.group.dev.dependencies]` (line 57) sections
with slightly different version constraints (e.g., `pytest-html = "^4.0.2"` vs
`"^4.1.1"`). Only the group-based section is needed.

### 8. Deprecated `typing.List` import

**File:** `__main__.py:1`

Since the project requires Python 3.9+, `list[str]` can be used directly instead
of `from typing import List`.

### 9. Inefficient set construction

**File:** `vcf_reference.py:34`

```python
parsed_sequences = {seq for seq in sequences}  # should be set(sequences)
```

### 10. `fake_vcf_data()` lacks type hints

**File:** `vcf_generator.py:54-64`

All parameters are untyped, unlike the rest of the codebase which uses annotations.

---

## Test Issues

### 11. Duplicate test functions

**File:** `test_vcf_cli.py:107,122`

`test_face_vcf_generation_compression` and
`test_face_vcf_generation_compression_no_bgzip` are **identical** — same body,
same assertions. The second was likely intended to mock out biopython to test
the gzip fallback path, but the mock is missing.

### 12. Memory map test doesn't test memory mapping

**File:** `test_vcf_fake_reference.py:137`

`test_reading_reference_parquet_files_with_memory_map` passes `memory_map=False`,
making it identical to the non-memory-mapped test above it. It should use
`memory_map=True`.

### 13. Built-in name shadowing in tests

**File:** `test_vcf_cli.py:171`

The parameter `chr` shadows Python's built-in `chr()` function:

```python
def test_face_vcf_generation_chr_flag(chr):  # shadows built-in
```

Should be renamed to `chrom` or `chromosome`.

### 14. Inconsistent test naming

Most CLI test functions use the prefix `test_face_vcf_generation_*` (note "face"
instead of "fake"). This appears throughout and is a consistent typo in the
naming convention.

---

## Minor / Informational

- **`vcf_faker.py:160`** — Error message uses `len(self.reference_data)` but
  the condition uses `self.reference_data.shape[0]`. These return the same value
  for PyArrow tables, but the inconsistency is confusing.
- **`vcf_faker.py:40`** — `rows_remaining = num_rows + 1` to account for the
  header is a non-obvious design. A boolean flag (`header_emitted`) would be
  clearer.
- **`vcf_faker.py:285-296`** — The context manager (`__enter__`/`__exit__`)
  does nothing. It could be removed or documented as intentional (for future
  resource cleanup).

---

## Summary

| Category          | Count |
|-------------------|-------|
| Bugs              | 4     |
| Code quality      | 6     |
| Test issues       | 4     |
| Minor/informational | 3   |

The most impactful bugs are **#1** (metadata key mismatch causing wrong VCF
headers) and **#3** (degenerate sample weights). The test issues (**#11**,
**#12**) mean certain code paths aren't actually being validated despite test
names suggesting they are.
