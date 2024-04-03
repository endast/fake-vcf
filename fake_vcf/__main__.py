from typing import List

import time
from pathlib import Path

import typer
from rich.console import Console

from fake_vcf import version
from fake_vcf.vcf_generator import fake_vcf_data
from fake_vcf.vcf_reference import import_reference

app = typer.Typer(
    name="fake-vcf",
    help="A fake vcf file generator",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """
    Callback function to print the version of the package.

    Args:
        print_version (bool): Flag to print the version.

    Raises:
        Exit: If the print_version flag is set.
    """
    if print_version:
        console.print(f"[yellow]fake-vcf[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.command(name="import-reference")
def vcf_reference_import(
    reference_file_path: Path = typer.Argument(
        help="Path to reference fasta file.",
    ),
    reference_storage_path: Path = typer.Argument(
        help="Where to store the references.",
    ),
    included_chromosomes: List[str] = typer.Option(
        None,
        "--included_chromosomes",
        "-c",
        help="List of chromosomes to extract from reference, if not specified all will be imported",
    ),
) -> None:
    print(f"Importing reference {reference_file_path}")
    if included_chromosomes:
        print(
            f"Importing {len(included_chromosomes)} chromosomes from reference {reference_file_path}: {', '.join(included_chromosomes)}"
        )
    else:
        print(f"Importing all chromosomes from reference {reference_file_path}")

    start_time = time.time()
    import_reference(
        file_path=reference_file_path,
        output_dir=reference_storage_path,
        include_sequences=included_chromosomes,
    )
    end_time = time.time()

    print(f"Reference imported in {end_time - start_time:.2f} seconds.")


@app.command(name="generate")
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
    """
    Main function to generate fake VCF data using Typer CLI.

    Args:
        fake_vcf_path (Path): Path to fake VCF file or None to write to standard output.
        num_rows (int): Number of rows.
        num_samples (int): Number of samples.
        chromosome (str): Chromosome identifier.
        seed (int): Random seed for reproducibility.
        sample_prefix (str): Prefix for sample names.
        phased (bool): Simulate phased genotypes.
        large_format (bool): Write large format VCF.
        print_version (bool): Flag to print the version of the fake-vcf package.
    """
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
    app()  # pragma: no cover
