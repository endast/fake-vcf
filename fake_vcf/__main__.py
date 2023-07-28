from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

from fake_vcf import version
from fake_vcf.vcf_generator import fake_vcf


class Color(str, Enum):
    white = "white"
    red = "red"
    cyan = "cyan"
    magenta = "magenta"
    yellow = "yellow"
    green = "green"


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


"""

@click.command()
@click.option(
    "--fake_vcf_path",
    "-o",
    default=None,
    type=click.Path(exists=False, writable=True, path_type=Path),
)
@click.option("--num_rows", default=10, help="Nr rows to generate (variants)")
@click.option("--num_samples", default=10, help="Nr of num_samples to generate.")
@click.option("--chromosome", default="chr1", help="chromosome default chr1")
@click.option("--seed", default=42, help="Random seed to use")
@click.option(
    "--sample_prefix",
    default="S",
    help="Sample prefix ex: SAM =>  SAM0000001	SAM0000002",
)
@click.option("--phased/--no-phased", default=True, help="Simulate phased")

"""


@app.command(name="")
def main(
    fake_vcf_path: Path = typer.Option(
        None,
        "--fake_vcf_path",
        "-o",
        case_sensitive=False,
        help="Path to fake vcf file.",
    ),
    num_rows: int = typer.Option(),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the fake-vcf package.",
    ),
) -> None:
    fake_vcf(
        fake_vcf_path=fake_vcf_path,
        num_rows=None,
        num_samples=None,
        chromosome=None,
        seed=None,
        sample_prefix=None,
        phased=None,
    )


if __name__ == "__main__":
    app()
