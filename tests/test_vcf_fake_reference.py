from pathlib import Path

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
        (f"chr1", test_data_dir / "reference/reference_small.fa", 77573),
        (f"chr2", test_data_dir / "reference/reference_small.fa", 95119),
        (f"chr5", test_data_dir / "reference/reference_small.fa", 129915),
    ),
)
def test_parse_sequences_content_sum(sequence_id, fasta_file, expected_sequence_sum):
    fasta_file = test_data_dir / "reference/reference_small.fa"
    sequences = refrence.parse_fasta(
        include_sequences=[sequence_id], file_path=fasta_file
    )
    assert sum([ord(s) for s in sequences[0]["sequence"]]) == expected_sequence_sum
