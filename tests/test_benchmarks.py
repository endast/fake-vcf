import pytest
from test_vcf_fake import get_vcf_data
from test_vcf_fake_reference import small_reference_file

import fake_vcf.vcf_reference as reference
from fake_vcf.vcf_faker import VirtualVCF


@pytest.mark.reference_import
@pytest.mark.parametrize(
    "include_sequences, expected_count, fasta_file",
    (
        (None, 10, small_reference_file),
        (
            [f"chr{c}" for c in range(1, 11)],
            10,
            small_reference_file,
        ),
        (
            [f"chr{c}" for c in range(1, 5)],
            4,
            small_reference_file,
        ),
        (
            [f"chr{c}" for c in range(3, 8)],
            5,
            small_reference_file,
        ),
    ),
)
def test_benchmark_parse_sequences(
    include_sequences, expected_count, fasta_file, benchmark
):
    benchmark(
        reference.parse_fasta, include_sequences=include_sequences, file_path=fasta_file
    )


def create_fake_vcf(
    num_rows, num_samples, chromosome, sample_prefix, random_seed, phased
):
    virtual_vcf = VirtualVCF(
        num_rows=num_rows,
        num_samples=num_samples,
        chromosome=chromosome,
        sample_prefix=sample_prefix,
        random_seed=random_seed,
        phased=phased,
    )

    return get_vcf_data(virtual_vcf=virtual_vcf)


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
def test_benchmark_fake_vcf_row_count(num_rows, benchmark):
    benchmark(
        create_fake_vcf,
        num_rows=num_rows,
        num_samples=10,
        chromosome="chr1",
        sample_prefix="S",
        random_seed=42,
        phased=False,
    )
