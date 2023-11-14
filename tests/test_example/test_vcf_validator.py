import platform
import stat
import subprocess
from pathlib import Path
from urllib.request import urlretrieve

import pytest
from typer.testing import CliRunner

from fake_vcf.__main__ import app

runner = CliRunner()

test_file_parent = Path(__file__).resolve().parent


def vcf_validator():
    vcf_validator_path = test_file_parent / "../../vcf_validator/vcf_validator"
    system_platform = platform.system()
    if not vcf_validator_path.exists():
        base_url = (
            "https://github.com/EBIvariation/vcf-validator/releases/download/v0.9.4"
        )

        dl_urls = {
            "Linux": f"vcf_validator_linux",
            "Darwin": f"vcf_validator_macos",
            "Windows": f"vcf_validator.exe",
        }
        vcf_validiator_dl_url = f"{base_url}/{dl_urls[system_platform]}"

        urlretrieve(
            vcf_validiator_dl_url, vcf_validator_path
        )  # nosec CWE-22 should not be a problem
        vcf_validator_path.chmod(vcf_validator_path.stat().st_mode | stat.S_IEXEC)

    return vcf_validator_path


def run_vcf_validator(vcf_file_path, result_path):
    args = ["-r", "text", "-i", f"{vcf_file_path}", f"-o", f"{result_path}"]
    vcf_validator_path = vcf_validator()
    cmd = [vcf_validator_path] + args

    result = subprocess.run(cmd, capture_output=True, text=True)
    all_error_data = []
    for f in result_path.glob("*error*.txt"):
        with open(f) as vcf_error_file:
            error_data = vcf_error_file.read()
            all_error_data.append(error_data)
    return result, "\n".join(all_error_data)


@pytest.mark.parametrize(
    ("cli_args",),
    [
        (["-r", "10", "--no-large-format"],),
        (["-r", "50", "--no-large-format"],),
        (["-r", "100", "--no-large-format"],),
    ],
)
def test_vcf_file_validation(cli_args: list, tmp_path):
    vcf_file_path = tmp_path / "example.vcf"
    args = cli_args + ["-o", vcf_file_path]
    runner.invoke(app, args=args)

    validator_status, validation_result = run_vcf_validator(
        vcf_file_path=vcf_file_path, result_path=tmp_path
    )

    assert (
        "According to the VCF specification, the input file is valid"
        in validation_result
    )
    assert validator_status.returncode == 0
