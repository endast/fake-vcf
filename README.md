# fake-vcf

<div align="center">

[![Build status](https://github.com/endast/fake-vcf/workflows/build/badge.svg?branch=master&event=push)](https://github.com/endast/fake-vcf/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/fake-vcf.svg)](https://pypi.org/project/fake-vcf/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/endast/fake-vcf/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![License](https://img.shields.io/github/license/endast/fake-vcf)](https://github.com/endast/fake-vcf/blob/main/LICENSE)
![Coverage Report](assets/images/coverage.svg)

## A fake vcf file generator

</div>

*fake-vcf* generates fake [vcf files](https://en.wikipedia.org/wiki/Variant_Call_Format) for testing purposes.

This is still a work in progress, originally created for the [DeepRVAT](https://github.com/PMBio/deeprvat) project.

## Usage

### Setup

```shell
git clone https://github.com/endast/fake-vcf.git
cd fake-vcf
make poetry-download
make install
```

If you want to write bgzip files instead gzip when writing compressed gzip files use `make install-all`. This
install the optional dependencies.

```shell
git clone https://github.com/endast/fake-vcf.git
cd fake-vcf
make poetry-download
make install-all
```

### Run

By default `fake-vcf` writes to stdout

```shell
poetry run fake-vcf generate -s 2 -r 2
##fileformat=VCFv4.2
##source=VCFake 0.2.2
##FILTER=<ID=PASS,Description="All filters passed">
##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">
##contig=<ID=chr1>
##reference=ftp://ftp.example.com/sample.fa
##INFO=<ID=AF,Number=A,Type=Float,Description="Estimated allele frequency in the range (0,1)">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth; some reads may have been filtered">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Phased Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	S0000001	S0000002
chr1	63	rs143	C	A	96	PASS	DP=10;AF=0.5;NS=2	GT	0|0	0|0
chr1	71	rs31	A	T	37	PASS	DP=10;AF=0.5;NS=2	GT	0|0	0|0

```

You can write to a vcf file by piping the output to a file:

```shell
poetry run fake-vcf generate -s 2 -r 2 > fake_file.vcf
ls -lah
total 1
-rw-r--r--   1 magnus  staff   682B Jul 28 16:48 fake_file.vcf
```

Or let the script write to a file directly using `-o`:

```shell
poetry run fake-vcf generate -s 2 -r 2 -o fake_file.vcf

Writing to file fake_file.vcf
(No compression)
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 50942.96it/s]
Done, data written to fake_file.vcf
ls -lah
total 1
-rw-r--r--   1 magnus  staff   682B Jul 28 16:48 fake_file.vcf
```

And if you want the file compressed add .gz to the file name:
(if you installed using `install-all` the file will be compressde using bgzip, otherwise using gzip).

```shell
poetry run fake-vcf generate -s 2 -r 2 -o fake_file.vcf.gz

Writing to file fake_file.vcf
(No compression)
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 50942.96it/s]
Done, data written to fake_file.vcf
ls -lah
total 2
-rw-r--r--   1 magnus  staff   682B Jul 28 16:56 fake_file.vcf
-rw-r--r--   1 magnus  staff   436B Jul 28 16:57 fake_file.vcf.gz
```

You can also pipe the output to bgzip (or gzip) to compress it.

```shell
poetry run fake-vcf generate -s 2 -r 2 | bgzip > fake_file.vcf.gz
ls -lah
total 1
-rw-r--r--   1 magnus  staff     716 Jan 30 13:38 bgzip.chr.vcf.gz
```

To see all options use --help

```shell
poetry run fake-vcf generate --help                   
                                                                                                                                                                                                                                                                                                                      
 Usage: fake-vcf generate [OPTIONS]                                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                                      
 Generate fake VCF data                                                                                                                                                                                                                                                                                               
 Args:     fake_vcf_path (Path): Path to fake VCF file or None to write to standard output.     num_rows (int): Number of rows.     num_samples (int): Number of samples.     chromosome (str): Chromosome identifier.     seed (int): Random seed for reproducibility.     sample_prefix (str): Prefix for sample    
 names.     phased (bool): Simulate phased genotypes.     large_format (bool): Write large format VCF.     print_version (bool): Flag to print the version of the fake-vcf package.     reference_dir (Path): Path to directory containing imported reference_data.                                                   
                                                                                                                                                                                                                                                                                                                      
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --fake_vcf_path       -o                       PATH     Path to fake vcf file. If the path ends with .gz the file will be gzipped. [default: None]                                                                                                                                                                 │
│ --num_rows            -r                       INTEGER  Nr rows to generate (variants) [default: 10]                                                                                                                                                                                                               │
│ --num_samples         -s                       INTEGER  Nr of num_samples to generate. [default: 10]                                                                                                                                                                                                               │
│ --chromosome          -c                       TEXT     chromosome default chr1 [default: chr1]                                                                                                                                                                                                                    │
│ --seed                                         INTEGER  Random seed to use, default none. [default: None]                                                                                                                                                                                                          │
│ --sample_prefix       -p                       TEXT     Sample prefix ex: SAM =>  SAM0000001    SAM0000002 [default: S]                                                                                                                                                                                            │
│ --phased                  --no-phased                   Simulate phased [default: phased]                                                                                                                                                                                                                          │
│ --large-format            --no-large-format             Write large format vcf [default: large-format]                                                                                                                                                                                                             │
│ --version             -v                                Prints the version of the fake-vcf package.                                                                                                                                                                                                                │
│ --reference-dir-path  -f                       PATH     Path to imported refernce directory. [default: None]                                                                                                                                                                                                       │
│ --help                                                  Show this message and exit.                                                                                                                                                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

### Using a reference fasta file
If you want to use a fasta file as reference when generating the fake vcf files you can use the `fake-vcf import-reference` cmd to prepare the data for usage witn `fake-vcf genererate`.

```shell
poetry run fake-vcf import-reference --help
 Usage: fake-vcf import-reference [OPTIONS] REFERENCE_FILE_PATH                                                                                                                                                                                                                                                       
                                  REFERENCE_STORAGE_PATH                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                                      
 Import reference fasta file and extract specified chromosomes if provided.                                                                                                                                                                                                                                           
 Parameters:     reference_file_path (Path): Path to reference fasta file.     reference_storage_path (Path): Where to store the references.     included_chromosomes (Optional[List[str]], optional): List of chromosomes         to extract from reference. If not specified, all will be imported.                 
 Example:     To import a reference file and extract specific chromosomes:     ```     vcf_reference_import("path/to/reference.fasta", "output/directory", included_chromosomes=["chr1", "chr2"])     ```                                                                                                             
 To import a reference file without extracting specific chromosomes:     ```     vcf_reference_import("path/to/reference.fasta", "output/directory")     ```                                                                                                                                                          
                                                                                                                                                                                                                                                                                                                      
╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    reference_file_path         PATH  Path to reference fasta file. [default: None] [required]                                                                                                                                                                                                                    │
│ *    reference_storage_path      PATH  Where to store the references. [default: None] [required]                                                                                                                                                                                                                   │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --included_chromosomes  -c      TEXT  List of chromosomes to extract from reference, if not specified all will be imported [default: None]                                                                                                                                                                         │
│ --help                                Show this message and exit.                                                                                                                                                                                                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


```


## 🛡 License

[![License](https://img.shields.io/github/license/endast/fake-vcf)](https://github.com/endast/fake-vcf/blob/main/LICENSE)

This project is licensed under the terms of the `MIT` license.
See [LICENSE](https://github.com/endast/fake-vcf/blob/main/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{fake-vcf,
  author = {Magnus Wahlberg},
  title = { A fake vcf file generator },
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/endast/fake-vcf}}
}
```
