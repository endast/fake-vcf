import json
from pathlib import Path

import pytest

import fake_vcf.vcf_reference as reference
from fake_vcf.vcf_faker import VirtualVCF
from tests.test_vcf_fake import get_vcf_data

test_data_dir = Path(__file__).resolve().parent / "test_data"
reference_dir = test_data_dir / "reference"
small_reference_file = reference_dir / "reference_small.fa"


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
def test_parse_sequences(include_sequences, expected_count, fasta_file):
    sequences = reference.parse_fasta(
        include_sequences=include_sequences, file_path=fasta_file
    )

    include_sequences = [] if include_sequences is None else include_sequences
    sequences = list(sequences)
    assert len(sequences) == expected_count
    assert (
        all(seq["id"] in include_sequences for seq in sequences)
        if include_sequences
        else True
    )
    assert all(len(seq["sequence"]) > 0 for seq in sequences)
    assert all(seq["sequence"] for seq in sequences)


@pytest.mark.reference_import
@pytest.mark.parametrize(
    "sequence_id, fasta_file, expected_sequence_sum",
    (
        ("chr1", small_reference_file, 77573),
        ("chr2", small_reference_file, 95119),
        ("chr5", small_reference_file, 129915),
    ),
)
def test_parse_sequences_content_sum(sequence_id, fasta_file, expected_sequence_sum):
    sequences = reference.parse_fasta(
        include_sequences=[sequence_id], file_path=fasta_file
    )
    sequences = list(sequences)
    assert sum([ord(s) for s in sequences[0]["sequence"]]) == expected_sequence_sum


@pytest.mark.reference_import
@pytest.mark.parametrize(
    "chrom, position, expected_reference_value",
    (
        ("chr1", 0, "N"),
        ("chr1", 10, "N"),
        ("chr1", 20, "N"),
        ("chr1", 25, "N"),
        ("chr1", 46, "N"),
        ("chr1", 50, "N"),
        ("chr1", 100, "N"),
        ("chr1", 460, "T"),
        ("chr1", 500, "C"),
        ("chr1", 1000, "G"),
        ("chr2", 0, "N"),
        ("chr2", 10, "N"),
        ("chr2", 20, "N"),
        ("chr2", 25, "N"),
        ("chr2", 46, "N"),
        ("chr2", 50, "N"),
        ("chr2", 100, "A"),
        ("chr2", 460, "C"),
        ("chr2", 500, "T"),
        ("chr2", 1000, "T"),
    ),
)
def test_reading_reference_parquet_files(chrom, position, expected_reference_value):
    reference_dir = test_data_dir / "reference/parquet"
    reference_file = reference_dir / f"fasta_{chrom}.parquet"
    reference_data = reference.load_reference_data(reference_file, memory_map=False)
    reference_value = reference.get_ref_at_pos(
        ref_data=reference_data, position=position
    )

    assert reference_value == expected_reference_value
    assert reference_data.num_columns == 1
    assert chrom in f"{reference_data.schema}"


@pytest.mark.reference_import
@pytest.mark.parametrize(
    "chrom, position, expected_reference_value",
    (
        ("chr1", 0, "N"),
        ("chr1", 10, "N"),
        ("chr1", 20, "N"),
        ("chr1", 25, "N"),
        ("chr1", 46, "N"),
        ("chr1", 50, "N"),
        ("chr1", 100, "N"),
        ("chr1", 460, "T"),
        ("chr1", 500, "C"),
        ("chr1", 1000, "G"),
        ("chr2", 0, "N"),
        ("chr2", 10, "N"),
        ("chr2", 20, "N"),
        ("chr2", 25, "N"),
        ("chr2", 46, "N"),
        ("chr2", 50, "N"),
        ("chr2", 100, "A"),
        ("chr2", 460, "C"),
        ("chr2", 500, "T"),
        ("chr2", 1000, "T"),
    ),
)
def test_reading_reference_parquet_files_with_memory_map(
    chrom, position, expected_reference_value
):
    reference_dir = test_data_dir / "reference/parquet"
    reference_parquet_file = reference_dir / f"fasta_{chrom}.parquet"
    reference_data = reference.load_reference_data(
        reference_parquet_file, memory_map=False
    )
    reference_value = reference.get_ref_at_pos(
        ref_data=reference_data, position=position
    )

    assert reference_value == expected_reference_value
    assert reference_data.num_columns == 1
    assert chrom in f"{reference_data.schema}"


@pytest.mark.reference_import
def test_parquet_reference():
    chrom = "chr1"
    row_count = 10
    sample_count = 10

    reference_dir = test_data_dir / "reference/parquet"
    reference_file = reference_dir / f"fasta_{chrom}.parquet"

    seed_value = 42

    metadata_col_count = 9
    virtual_vcf = VirtualVCF(
        num_rows=row_count,
        num_samples=sample_count,
        random_seed=seed_value,
        chromosome="chr1",
        reference_file=reference_file,
    )
    data_rows, metadata = get_vcf_data(virtual_vcf)
    columns = data_rows[0].split("\t")

    assert len(data_rows) == row_count
    assert len(columns) - metadata_col_count == sample_count


@pytest.mark.reference_import
def test_parquet_reference_outside_reference():
    chrom = "chr1"

    reference_dir = test_data_dir / "reference/parquet"
    reference_parquet_file = reference_dir / f"fasta_{chrom}.parquet"

    seed_value = 42

    with pytest.raises(ValueError):
        VirtualVCF(
            num_rows=100,
            num_samples=10,
            random_seed=seed_value,
            chromosome="chr1",
            reference_file=reference_parquet_file,
        )


@pytest.mark.reference_import
def test_import_reference(tmp_path):
    output_dir = tmp_path / "output"
    reference.import_reference(file_path=small_reference_file, output_dir=output_dir)

    assert (output_dir / "sequence_metadata.json").exists()

    with open(output_dir / "sequence_metadata.json") as metadata_file:
        metadata = json.load(metadata_file)

    for seq_id, reference_path in metadata.items():
        assert (output_dir / reference_path).exists()
