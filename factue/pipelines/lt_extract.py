import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import extract_claim
from factue.methods.llm_langchain.llm import Llm
from factue.utils.paths import generate_output_path
from factue.utils.types import ModelMode, ModelName, ModelProvider


class ExtractClaimTask(luigi.Task):
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
        df["claim"] = df.apply(
            lambda row: extract_claim(
                llm=llm,
                layout_version=self.layout_version,
                task_version=self.task_version,
                output_version=self.output_version,
                text=row["text"],
            ),
            axis=1,
        )
        df["identifier"] = self.identifier
        df.to_parquet(output_path, index=True, compression="snappy")
        print(f"Processed {self.input_path} -> {output_path}")


class ExtractClaimTaskAll(luigi.WrapperTask):
    lang = luigi.Parameter(default="*")
    split = luigi.Parameter(default="*")
    part = luigi.Parameter(default="*")

    model_name = luigi.Parameter(default=ModelName.LLAMA_31_8B)
    provider = luigi.Parameter(default=ModelProvider.OLLAMA)
    task_version = luigi.Parameter(default="v001")
    output_version = luigi.Parameter(default="v001")
    layout_version = luigi.Parameter(default="v001")
    mode = luigi.Parameter(default=ModelMode.CHAT)
    temperature = luigi.Parameter(default=0.0)

    def requires(self):

        identifier = f"{self.model_name}-T{self.task_version}-O{self.output_version}"

        input_dir = Path("data/01_preprocessed")
        output_dir = Path(f"data/03_extracted_claims-{identifier}")
        return [
            ExtractClaimTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
                model_name=self.model_name,
                provider=self.provider,
                task_version=self.task_version,
                output_version=self.output_version,
                layout_version=self.layout_version,
                mode=self.mode,
                temperature=self.temperature,
                identifier=identifier,
            )
            for input_path in input_dir.glob(
                f"**/{self.split}/{self.split}-{self.lang}/batch_{self.part}.parquet"
            )
        ]


if __name__ == "__main__":
    args = sys.argv[1:]  # Get command line arguments
    luigi.run(["ExtractClaimTaskAll", "--local-scheduler"] + args)
