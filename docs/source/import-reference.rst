Import reference
===============

`fake-vcf import-reference`
---------------------------

Import reference fasta file and extract specified chromosomes if provided.

Parameters:
    reference_file_path (Path): Path to reference fasta file.
    reference_storage_path (Path): Where to store the references.
    included_chromosomes (Optional[List[str]], optional): List of chromosomes
        to extract from reference. If not specified, all will be imported.

Example:
    To import a reference file and extract specific chromosomes:
    ::
    vcf_reference_import("path/to/reference.fasta", "output/directory", included_chromosomes=["chr1", "chr2"])

    To import a reference file without extracting specific chromosomes:
    ::
    vcf_reference_import("path/to/reference.fasta", "output/directory")

Usage
-----

.. code-block:: console

    $ fake-vcf import-reference [OPTIONS] REFERENCE_FILE_PATH REFERENCE_STORAGE_PATH

Arguments
---------

* ``REFERENCE_FILE_PATH``: Path to reference fasta file.  [required]
* ``REFERENCE_STORAGE_PATH``: Where to store the references.  [required]

Options
-------

* ``-c, --included_chromosomes TEXT``: List of chromosomes to extract from reference, if not specified all will be imported
* ``--help``: Show this message and exit.
