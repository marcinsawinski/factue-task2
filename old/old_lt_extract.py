import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import make_call
from factue.methods.llm_langchain.llm import Llm
from factue.utils.paths import generate_output_from_input_path
from factue.utils.types import ModelMode, ModelName, ModelProvider


class ExtractClaimTask(luigi.Task):
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()
    identifier = luigi.Parameter()
    force = luigi.BoolParameter()
    ##
    model_name = luigi.Parameter()
    provider = luigi.Parameter()
    step_id = luigi.Parameter()
    prompt_id = luigi.Parameter()
    max_iterations = luigi.IntParameter()
    mode = luigi.Parameter()
    temperature = luigi.FloatParameter()
    seed = luigi.IntParameter()

    def complete(self):
        if self.force:
            return False
        return self.output().exists()

    def output(self):  # type: ignore[override]
        output_path = generate_output_from_input_path(
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
            seed=self.seed,  # type: ignore
        )

        df = pd.read_parquet(str(self.input_path)).head(2)

        df["claim"] = df.apply(
            lambda row: make_call(
                llm=llm,
                step_id=self.step_id,
                prompt_id=self.prompt_id,
                variables={"text": row["text"]},
                max_iterations=self.max_iterations,
            ),
            axis=1,
        )
        df["identifier"] = self.identifier
        df.to_parquet(output_path, index=True, compression="snappy")
        print(f"Processed {self.input_path} -> {output_path}")
        self.force = False


class ExtractClaimTaskAll(luigi.WrapperTask):
    lang = luigi.Parameter(default="*")
    split = luigi.Parameter(default="*")
    part = luigi.Parameter(default="*")
    force = luigi.BoolParameter(default=False)

    model_name = luigi.Parameter(default=ModelName.LLAMA_31_8B)
    provider = luigi.Parameter(default=ModelProvider.OLLAMA)
    step_id = luigi.Parameter(default="extract_task")
    prompt_id = luigi.Parameter(default="extract_001")
    max_iterations = luigi.IntParameter(default=1)
    mode = luigi.Parameter(default=ModelMode.CHAT)
    temperature = luigi.FloatParameter(default=0.0)
    seed = luigi.IntParameter(default=0)

    def requires(self):

        identifier = f"{self.model_name}-{self.step_id}-{self.prompt_id}"
        input_dir = Path("data/01_preprocessed")
        output_dir = Path(f"data/03_extracted_claims/{identifier}")

        return [
            ExtractClaimTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
                identifier=identifier,
                force=self.force,
                ###
                model_name=self.model_name,
                provider=self.provider,
                step_id=self.step_id,
                prompt_id=self.prompt_id,
                max_iterations=self.max_iterations,
                mode=self.mode,
                temperature=self.temperature,
                seed=self.seed,
            )
            for input_path in input_dir.glob(
                f"**/{self.split}/{self.split}-{self.lang}/batch_{self.part}.parquet"
            )
        ]


if __name__ == "__main__":
    args = sys.argv[1:]  # Get command line arguments
    luigi.run(["ExtractClaimTaskAll", "--local-scheduler"] + args)
