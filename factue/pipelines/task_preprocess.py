from pathlib import Path

import luigi
import pandas as pd

from factue.methods.textual import detect_lang

from factue.utils.paths import generate_output_path

column_mapping = {
    "normalized claim": "gold",
    "post": "post",
}


class PreprocessTask(luigi.Task):
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()
    batch_size = luigi.IntParameter(default=100)

    def output(self):
        output_path = generate_output_path(
            input_path=self.input_path,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )
        # Return a directory target instead of a file
        return luigi.LocalTarget(output_path)

    def run(self):
        output_path = Path(self.output().path)
        batch_dir = output_path.with_suffix(
            ""
        )  # Remove suffix if any, to get base name directory
        batch_dir.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(self.input_path).rename(columns=column_mapping)
        if "post" in df.columns:
            df[["post_lang", "post_lang_score"]] = df["post"].apply(
                lambda x: pd.Series(detect_lang(x))
            )
        if "gold" in df.columns:
            df[["gold_lang", "gold_lang_score"]] = df["gold"].apply(
                lambda x: pd.Series(detect_lang(x))
            )
        # Split dataframe into batches of 100 rows and save each
        
        for i, start in enumerate(range(0, len(df), self.batch_size)):
            batch_df = df.iloc[start : start + self.batch_size]
            batch_file = batch_dir / f"batch_{i:04d}.parquet"
            batch_df.to_parquet(batch_file, index=True, compression="snappy")
        print(f"Converted {self.input_path} -> {batch_dir}")


class PreprocessAll(luigi.WrapperTask):
    def requires(self):
        input_dir = Path("data/clef25")
        output_dir = Path("data/input")
        return [
            PreprocessTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
                batch_size=100,
            )
            for input_path in input_dir.glob("**/*.csv")
        ]


if __name__ == "__main__":
    print('starting preprocessing')
    luigi.run(["PreprocessAll", "--local-scheduler"])
