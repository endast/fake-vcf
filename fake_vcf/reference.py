from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm


def parse_fasta(file_path, include_sequences):
    sequences = []
    include_sequences = set(include_sequences)
    with open(file_path) as fasta_file:
        current_sequence = {"id": "", "sequence": []}

        for line in tqdm(fasta_file):
            line = line.strip()

            if line.startswith(">"):  # New sequence header
                parsed_sequences = {seq["id"] for seq in sequences}
                if parsed_sequences == include_sequences:
                    return sequences

                if (
                    current_sequence["id"]
                    and current_sequence["id"] in include_sequences
                ):
                    sequences.append(current_sequence.copy())

                current_sequence = {"id": line[1:].split(" ")[0], "sequence": []}

            elif current_sequence["id"] in include_sequences:
                current_sequence["sequence"].extend(line.upper())

        # Add the last sequence in the file
        if current_sequence["id"] and current_sequence["id"] in include_sequences:
            sequences.append(current_sequence.copy())

    return sequences


def main():
    script_dir = Path(__file__).resolve().parent
    file_path = script_dir / ("../tests/test_data/reference/reference_small.fa")

    include_sequences = [f"chr{c}" for c in range(1, 23)]
    print(f"Getting sequences from {file_path}\n including {include_sequences}")
    parsed_sequences = parse_fasta(file_path, include_sequences=include_sequences)

    # TODO Write every sequence in loop?
    print(f"\nWriting {len(parsed_sequences)} sequences to parquet\n")
    for parsed_sequence in (pbar := tqdm(parsed_sequences)):
        pbar.set_description(f"Processing {parsed_sequence['id']}")

        parquet_file = (
            script_dir / "../reference_fasta" / f"fasta_{parsed_sequence['id']}.parquet"
        )
        table_chr = pa.Table.from_arrays(
            [pa.array(parsed_sequence["sequence"], pa.string())],
            names=[parsed_sequence["id"]],
        )
        pq.write_table(table_chr, parquet_file, compression="zstd")

    print("\nDONE!")


if __name__ == "__main__":
    main()
