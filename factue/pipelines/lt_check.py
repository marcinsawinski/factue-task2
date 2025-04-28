from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import check_claim
from factue.methods.llm_langchain.llm import Llm
from factue.utils.paths import generate_output_path
from factue.utils.types import ModelMode, ModelName, ModelProvider


class CleanReferenceTask(luigi.Task):
    force = luigi.BoolParameter(default=False)
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    model_name = luigi.Parameter(default=ModelName.LLAMA_31_8B)
    provider = luigi.Parameter(default=ModelProvider.OLLAMA)
    task_version = luigi.Parameter(default="v001")
    output_version = luigi.Parameter(default="v001")
    layout_version = luigi.Parameter(default="v001")
    mode = luigi.Parameter(default=ModelMode.CHAT)
    temperature = luigi.Parameter(default=0.0)
    identifier = luigi.Parameter(default="default")

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

        llm = Llm(
            model_name=self.model_name,  # type: ignore
            provider=self.provider,  # type: ignore
            mode=self.mode,  # type: ignore
            temperature=self.temperature,  # type: ignore
        )

        df = pd.read_parquet(str(self.input_path))
        df["check"] = df.apply(
            lambda row: check_claim(
                llm=llm,
                layout_version="v001",
                task_version="v001",
                output_version="v001",
                text=row["text"],
                claim=row["reference"],
            ),
            axis=1,
        )
        df.to_parquet(output_path, index=False)
        print(f"Converted {self.input_path} -> {output_path}")


class CleanReferenceTaskAll(luigi.WrapperTask):
    def requires(self):

        input_dir = Path("data/01_preprocessed")
        output_dir = Path("data/02_cleaned_reference")
        return [
            CleanReferenceTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
            )
            for input_path in input_dir.glob("**/*dev*/*eng*/*.parquet")
        ]


if __name__ == "__main__":
    luigi.run(["CleanReferenceTaskAll", "--local-scheduler"])
