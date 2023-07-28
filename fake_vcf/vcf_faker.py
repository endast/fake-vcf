import random
from collections import deque


class VirtualVCF:
    def __init__(
        self,
        num_rows: int,
        num_samples: int,
        chromosome: str,
        sample_prefix: str = "SAMPLES",
        random_seed: int = 42,
        phased: bool = True,
    ):
        self.num_rows = num_rows
        self.rows_remaining = num_rows + 1  # One for the header
        self.num_samples = num_samples
        self.chromosome = chromosome
        self.sample_prefix = sample_prefix
        self.phased = phased
        random.seed(random_seed)

        self.header = (
            "\n".join(
                [
                    "##fileformat=VCFv4.2",
                    "##source=StegosaurusVCFaker",
                    '##FILTER=<ID=PASS,Description="All filters passed">',
                    '##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">',
                    f"##contig=<ID={chromosome}>",
                    "##reference=ftp://ftp.example.com/sample.fa",
                    '##INFO=<ID=AF,Number=A,Type=Float,Description="Estimated allele frequency in the range (0,1)">',
                    '##INFO=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth; some reads may have been filtered">',
                    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Phased Genotype">',
                ]
            )
            + "\n"
        )  # VCF file format header

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

        self.avail_samples = deque(
            random.choices(
                self.sample_values,
                weights=self.sample_value_weights,
                k=self.num_samples,
            )
        )

        self.alleles = ["A", "C", "G", "T"]

        # Generate and sort positions
        self.positions = random.sample(range(1, self.num_rows * 100), self.num_rows)
        self.positions.sort()

        self.current_pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.rows_remaining <= 0:
            raise StopIteration
        vcf_data = self._generate_vcf_data()
        self.rows_remaining -= 1
        return vcf_data

    def _generate_vcf_header(self):
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

    def _generate_vcf_row(self):
        ref_index = random.randint(0, 3)

        position = self.positions[self.current_pos]
        # Generate random values for each field in the VCF row
        pos = f"{position}"
        vid = f"rs{random.randint(1, 1000)}"
        ref = self.alleles[ref_index]
        alt = self.alleles[ref_index - random.randint(1, 2)]
        qual = f"{random.randint(10, 100)}"
        filt = random.choice(["PASS"])
        info = f"DP=10;AF=0.5;NS={self.num_samples}"
        fmt = "GT"

        # Generate random values for each sample by rotating the sample list randomly
        self.avail_samples.rotate(random.randint(1, int(self.num_samples / 10)))
        samples = self.avail_samples.copy()

        row = (
            "\t".join((self.chromosome, pos, vid, ref, alt, qual, filt, info, fmt))
            + "\t"
        )
        row += "\t".join(samples) + "\n"

        self.current_pos += 1

        return row

    def _generate_vcf_data(self):
        if self.rows_remaining == self.num_rows + 1:
            vcf_row = self._generate_vcf_header()
        else:
            vcf_row = self._generate_vcf_row()
        return vcf_row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
