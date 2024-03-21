from pathlib import Path

import pyarrow.parquet as pq
import pytest

import fake_vcf.reference as refrence

test_data_dir = Path(__file__).resolve().parent / "test_data"


@pytest.mark.parametrize(
    "include_sequences, fasta_file",
    (
        (None, test_data_dir / "reference/reference_small.fa"),
        (
            [f"chr{c}" for c in range(1, 11)],
            test_data_dir / "reference/reference_small.fa",
        ),
        (
            [f"chr{c}" for c in range(1, 5)],
            test_data_dir / "reference/reference_small.fa",
        ),
        (
            [f"chr{c}" for c in range(3, 8)],
            test_data_dir / "reference/reference_small.fa",
        ),
    ),
)
def test_parse_sequences(include_sequences, fasta_file):
    fasta_file = test_data_dir / "reference/reference_small.fa"
    sequences = refrence.parse_fasta(
        include_sequences=include_sequences, file_path=fasta_file
    )

    include_sequences = [] if include_sequences is None else include_sequences

    assert len(sequences) == len(include_sequences)
    assert all(seq["id"] in include_sequences for seq in sequences)
    assert all(len(seq["sequence"]) > 0 for seq in sequences)
    assert all(seq["sequence"] for seq in sequences)


@pytest.mark.parametrize(
    "sequence_id, fasta_file, expected_sequence_sum",
    (
        ("chr1", test_data_dir / "reference/reference_small.fa", 77573),
        ("chr2", test_data_dir / "reference/reference_small.fa", 95119),
        ("chr5", test_data_dir / "reference/reference_small.fa", 129915),
    ),
)
def test_parse_sequences_content_sum(sequence_id, fasta_file, expected_sequence_sum):
    fasta_file = test_data_dir / "reference/reference_small.fa"
    sequences = refrence.parse_fasta(
        include_sequences=[sequence_id], file_path=fasta_file
    )
    assert sum([ord(s) for s in sequences[0]["sequence"]]) == expected_sequence_sum


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
    reference_data = refrence.load_reference_data(reference_file, memory_map=True)
    reference_value = refrence.get_ref_at_pos(
        ref_data=reference_data, position=position
    )

    assert reference_value == expected_reference_value
    assert reference_data.num_columns == 1
    assert chrom in f"{reference_data.schema}"
