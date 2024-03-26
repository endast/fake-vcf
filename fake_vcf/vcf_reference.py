from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm


def get_ref_at_pos(ref_data, position):
    reference_value = ref_data.take([position])[0][0].as_py()
    return reference_value


def load_reference_data(reference_file, memory_map=True):
    reference_data = pq.read_table(reference_file, memory_map=memory_map)
    return reference_data


def parse_fasta(file_path, include_sequences):
    sequences = []
    include_sequences = set(include_sequences) if include_sequences else set()
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


def import_reference(file_path, output_dir):
    output_dir = Path(output_dir)

    include_sequences = [f"chr{c}" for c in range(1, 23)]
    print(f"Getting sequences from {file_path}\n including {include_sequences}")
    parsed_sequences = parse_fasta(file_path, include_sequences=include_sequences)

    # TODO Write every sequence in loop?
    print(f"\nWriting {len(parsed_sequences)} sequences to parquet\n")
    for parsed_sequence in (pbar := tqdm(parsed_sequences)):
        pbar.set_description(f"Processing {parsed_sequence['id']}")

        parquet_file = output_dir / f"fasta_{parsed_sequence['id']}.parquet"

        table_chr = pa.Table.from_arrays(
            [pa.array(parsed_sequence["sequence"], pa.string())],
            names=[parsed_sequence["id"]],
        )
        pq.write_table(table_chr, parquet_file, compression="zstd")

    print("\nDONE!")
