import json
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
    include_sequences = set(include_sequences) if include_sequences else None
    sequences = []
    with open(file_path) as fasta_file:
        current_sequence = {"id": "", "sequence": []}

        for line in tqdm(fasta_file):
            line = line.strip()

            if line.startswith(">"):  # New sequence header
                if include_sequences is not None:
                    parsed_sequences = {seq for seq in sequences}
                    if parsed_sequences == include_sequences:
                        return

                if current_sequence["id"] and (
                    include_sequences is None
                    or current_sequence["id"] in include_sequences
                ):
                    sequences.append(current_sequence["id"])
                    yield current_sequence.copy()

                current_sequence = {"id": line[1:].split(" ")[0], "sequence": []}

            elif current_sequence["id"] and (
                include_sequences is None or current_sequence["id"] in include_sequences
            ):
                current_sequence["sequence"].extend(line.upper())

        # Add the last sequence in the file
        if current_sequence["id"] and (
            include_sequences is None or current_sequence["id"] in include_sequences
        ):
            sequences.append(current_sequence["id"])
            yield current_sequence.copy()


def import_reference(file_path, output_dir, include_sequences=None):
    output_dir = Path(output_dir)

    if not output_dir.exists():
        print(f"Creating output directory {output_dir}")
        output_dir.mkdir(parents=True)

    if include_sequences:
        print(f"Getting sequences from {file_path}\n including {include_sequences}")
    else:
        print(f"Getting all sequences from {file_path}")

    sequence_metadata_path = output_dir / "sequence_metadata.json"

    parsed_sequences = parse_fasta(file_path, include_sequences=include_sequences)
    sequence_metadata = {"reference_file": file_path.name}

    for parsed_sequence in (pbar := tqdm(parsed_sequences)):
        pbar.set_description(f"Processing {parsed_sequence['id']}")
        parquet_file = output_dir / f"reference_{parsed_sequence['id']}.parquet"
        sequence_metadata[parsed_sequence["id"]] = parquet_file.name

        table_chr = pa.Table.from_arrays(
            [pa.array(parsed_sequence["sequence"], pa.string())],
            names=[parsed_sequence["id"]],
        )
        pq.write_table(table_chr, parquet_file, compression="zstd")

    print(f"\nWriting sequence metadata to {sequence_metadata_path}")
    with open(sequence_metadata_path, "w") as metadata_file:
        json.dump(sequence_metadata, metadata_file, ensure_ascii=False, indent=4)

    print("\nDONE!")
