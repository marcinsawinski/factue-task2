import logging
import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import make_call
from factue.methods.llm_langchain.llm import Llm
from factue.utils.paths import generate_output_path
from factue.utils.types import ModelMode, ModelName, ModelProvider


class ExtractClaimTask(luigi.Task):
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()
    identifier = luigi.Parameter()
    force = luigi.BoolParameter()
    resource_id = luigi.Parameter(default="")
    ##
    model_name = luigi.Parameter()
    provider = luigi.Parameter()
    step_id = luigi.Parameter()
    prompt_id = luigi.Parameter()
    max_iterations = luigi.IntParameter()
    mode = luigi.Parameter()
    temperature = luigi.FloatParameter()
    seed = luigi.IntParameter()

    @property
    def resources(self):
        return {self.resource_id:1}

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

        llm_params = {
            "model_name": self.model_name,
            "provider": self.provider,
            "mode": self.mode,
            "temperature": self.temperature,
            "seed": self.seed,
        }

        if self.resource_id and self.resource_id !="NO_PARALLELISM_":
            llm_params.update({"resource_id": self.resource_id})

        llm = Llm(**llm_params)

        df = pd.read_parquet(str(self.input_path))

        df["claim"] = df.apply(
            lambda row: make_call(
                llm=llm,
                step_id=self.step_id,
                prompt_id=self.prompt_id,
                variables={"text": row["text"], "text_lang": row["text_lang"]},
                max_iterations=self.max_iterations,
            ),
            axis=1,
        )
        df["identifier"] = self.identifier
        df.to_parquet(output_path, index=True, compression="snappy")
        logging.info(f"Processed {self.input_path} -> {output_path}")
        self.force = False


class ExtractClaimTaskAll(luigi.WrapperTask):
    lang = luigi.Parameter(default="*")
    split = luigi.Parameter(default="*")
    part = luigi.Parameter(default="*")
    force = luigi.BoolParameter(default=False)
    resource_type = luigi.Parameter(default="NO_PARALLELISM")
    resource_list = luigi.Parameter(default="_")

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
        output_dir = Path(f"data/{self.step_id}/{identifier}")

        return [
            ExtractClaimTask(
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
                identifier=identifier,
                force=self.force,
                resource_id=self.resource_type+self.resource_list[idx%len(self.resource_list)],
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
            for idx,input_path in enumerate(input_dir.glob(
                f"**/{self.split}/{self.split}-{self.lang}/batch_{self.part}.parquet"
            ))
        ]


if __name__ == "__main__":
    # Optional: adjust logging level (DEBUG, INFO, WARNING, ERROR)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Optional: set Luigi-specific logger to DEBUG
    logging.getLogger("luigi-interface").setLevel(logging.INFO)

    args = sys.argv[1:]

    resource_type = None
    resource_list = []
    new_args = args.copy()

    logging.info(f"Provided {args}")
    i = 0
    while i < len(args):
        if args[i] == "--resource-type" and i + 1 < len(args):
            resource_type = args[i + 1]
            i += 2
        elif args[i] == "--resource-list" and i + 1 < len(args):
            resource_list = args[i + 1]
            i += 2
        else:
            i+=1

    if resource_type and resource_list:
        new_args.append(f"--workers={len(resource_list)}")
    luigi_args = ["ExtractClaimTaskAll", "--local-scheduler"] + new_args
    logging.info(f"Start Luigi as {luigi_args}")
    luigi.run(luigi_args)
