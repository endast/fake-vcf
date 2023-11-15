"""Tests for fake-vcf"""
import typing

import pytest

from fake_vcf.vcf_faker import VirtualVCF

NR_NON_SAMPLE_COL = 9


def get_vcf_data(
    virtual_vcf: VirtualVCF,
) -> typing.Tuple[typing.List[str], str]:
    with virtual_vcf as v_vcf:
        vcf_rows = list(v_vcf)
        data_rows = [r for r in vcf_rows if not r.startswith("##")]
        metadata = vcf_rows[0]
    return data_rows, metadata


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


@pytest.mark.parametrize(
    ("num_samples",),
    [
        *[(s,) for s in range(1, 11)],
        (20,),
        (50,),
        (1000,),
        (1337,),
    ],
)
def test_fake_vcf_sample_count(num_samples):
    virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=num_samples,
        chromosome="chr1",
        sample_prefix="S",
        random_seed=42,
        phased=False,
    )

    data_rows, metadata = get_vcf_data(virtual_vcf=virtual_vcf)
    samples = data_rows[0].split("\t")
    assert len(samples) - NR_NON_SAMPLE_COL == num_samples


@pytest.mark.parametrize(
    ("num_samples",),
    [
        *[(s,) for s in range(-10, 1)],
    ],
)
def test_invalid_sample_count(num_samples):
    with pytest.raises(ValueError):
        VirtualVCF(
            num_rows=10,
            num_samples=num_samples,
            chromosome="chr1",
            sample_prefix="S",
            random_seed=42,
            phased=False,
        )


@pytest.mark.parametrize(
    ("num_rows",),
    [
        *[(r,) for r in range(-10, 1)],
    ],
)
def test_invalid_row_count(num_rows):
    with pytest.raises(ValueError):
        VirtualVCF(
            num_rows=num_rows,
            num_samples=10,
            chromosome="chr1",
            sample_prefix="S",
            random_seed=42,
            phased=False,
        )


@pytest.mark.parametrize(
    (
        "num_samples",
        "sample_prefix",
        "expected",
    ),
    [
        (1, "SAM", ["SAM0000001"]),
        (2, "SAM", ["SAM0000001", "SAM0000002"]),
        (3, "SAM", ["SAM0000001", "SAM0000002", "SAM0000003"]),
        (9, "SAM", [f"SAM000000{i}" for i in range(1, 10)]),
        (9, "", [f"000000{i}" for i in range(1, 10)]),
    ],
)
def test_fake_vcf_sample_prefix(num_samples, sample_prefix, expected):
    virtual_vcf = VirtualVCF(
        num_rows=10,
        num_samples=num_samples,
        chromosome="chr1",
        sample_prefix=sample_prefix,
        random_seed=42,
        phased=False,
    )

    data_rows, metadata = get_vcf_data(virtual_vcf=virtual_vcf)
    header_row = metadata.split("\n")[-2]
    sample_names = header_row.split("\t")[NR_NON_SAMPLE_COL:]
    assert sample_names == expected


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


def test_fake_vcf_reproducibility():
    seed_value = 42

    orig_virtual_vcf = VirtualVCF(
        num_rows=10, num_samples=10, random_seed=seed_value, chromosome="chr1"
    )

    new_virtual_vcf = VirtualVCF(
        num_rows=10, num_samples=10, random_seed=seed_value, chromosome="chr1"
    )

    orig_data = get_vcf_data(virtual_vcf=orig_virtual_vcf)
    new_data = get_vcf_data(virtual_vcf=new_virtual_vcf)
    assert orig_data == new_data


def test_fake_vcf_novel_data():
    first_seed = 42
    second_seed = 1337

    orig_virtual_vcf = VirtualVCF(
        num_rows=10, num_samples=10, random_seed=first_seed, chromosome="chr1"
    )

    new_virtual_vcf = VirtualVCF(
        num_rows=10, num_samples=10, random_seed=second_seed, chromosome="chr1"
    )

    orig_data = get_vcf_data(virtual_vcf=orig_virtual_vcf)
    new_data = get_vcf_data(virtual_vcf=new_virtual_vcf)
    assert orig_data != new_data
