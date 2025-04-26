from pathlib import Path

import luigi
import pandas as pd

from factue.utils.paths import generate_output_path


class CleanGroundTruthTask(luigi.Task):
    force = luigi.BoolParameter(default=False)
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    def complete(self):
        if self.force:
            return False
        return self.output().exists()

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
        df = pd.read_parquet(str(self.input_path))
        # todo
        df["gold_check"] = "ok"
        df["gold_check_score"] = 1
        df.to_parquet(output_path, index=False)
        print(f"Converted {self.input_path} -> {output_path}")


class CleanGroundTruthAll(luigi.WrapperTask):
    def requires(self):

        input_dir = Path("data/01_preprocessed")
        output_dir = Path("data/02_cleaned_ground_truth")
        return [
            CleanGroundTruthTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
            )
            for input_path in input_dir.glob("**/*dev*/*eng*/*.parquet")
        ]


if __name__ == "__main__":
    luigi.run(["CleanGroundTruthAll", "--local-scheduler"])
