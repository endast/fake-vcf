import pytest
from typer.testing import CliRunner

from fake_vcf import version
from fake_vcf.__main__ import app
from tests.test_vcf_fake import NR_NON_SAMPLE_COL

runner = CliRunner()


def is_gz_file(filepath):
    with open(filepath, "rb") as test_f:
        return test_f.read(2) == b"\x1f\x8b"


def is_bgzip_compressed(file_path):
    with open(file_path, "rb") as file:
        # Read the first three bytes from the file
        magic_bytes = file.read(3)

    # Check if the magic bytes indicate bgzip compression
    return magic_bytes == b"\x1F\x8B\x08"


def test_app_no_input():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "source=VCFake" in result.stdout


def test_app_no_compression_output(tmp_path):
    output_file = tmp_path / "example.vcf"
    result = runner.invoke(app, ["-o", output_file])
    assert result.exit_code == 0
    assert output_file.exists()
    assert "No compression" in result.stdout

    try:
        assert not is_bgzip_compressed(output_file)
    except AssertionError:
        assert not is_gz_file(output_file)


def test_app_compression(tmp_path):
    output_file = tmp_path / "example.vcf.gz"
    result = runner.invoke(app, ["-o", output_file])
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Using compression" in result.stdout

    # If biopython is installed check that we wrote a bgzip file
    try:
        assert is_bgzip_compressed(output_file)
    except AssertionError:
        assert is_gz_file(output_file)


def test_app_seed_same(tmp_path):
    result_1 = runner.invoke(app, ["--seed", "42"])
    result_2 = runner.invoke(app, ["--seed", "42"])
    assert result_1.exit_code == 0
    assert result_2.exit_code == 0
    assert result_1.stdout == result_2.stdout


def test_app_seed_differ(tmp_path):
    result_1 = runner.invoke(app, ["--seed", "42"])
    result_2 = runner.invoke(app, ["--seed", "1337"])
    assert result_1.exit_code == 0
    assert result_2.exit_code == 0
    assert result_1.stdout != result_2.stdout


def test_app_version(tmp_path):
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    assert version in result.stdout


@pytest.mark.parametrize(
    ("chr",),
    [
        *[(f"chr{c}",) for c in range(1, 22)],
    ],
)
def test_app_chr_flag(chr):
    result = runner.invoke(app, ["-c", chr])
    assert result.exit_code == 0
    assert chr in result.stdout


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
def test_app_sample_prefix_flag(prefix):
    result = runner.invoke(app, ["-p", prefix])
    assert result.exit_code == 0
    assert f"{prefix}0000" in result.stdout


@pytest.mark.parametrize(
    ("expected_rows",),
    [
        *[(r,) for r in range(1, 100, 10)],
    ],
)
def test_app_nr_rows(expected_rows):
    result = runner.invoke(app, ["-r", f"{expected_rows}"])
    row_count = len([r for r in result.stdout.split("\n") if r.startswith("chr1")])
    assert result.exit_code == 0
    assert row_count == expected_rows


@pytest.mark.parametrize(
    ("expected_sample_count",),
    [
        *[(r,) for r in range(1, 100, 10)],
    ],
)
def test_app_nr_samples(expected_sample_count):
    result = runner.invoke(app, ["-s", f"{expected_sample_count}"])
    sample_count = len(
        [r for r in result.stdout.split("\n") if r.startswith("chr1")][0].split("\t")
    )
    assert result.exit_code == 0
    assert sample_count == expected_sample_count + NR_NON_SAMPLE_COL
