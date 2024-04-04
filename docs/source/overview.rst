Usage
=====

.. _installation:

Installation
------------

To use fake-vcf, first install:

.. code-block:: shell

    git clone https://github.com/endast/fake-vcf.git
    cd fake-vcf
    make poetry-download
    make install

Running
----------------


By default `fake-vcf` writes to stdout

.. code-block::

  poetry run fake-vcf generate -s 2 -r 2
  ##fileformat=VCFv4.2
  ##source=VCFake 0.2.0
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



You can write to a vcf file by piping the output to a file:

.. code-block:: shell

  poetry run fake-vcf generate -s 2 -r 2 > fake_file.vcf
  ls -lah
  total 1
  -rw-r--r--   1 magnus  staff   682B Jul 28 16:48 fake_file.vcf

Or let the script write to a file directly using `-o`:

.. code-block:: shell

  poetry run fake-vcf generate -s 2 -r 2 -o fake_file.vcf

  Writing to file fake_file.vcf
  (No compression)
  100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 50942.96it/s]
  Done, data written to fake_file.vcf
  ls -lah
  total 1
  -rw-r--r--   1 magnus  staff   682B Jul 28 16:48 fake_file.vcf


And if you want the file gzipped add .gz to the file name:

.. code-block:: shell

  poetry run fake-vcf generate -s 2 -r 2 -o fake_file.vcf.gz

  Writing to file fake_file.vcf
  (No compression)
  100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 50942.96it/s]
  Done, data written to fake_file.vcf
  ls -lah
  total 2
  -rw-r--r--   1 magnus  staff   682B Jul 28 16:56 fake_file.vcf
  -rw-r--r--   1 magnus  staff   436B Jul 28 16:57 fake_file.vcf.gz



To see all options use --help

.. code-block:: shell

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
