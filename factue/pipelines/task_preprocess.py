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

    def output(self):  # type: ignore[override]
        output_path = generate_output_path(
            input_path=self.input_path,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
        )

        return luigi.LocalTarget(output_path)

    def run(self):
        output_path = Path(self.output().path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(self.input_path).rename(columns=column_mapping)  # type: ignore
        if "post" in df.columns:
            df[["post_lang", "post_lang_score"]] = df["post"].apply(
                lambda x: pd.Series(detect_lang(x))
            )
        if "gold" in df.columns:
            df[["gold_lang", "gold_lang_score"]] = df["gold"].apply(
                lambda x: pd.Series(detect_lang(x))
            )
        df.to_parquet(output_path, index=True)
        print(f"Converted {self.input_path} -> {output_path}")


class ConvertAllCSVs(luigi.WrapperTask):
    def requires(self):
        input_dir = Path("data/raw")
        output_dir = Path("data/parquet/input")
        return [
            PreprocessTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
            )
            for input_path in input_dir.glob("**/*.csv")
        ]


if __name__ == "__main__":
    luigi.run(["ConvertAllCSVs", "--local-scheduler"])
