import gzip
import sys

import tqdm

from fake_vcf.vcf_faker import VirtualVCF


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
