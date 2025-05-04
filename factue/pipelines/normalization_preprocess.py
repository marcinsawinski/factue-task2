import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.textual import detect_lang
from factue.utils.paths import generate_output_from_input_path

column_mapping = {
    "normalized claim": "reference",
    "post": "text",
}


class PreprocessRawClefTask(luigi.Task):
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()
    batch_size = luigi.IntParameter(default=100)

    def output(self):  # type: ignore[override]
        output_path = generate_output_from_input_path(
            input_path=self.input_path,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            output_suffix="",
        )
        # Return a directory target instead of a file
        return luigi.LocalTarget(output_path)

    def run(self):
        output_path = Path(self.output().path)
        batch_dir = output_path.with_suffix(
            ""
        )  # Remove suffix if any, to get base name directory
        batch_dir.mkdir(parents=True, exist_ok=True)

        try:
            df = pd.read_csv(str(self.input_path)).rename(columns=column_mapping)
        except Exception as e:
            raise RuntimeError(
                f"Failed to read or rename columns in {self.input_path}: {e}"
            )
        try:
            if "text" in df.columns:
                df[["text_lang", "text_lang_score"]] = df["text"].apply(
                    lambda x: pd.Series(detect_lang(x))
                )
            if "reference" in df.columns:
                df[["reference_lang", "reference_lang_score"]] = df["reference"].apply(
                    lambda x: pd.Series(detect_lang(x))
                )
        except Exception as e:
            raise RuntimeError(f"Failed to detect language for {self.input_path}: {e}")
        # Split dataframe into batches of 100 rows and save each
        for i, start in enumerate(range(0, len(df), self.batch_size)):  # type: ignore
            batch_df = df.iloc[start : start + self.batch_size]  # type: ignore
            batch_file = batch_dir / f"batch_{i:04d}.parquet"
            batch_df.to_parquet(batch_file, index=True, compression="snappy")
        print(f"Converted {self.input_path} -> {batch_dir}")


class PreprocessRawClefTaskAll(luigi.WrapperTask):
    lang = luigi.Parameter(default="*")
    split = luigi.Parameter(default="*")

    def requires(self):
        input_dir = Path("data/raw/clef25")
        output_dir = Path("data/preprocessed/clef25")
        return [
            PreprocessRawClefTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
                batch_size=20,
            )
            for input_path in input_dir.glob(
                f"**/{self.split}/{self.split}-{self.lang}.csv"
            )
        ]


if __name__ == "__main__":
    args = sys.argv[1:]  # Get command line arguments
    luigi.run(["PreprocessRawClefTaskAll", "--local-scheduler"] + args)
