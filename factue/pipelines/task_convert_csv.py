from pathlib import Path

import luigi
import pandas as pd


class ConvertCSVToParquetTask(luigi.Task):
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    def output(self):

        relative_path = Path(self.input_path).relative_to(self.input_dir)
        relative_path = relative_path.with_suffix(".parquet")
        output_path = self.output_dir / relative_path
        return luigi.LocalTarget(str(output_path))

    def run(self):
        output_path = Path(self.output().path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.read_csv(self.input_path)
        df.to_parquet(output_path, index=False)
        print(f"Converted {self.input_path} -> {output_path}")


class ConvertAllCSVs(luigi.WrapperTask):
    def requires(self):
        input_dir = Path("data/raw")
        output_dir = Path("data/parquet/input")
        return [
            ConvertCSVToParquetTask(
                input_path=str(input_file),
                input_dir=input_dir,
                output_dir=output_dir,
            )
            for input_file in input_dir.glob("**/*.csv")
        ]


if __name__ == "__main__":
    luigi.run(["ConvertAllCSVs", "--local-scheduler"])
