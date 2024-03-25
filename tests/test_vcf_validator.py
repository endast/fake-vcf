import itertools
import platform
import stat
import subprocess
from pathlib import Path
from urllib.request import urlretrieve

import pytest
from typer.testing import CliRunner

from fake_vcf.__main__ import app
from tests.test_vcf_cli import GENERATE_CMD

runner = CliRunner()

test_file_parent = Path(__file__).resolve().parent


def vcf_validator():
    vcf_validator_path = test_file_parent / "../vcf_validator/vcf_validator"
    system_platform = platform.system()
    if not vcf_validator_path.exists():
        base_url = (
            "https://github.com/EBIvariation/vcf-validator/releases/download/v0.9.4"
        )

        dl_urls = {
            "Linux": "vcf_validator_linux",
            "Darwin": "vcf_validator_macos",
            "Windows": "vcf_validator.exe",
        }
        vcf_validiator_dl_url = f"{base_url}/{dl_urls[system_platform]}"

        urlretrieve(
            vcf_validiator_dl_url, vcf_validator_path
        )  # nosec CWE-22 should not be a problem
        vcf_validator_path.chmod(vcf_validator_path.stat().st_mode | stat.S_IEXEC)

    return vcf_validator_path


def run_vcf_validator(vcf_file_path, result_path):
    args = ["-r", "text", "-i", f"{vcf_file_path}", "-o", f"{result_path}"]
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
    "cli_args",
    list(
        itertools.product(
            *[
                [["-r", f"{r}"] for r in range(1, 100, 25)],
                [["-s", f"{s}"] for s in range(1, 100, 25)],
                ["--large-format", "--no-large-format"],
                ["--phased", "--no-phased"],
                [["-c", f"chr{c}"] for c in range(1, 23)],
            ]
        )
    ),
)
def test_vcf_file_validation(cli_args: tuple, tmp_path):
    args = [GENERATE_CMD]
    for cli_arg in cli_args:
        if isinstance(cli_arg, list):
            args += cli_arg
        else:
            args += [cli_arg]

    vcf_file_path = tmp_path / f"example_{'_'.join(args)}.vcf"
    args += ["-o", vcf_file_path]

    runner.invoke(app, args=args)

    validator_status, validation_result = run_vcf_validator(
        vcf_file_path=vcf_file_path, result_path=tmp_path
    )

    assert (
        "According to the VCF specification, the input file is valid"
        in validation_result
    )
    assert validator_status.returncode == 0
