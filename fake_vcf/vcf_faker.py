from __future__ import annotations

import json
import random
from collections import deque
from pathlib import Path

from fake_vcf import vcf_reference, version


class VirtualVCF:
    def __init__(
        self,
        num_rows: int,
        num_samples: int,
        chromosome: str,
        sample_prefix: str | None = "SAMPLES",
        random_seed: int | None = None,
        phased: bool | None = True,
        large_format: bool | None = True,
        reference_dir: str | Path | None = None,
    ):
        """
        Initialize VirtualVCF object.

        Args:
            num_rows (int): Number of rows.
            num_samples (int): Number of samples.
            chromosome (str): Chromosome identifier.
            sample_prefix (str, optional): Prefix for sample names. Defaults to "SAMPLES".
            random_seed (int, optional): Random seed for reproducibility. Defaults to None.
            phased (bool, optional): Phased or unphased genotypes. Defaults to True.
            large_format (bool, optional): Use large format VCF. Defaults to True.
            reference_dir (str or Path, optional): Path to reference file directory.

        Raises:
            ValueError: If num_samples or num_rows is less than 1.
        """
        self.num_rows = num_rows
        self.rows_remaining = num_rows + 1  # One for the header
        self.num_samples = num_samples
        self.chromosome = chromosome
        self.sample_prefix = sample_prefix
        self.phased = phased
        # Use a per instance seed for reproducibility
        self.random = random.Random(random_seed)
        self.large_format = large_format
        self.reference_dir = Path(reference_dir) if reference_dir else None
        self.reference_file = None
        self.reference_metadata = {}
        self._setup_reference_data()

        self.header = "\n".join(
            [
                "##fileformat=VCFv4.2",
                f"##source=VCFake {version}",
                '##FILTER=<ID=PASS,Description="All filters passed">',
                '##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">',
                f"##contig=<ID={chromosome}>",
                f"##reference=ftp://ftp.example.com/{self.reference_metadata.get('source_reference_file', 'sample.fa')}",
                '##INFO=<ID=AF,Number=A,Type=Float,Description="Estimated allele frequency in the range (0,1)">',
                '##INFO=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth; some reads may have been filtered">',
                '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
                "",
            ]
        )  # VCF file format header

        if self.large_format:
            self.header += "\n".join(
                [
                    '##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allelic depths for the ref and alt alleles in the order listed">',
                    '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth (reads with MQ=255 or with bad mates are filtered)">',
                    '##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">',
                    '##FORMAT=<ID=PL,Number=G,Type=Integer,Description="Phred-scaled genotype Likelihoods">',
                    "",
                ]
            )

        if num_samples < 1 or num_rows < 1:
            raise ValueError("Nr of samples and rows must be greater or equal to 1")

        if self.phased:
            self.sample_values = [
                "0|0",
                "1|0",
                "0|1",
                "1|1",
            ]
            self.sample_value_weights = [
                num_samples * 10,
                int(num_samples / 500),
                int(num_samples / 500),
                int(num_samples / 300),
            ]
        else:
            self.sample_values = [
                "0/0",
                "0/1",
                "1/1",
            ]
            self.sample_value_weights = [
                num_samples * 10,
                int(num_samples / 250),
                int(num_samples / 300),
            ]

        if self.large_format:
            extra_data = [
                "0,30:30:89:913,89,0",
                "0,10:10:49:413,33,0",
                "0,20:20:55:489,89,0",
                "0,40:00:66:726,85,0",
            ]

            self.sample_values = [
                f"{sv}:{self.random.choice(extra_data)}" for sv in self.sample_values
            ]

        self.avail_samples = deque(
            self.random.choices(
                self.sample_values,
                weights=self.sample_value_weights,
                k=self.num_samples,
            )
        )

        # Check so that at lest one sample in avail_samples is not 0|0 or 0/0
        if all(
            [sample.startswith(self.sample_values[0]) for sample in self.avail_samples]
        ):
            selected_sample = random.randint(0, len(self.avail_samples) - 1)

            if self.phased:
                self.avail_samples[selected_sample] = self.avail_samples[
                    selected_sample
                ].replace("0", "1", 1)
            else:
                self.avail_samples[selected_sample] = self.avail_samples[
                    selected_sample
                ].replace("0/0", "0/1", 1)

        self.alleles = ["A", "C", "G", "T"]

        # Generate and sort positions
        self.positions = self.random.sample(
            range(1, self.num_rows * 100), self.num_rows
        )
        self.positions.sort()

        self.current_pos = 0

        self.reference_data = None
        if self.reference_dir:
            self.reference_data = vcf_reference.load_reference_data(
                self.reference_file, memory_map=False
            )
            if self.reference_data.shape[0] < max(self.positions):
                raise ValueError(
                    f"""Max position size {max(self.positions)} is outside the reference which has a max of {len(self.reference_data)}"""
                )

    def __iter__(self):
        """
        Iterates over VirtualVCF object.
        """
        return self

    def __next__(self):
        """
        Retrieves the next VCF data.
        """
        if self.rows_remaining <= 0:
            raise StopIteration
        vcf_data = self._generate_vcf_data()
        self.rows_remaining -= 1
        return vcf_data

    def _generate_vcf_header(self):
        """
        Generates the VCF header.
        """
        # Create a list of column names
        columns = [
            "#CHROM",
            "POS",
            "ID",
            "REF",
            "ALT",
            "QUAL",
            "FILTER",
            "INFO",
            "FORMAT",
        ]

        # Add sample names to the column list
        for i in range(1, self.num_samples + 1):
            columns.append(f"{self.sample_prefix}{i:07d}")

        self.header += "\t".join(columns) + "\n"

        return self.header

    def _get_ref_at_pos(self, position, ref_index):
        """
        Retrieves the reference value at a given position if it exists in reference data
        or returns the allele at the given index.
        """
        if self.reference_data:
            reference_value = vcf_reference.get_ref_at_pos(
                self.reference_data, position - 1
            )
        else:
            reference_value = self.alleles[ref_index]
        return reference_value

    def _generate_vcf_row(self):
        """
        Generates a VCF row.
        """
        ref_index = self.random.randint(0, 3)

        position = self.positions[self.current_pos]
        # Generate random values for each field in the VCF row
        pos = f"{position}"
        vid = f"rs{self.random.randint(1, 1000)}"
        ref = self._get_ref_at_pos(position, ref_index)
        if ref in self.alleles:
            alt = self.alleles[self.alleles.index(ref) - self.random.randint(1, 3)]
        else:
            alt = self.alleles[ref_index - self.random.randint(1, 3)]
        qual = f"{self.random.randint(10, 100)}"
        filt = self.random.choice(["PASS"])
        info = f"DP=10;AF=0.5;NS={self.num_samples}"
        if self.large_format:
            fmt = "GT:AD:DP:GQ:PL"
        else:
            fmt = "GT"

        # Generate random values for each sample by rotating the sample list randomly
        max_rotation = (
            int(self.num_samples / 10) if self.num_samples >= 10 else self.num_samples
        )
        self.avail_samples.rotate(self.random.randint(1, max_rotation))
        samples = self.avail_samples.copy()

        row = (
            "\t".join((self.chromosome, pos, vid, ref, alt, qual, filt, info, fmt))
            + "\t"
        )
        row += "\t".join(samples) + "\n"

        self.current_pos += 1

        return row

    def _setup_reference_data(self):

        if self.reference_dir:
            with open(
                self.reference_dir / vcf_reference.METADATA_FILE_NAME
            ) as metadata_file:
                self.reference_metadata = json.load(metadata_file)

            if self.chromosome not in self.reference_metadata["reference_files"].keys():
                raise ValueError(
                    f"""{self.chromosome} does not exist in the reference data"""
                )

            self.reference_file = (
                self.reference_dir
                / self.reference_metadata["reference_files"][self.chromosome]
            )

    def _generate_vcf_data(self):
        """
        Generates VCF data.
        """
        if self.rows_remaining == self.num_rows + 1:
            vcf_row = self._generate_vcf_header()
        else:
            vcf_row = self._generate_vcf_row()
        return vcf_row

    def __enter__(self):
        """
        Enters the context.
        """

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context.
        """
        pass
