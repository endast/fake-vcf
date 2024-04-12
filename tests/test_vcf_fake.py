"""Tests for fake-vcf"""

import typing

from pathlib import Path

import pytest

from fake_vcf.vcf_faker import VirtualVCF

NR_NON_SAMPLE_COL = 9

test_data_dir = Path(__file__).resolve().parent / "test_data"
reference_dir = test_data_dir / "reference"


def get_vcf_data(
    virtual_vcf: VirtualVCF,
) -> typing.Tuple[typing.List[str], str]:
    with virtual_vcf as v_vcf:
        vcf_rows = list(v_vcf)
        data_rows = [r for r in vcf_rows if not r.startswith("##")]
        metadata = vcf_rows[0]
    return data_rows, metadata


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("num_rows",),
    [
        *[(r,) for r in range(1, 11)],
        (20,),
        (50,),
        (1000,),
        (1337,),
    ],
)
def test_fake_vcf_row_count(num_rows):
    virtual_vcf = VirtualVCF(
        num_rows=num_rows,
        num_samples=10,
        chromosome="chr1",
        sample_prefix="S",
        random_seed=42,
        phased=False,
    )

    data_rows, metadata = get_vcf_data(virtual_vcf=virtual_vcf)
    assert len(data_rows) == num_rows


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("num_rows", "phased", "large_format"),
    [
        *[(r, True, True) for r in range(1, 11)],
        (20, True, True),
        (50, True, True),
        (1000, True, True),
        (1337, True, True),
        *[(r, False, True) for r in range(1, 11)],
        (20, False, True),
        (50, False, True),
        (1000, False, True),
        (1337, False, True),
        *[(r, True, False) for r in range(1, 11)],
        (20, True, False),
        (50, True, False),
        (1000, True, False),
        (1337, True, False),
        *[(r, False, False) for r in range(1, 11)],
        (20, False, False),
        (50, False, False),
        (1000, False, False),
        (1337, False, False),
    ],
)
def test_fake_vcf_never_zero(num_rows, phased, large_format):
    virtual_vcf = VirtualVCF(
        num_rows=num_rows,
        num_samples=10,
        chromosome="chr1",
        sample_prefix="S",
        phased=phased,
        large_format=large_format,
    )

    data_rows, metadata = get_vcf_data(virtual_vcf=virtual_vcf)
    non_zero_row_count = 0
    for sample_value in virtual_vcf.sample_values[1:]:
        non_zero_sample = sample_value.split(":")[0]
        for data_row in data_rows:
            if non_zero_sample in f"{data_row}":
                non_zero_row_count += 1

    assert non_zero_row_count == num_rows


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("num_samples", "ref_dir"),
    [
        *[(s, None) for s in range(1, 11)],
        (20, None),
        (50, None),
        (1000, None),
        (1337, None),
        *[(s, reference_dir / "parquet") for s in range(1, 11)],
        (20, reference_dir / "parquet"),
        (50, reference_dir / "parquet"),
        (1000, reference_dir / "parquet"),
        (1337, reference_dir / "parquet"),
    ],
)
def test_fake_vcf_sample_count(num_samples, ref_dir):
    virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=num_samples,
        chromosome="chr1",
        sample_prefix="S",
        random_seed=42,
        phased=False,
        reference_dir=ref_dir,
    )

    data_rows, metadata = get_vcf_data(virtual_vcf=virtual_vcf)
    samples = data_rows[0].split("\t")
    assert len(samples) - NR_NON_SAMPLE_COL == num_samples


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("num_samples", "ref_dir"),
    [
        *[(s, None) for s in range(-10, 1)],
        *[(s, reference_dir / "parquet") for s in range(-10, 1)],
    ],
)
def test_invalid_sample_count(num_samples, ref_dir):
    with pytest.raises(ValueError):
        VirtualVCF(
            num_rows=10,
            num_samples=num_samples,
            chromosome="chr1",
            sample_prefix="S",
            random_seed=42,
            phased=False,
            reference_dir=ref_dir,
        )


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("num_rows", "ref_dir"),
    [
        *[(r, None) for r in range(-10, 1)],
        *[(r, reference_dir / "parquet") for r in range(-10, 1)],
    ],
)
def test_invalid_row_count(num_rows, ref_dir):
    with pytest.raises(ValueError):
        VirtualVCF(
            num_rows=num_rows,
            num_samples=10,
            chromosome="chr1",
            sample_prefix="S",
            random_seed=42,
            phased=False,
            reference_dir=ref_dir,
        )


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("num_samples", "sample_prefix", "expected", "ref_dir"),
    [
        (1, "SAM", ["SAM0000001"], None),
        (2, "SAM", ["SAM0000001", "SAM0000002"], None),
        (3, "SAM", ["SAM0000001", "SAM0000002", "SAM0000003"], None),
        (9, "SAM", [f"SAM000000{i}" for i in range(1, 10)], None),
        (9, "", [f"000000{i}" for i in range(1, 10)], None),
        (1, "SAM", ["SAM0000001"], reference_dir / "parquet"),
        (2, "SAM", ["SAM0000001", "SAM0000002"], reference_dir / "parquet"),
        (
            3,
            "SAM",
            ["SAM0000001", "SAM0000002", "SAM0000003"],
            reference_dir / "parquet",
        ),
        (9, "SAM", [f"SAM000000{i}" for i in range(1, 10)], reference_dir / "parquet"),
        (9, "", [f"000000{i}" for i in range(1, 10)], reference_dir / "parquet"),
    ],
)
def test_fake_vcf_sample_prefix(num_samples, sample_prefix, expected, ref_dir):
    virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=num_samples,
        chromosome="chr1",
        sample_prefix=sample_prefix,
        random_seed=42,
        phased=False,
        reference_dir=ref_dir,
    )

    data_rows, metadata = get_vcf_data(virtual_vcf=virtual_vcf)
    header_row = metadata.split("\n")[-2]
    sample_names = header_row.split("\t")[NR_NON_SAMPLE_COL:]
    assert sample_names == expected


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("chromosome",),
    [
        *[(f"chromosome{c}",) for c in list(range(1, 23)) + ["X", "Y"]],
        *[(f"chr{c}",) for c in list(range(1, 23)) + ["X", "Y"]],
        *[(f"c{c}",) for c in list(range(1, 23)) + ["X", "Y"]],
        *[(f"CHR{c}",) for c in list(range(1, 23)) + ["X", "Y"]],
    ],
)
def test_fake_vcf_chromosome(chromosome):
    virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=10,
        chromosome=chromosome,
        sample_prefix="S",
        random_seed=42,
        phased=False,
    )

    data_rows, metadata = get_vcf_data(virtual_vcf=virtual_vcf)
    vcf_chromosome = data_rows[0].split("\t")[0]
    assert vcf_chromosome == chromosome


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    "ref_dir",
    [(None), (reference_dir / "parquet")],
)
def test_fake_vcf_reproducibility(ref_dir):
    seed_value = 42

    orig_virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=10,
        random_seed=seed_value,
        chromosome="chr1",
        reference_dir=ref_dir,
    )

    new_virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=10,
        random_seed=seed_value,
        chromosome="chr1",
        reference_dir=ref_dir,
    )

    orig_data = get_vcf_data(virtual_vcf=orig_virtual_vcf)
    new_data = get_vcf_data(virtual_vcf=new_virtual_vcf)
    assert orig_data == new_data


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    "ref_dir",
    [(None), (reference_dir / "parquet")],
)
def test_fake_vcf_novel_data(ref_dir):
    first_seed = 42
    second_seed = 1337

    orig_virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=10,
        random_seed=first_seed,
        chromosome="chr1",
        reference_dir=ref_dir,
    )

    new_virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=10,
        random_seed=second_seed,
        chromosome="chr1",
        reference_dir=ref_dir,
    )

    orig_data = get_vcf_data(virtual_vcf=orig_virtual_vcf)
    new_data = get_vcf_data(virtual_vcf=new_virtual_vcf)
    assert orig_data != new_data
