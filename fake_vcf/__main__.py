from pathlib import Path

import typer
from rich.console import Console

from fake_vcf import version
from fake_vcf.vcf_generator import fake_vcf_data

app = typer.Typer(
    name="fake-vcf",
    help="A fake vcf file generator",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]fake-vcf[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.command(name="fake-vcf")
def main(
    fake_vcf_path: Path = typer.Option(
        None,
        "--fake_vcf_path",
        "-o",
        help="Path to fake vcf file. If the path ends with .gz the file will be gzipped.",
    ),
    num_rows: int = typer.Option(
        10, "--num_rows", "-r", help="Nr rows to generate (variants)"
    ),
    num_samples: int = typer.Option(
        10, "--num_samples", "-s", help="Nr of num_samples to generate."
    ),
    chromosome: str = typer.Option(
        "chr1", "--chromosome", "-c", help="chromosome default chr1"
    ),
    seed: int = typer.Option(None, "--seed", help="Random seed to use, default none."),
    sample_prefix: str = typer.Option(
        "S",
        "--sample_prefix",
        "-p",
        help="Sample prefix ex: SAM =>  SAM0000001	SAM0000002",
    ),
    phased: bool = typer.Option(default=True, help="Simulate phased"),
    large_format: bool = typer.Option(default=True, help="Write large format vcf"),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the fake-vcf package.",
    ),
) -> None:
    fake_vcf_data(
        fake_vcf_path=fake_vcf_path,
        num_rows=num_rows,
        num_samples=num_samples,
        chromosome=chromosome,
        seed=seed,
        sample_prefix=sample_prefix,
        phased=phased,
        large_format=large_format,
    )


if __name__ == "__main__":
    app()
