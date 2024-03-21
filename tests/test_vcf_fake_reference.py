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
    "reference_file_name, position, expected_reference_value",
    (
        ("fasta_chr1.parquet", 0, "N"),
        ("fasta_chr1.parquet", 10, "N"),
        ("fasta_chr1.parquet", 20, "N"),
        ("fasta_chr1.parquet", 25, "N"),
        ("fasta_chr1.parquet", 46, "N"),
        ("fasta_chr1.parquet", 50, "N"),
        ("fasta_chr1.parquet", 100, "N"),
        ("fasta_chr1.parquet", 460, "T"),
        ("fasta_chr1.parquet", 500, "C"),
        ("fasta_chr1.parquet", 1000, "G"),
    ),
)
def test_reading_reference_parquet_files(
    reference_file_name, position, expected_reference_value
):
    reference_dir = test_data_dir / "reference/parquet"
    reference_file = reference_dir / reference_file_name
    reference_data = pq.read_table(reference_file, memory_map=True)
    reference_value = reference_data.take([position]).to_pandas().iloc[0, 0]

    assert reference_value == expected_reference_value
    assert reference_data.num_columns == 1
