"""Tests for fake-vcf"""
import typing

import pytest

from fake_vcf.vcf_faker import VirtualVCF


def get_vcf_data(
    virtual_vcf: VirtualVCF,
) -> typing.Tuple[typing.List[str], typing.List[str]]:
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

    nr_non_sample_col = 9
    data_rows, metadata = get_vcf_data(virtual_vcf=virtual_vcf)
    samples = data_rows[0].split("\t")
    assert len(samples) - nr_non_sample_col == num_samples


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
def test_invalid_sample_count(num_rows):
    with pytest.raises(ValueError):
        VirtualVCF(
            num_rows=num_rows,
            num_samples=1,
            chromosome="chr1",
            sample_prefix="S",
            random_seed=42,
            phased=False,
        )
