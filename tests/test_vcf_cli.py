from pathlib import Path

import pytest
from typer.testing import CliRunner

from fake_vcf import version
from fake_vcf.__main__ import app
from tests.test_vcf_fake import NR_NON_SAMPLE_COL

runner = CliRunner()

GENERATE_CMD = "generate"
IMPORT_REFERENCE_CMD = "import-reference"


def is_gz_file(filepath):
    with open(filepath, "rb") as test_f:
        return test_f.read(2) == b"\x1f\x8b"


def is_bgzip_compressed(file_path):
    with open(file_path, "rb") as file:
        # Read the first three bytes from the file
        magic_bytes = file.read(3)

    # Check if the magic bytes indicate bgzip compression
    return magic_bytes == b"\x1F\x8B\x08"


script_dir = Path(__file__).resolve().parent


@pytest.mark.generate_vcf
def test_fake_vcf_reference_import_no_input():
    result = runner.invoke(app, [IMPORT_REFERENCE_CMD])
    assert result.exit_code == 2


@pytest.mark.reference_import
def test_fake_vcf_reference_import_only_input():
    result = runner.invoke(
        app,
        [
            IMPORT_REFERENCE_CMD,
            "reference.fa",
        ],
    )
    assert result.exit_code == 2


@pytest.mark.reference_import
def test_fake_vcf_reference_import_input_output(tmp_path):
    small_reference_path = script_dir / (
        "../tests/test_data/reference/reference_small.fa"
    )

    result = runner.invoke(
        app,
        [IMPORT_REFERENCE_CMD, small_reference_path.as_posix(), tmp_path.as_posix()],
    )
    assert result.exit_code == 0


@pytest.mark.reference_import
def test_fake_vcf_reference_import_input_output_incl_chrom(tmp_path):
    small_reference_path = script_dir / (
        "../tests/test_data/reference/reference_small.fa"
    )

    result = runner.invoke(
        app,
        [
            IMPORT_REFERENCE_CMD,
            "--included_chromosomes",
            "chr1",
            small_reference_path.as_posix(),
            tmp_path.as_posix(),
        ],
    )
    assert result.exit_code == 0


@pytest.mark.generate_vcf
def test_fake_vcf_generate_no_input():
    result = runner.invoke(app, [GENERATE_CMD])
    assert result.exit_code == 0
    assert "source=VCFake" in result.stdout


@pytest.mark.generate_vcf
def test_fake_vcf_generate_no_compression_output(tmp_path):
    output_file = tmp_path / "example.vcf"
    result = runner.invoke(app, [GENERATE_CMD, "-o", output_file])
    assert result.exit_code == 0
    assert output_file.exists()
    assert "No compression" in result.stdout

    try:
        assert not is_bgzip_compressed(output_file)
    except AssertionError:
        assert not is_gz_file(output_file)


@pytest.mark.generate_vcf
def test_face_vcf_generation_compression(tmp_path):
    output_file = tmp_path / "example.vcf.gz"
    result = runner.invoke(app, [GENERATE_CMD, "-o", output_file])
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Using compression" in result.stdout

    # If biopython is installed check that we wrote a bgzip file
    try:
        assert is_bgzip_compressed(output_file)
    except AssertionError:
        assert is_gz_file(output_file)


@pytest.mark.generate_vcf
def test_face_vcf_generation_compression_no_bgzip(tmp_path):
    pytest.importorskip("Bio")
    output_file = tmp_path / "example.vcf.gz"
    result = runner.invoke(app, [GENERATE_CMD, "-o", output_file])
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Using compression" in result.stdout

    # If biopython is installed check that we wrote a bgzip file
    try:
        assert is_bgzip_compressed(output_file)
    except AssertionError:
        assert is_gz_file(output_file)


@pytest.mark.generate_vcf
def test_face_vcf_generation_seed_same(tmp_path):
    args = [GENERATE_CMD, "--seed", "42"]

    result_1 = runner.invoke(app, args)
    result_2 = runner.invoke(app, args)
    assert result_1.exit_code == 0
    assert result_2.exit_code == 0
    assert result_1.stdout == result_2.stdout


@pytest.mark.generate_vcf
def test_face_vcf_generation_seed_differ(tmp_path):
    base_args = [GENERATE_CMD, "--seed"]
    result_1 = runner.invoke(app, base_args + ["42"])
    result_2 = runner.invoke(app, base_args + ["1337"])
    assert result_1.exit_code == 0
    assert result_2.exit_code == 0
    assert result_1.stdout != result_2.stdout


@pytest.mark.generate_vcf
def test_face_vcf_generation_version(tmp_path):
    result = runner.invoke(app, [GENERATE_CMD, "-v"])
    assert result.exit_code == 0
    assert version in result.stdout


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("chr",),
    [
        *[(f"chr{c}",) for c in range(1, 22)],
    ],
)
def test_face_vcf_generation_chr_flag(chr):
    result = runner.invoke(app, [GENERATE_CMD, "-c", chr])
    assert result.exit_code == 0
    assert chr in result.stdout


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("prefix",),
    [
        ("BAM",),
        ("SAM",),
        ("MAM",),
        ("wham",),
        ("tapir",),
    ],
)
def test_face_vcf_generation_sample_prefix_flag(prefix):
    result = runner.invoke(app, [GENERATE_CMD, "-p", prefix])
    assert result.exit_code == 0
    assert f"{prefix}0000" in result.stdout


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("expected_rows",),
    [
        *[(r,) for r in range(1, 100, 10)],
    ],
)
def test_face_vcf_generation_nr_rows(expected_rows):
    result = runner.invoke(app, [GENERATE_CMD, "-r", f"{expected_rows}"])
    row_count = len([r for r in result.stdout.split("\n") if r.startswith("chr1")])
    assert result.exit_code == 0
    assert row_count == expected_rows


@pytest.mark.generate_vcf
@pytest.mark.parametrize(
    ("expected_sample_count",),
    [
        *[(r,) for r in range(1, 100, 10)],
    ],
)
def test_face_vcf_generation_nr_samples(expected_sample_count):
    result = runner.invoke(app, [GENERATE_CMD, "-s", f"{expected_sample_count}"])
    sample_count = len(
        [r for r in result.stdout.split("\n") if r.startswith("chr1")][0].split("\t")
    )
    assert result.exit_code == 0
    assert sample_count == expected_sample_count + NR_NON_SAMPLE_COL
