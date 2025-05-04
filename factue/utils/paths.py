from pathlib import Path


def generate_output_from_input_path(
    input_path, input_dir, output_dir, output_suffix=".parquet"
):
    """
    Generate the output path for the given input file.

    Args:
        input_path (str): The path to the input file.
        input_dir (str): The directory containing the input file.
        output_dir (str): The directory where the output file should be saved.

    Returns:
        luigi.LocalTarget: A LocalTarget object representing the output path.
    """

    # Ensure the input and output directories are Path objects
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    # Generate the relative path and replace the suffix with .parquet
    relative_path = Path(input_path).relative_to(input_dir)
    relative_path = relative_path.with_suffix(output_suffix)
    output_path = output_dir / relative_path
    return str(output_path)
