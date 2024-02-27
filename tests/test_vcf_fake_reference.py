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
    include_sequences = [f"chr{c}" for c in range(1, 11)]
    fasta_file = test_data_dir / "reference/reference_small.fa"
    sequences = refrence.parse_fasta(
        include_sequences=include_sequences, file_path=fasta_file
    )
    assert len(sequences) == len(include_sequences)
    assert all(seq["id"] in include_sequences for seq in sequences)
