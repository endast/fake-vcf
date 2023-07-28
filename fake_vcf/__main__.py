from typing import Optional

import gzip
import sys
from enum import Enum
from pathlib import Path
from random import choice

import click
import tqdm
import typer
from rich.console import Console

from fake_vcf import version
from fake_vcf.example import hello
from fake_vcf.vcf_faker import VirtualVCF


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


@app.command(name="")
def main(
    name: str = typer.Option(..., help="Person to greet."),
    color: Optional[Color] = typer.Option(
        None,
        "-c",
        "--color",
        "--colour",
        case_sensitive=False,
        help="Color for print. If not specified then choice will be random.",
    ),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the fake-vcf package.",
    ),
) -> None:
    """Print a greeting with a giving name."""
    if color is None:
        color = choice(list(Color))

    greeting: str = hello(name)
    console.print(f"[bold {color}]{greeting}[/]")


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
def fake_vcf(
    fake_vcf_path, num_rows, num_samples, chromosome, seed, sample_prefix, phased
):
    virtual_vcf = VirtualVCF(
        num_rows=num_rows,
        num_samples=num_samples,
        chromosome=chromosome,
        sample_prefix=sample_prefix,
        random_seed=seed,
        phased=phased,
    )

    if fake_vcf_path is None:
        with virtual_vcf as v_vcf:
            for line in v_vcf:
                sys.stdout.write(line)
        return

    print(f"Writing to file {fake_vcf_path}")

    if fake_vcf_path.suffix == ".gz":
        print("(Using compression)")
        with gzip.open(fake_vcf_path, "wt") as gz_file, virtual_vcf as v_vcf:
            for line in tqdm.tqdm(v_vcf, total=num_rows + 1):
                gz_file.write(line)
    else:
        print("(No compression)")
        with open(
            fake_vcf_path, "w", encoding="utf-8"
        ) as txt_file, virtual_vcf as v_vcf:
            for line in tqdm.tqdm(v_vcf, total=num_rows + 1):
                txt_file.write(line)

    print(f"Done, data written to {fake_vcf_path}")


if __name__ == "__main__":
    app()
