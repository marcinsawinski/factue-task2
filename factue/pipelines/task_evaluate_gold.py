from pathlib import Path

import luigi
import pandas as pd

from factue.utils.paths import generate_output_path


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
        df = pd.read_parquet(self.input_path)  # type: ignore
        # todo
        df.to_parquet(output_path, index=False)
        print(f"Converted {self.input_path} -> {output_path}")


class PreprocessAll(luigi.WrapperTask):
    def requires(self):

        input_dir = Path("data/parquet/input")
        output_dir = Path("data/parquet/preprocessed")
        return [
            PreprocessTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
            )
            for input_path in input_dir.glob("**/*.parquet")
        ]


if __name__ == "__main__":
    luigi.run(["PreprocessAll", "--local-scheduler"])
