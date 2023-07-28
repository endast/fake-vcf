"""Tests for fake_vcf"""
import pytest

from fake_vcf.vcf_faker import VirtualVCF
from fake_vcf.vcf_generator import fake_vcf


@pytest.mark.parametrize(
    ("num_rows",),
    [
        *[(r,) for r in range(0, 11)],
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

    with virtual_vcf as v_vcf:
        vcf_rows = list(v_vcf)
        data_rows = [r for r in vcf_rows if not r.startswith("##")]
        assert len(data_rows) == num_rows
