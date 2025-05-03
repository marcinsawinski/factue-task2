import logging
import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import make_call
from factue.methods.llm_langchain.llm import Llm
from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.utils.paths import generate_output_path
from factue.utils.types import ModelMode, ModelName, ModelProvider


class BaseLLmTask(luigi.Task):
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()
    identifier = luigi.Parameter()
    force = luigi.BoolParameter()
    resource_id = luigi.Parameter()
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
        return {self.resource_id: 1}

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

    def _generate_output_path(self) -> str:
        output_path = Path(self.output().path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path

    def _generate_llm(self) -> str:
        llm_params = {
            "model_name": self.model_name,
            "provider": self.provider,
            "mode": self.mode,
            "temperature": self.temperature,
            "seed": self.seed,
        }

        if self.resource_id and self.resource_id != "NO_PARALLELISM_":
            llm_params.update({"resource_id": self.resource_id})

        return Llm(**llm_params)

    def _process_df(self, df, llm):
        df["result"] = df.apply(
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
        return df

    def run(self):
        output_path = self._generate_output_path()
        llm = self._generate_llm()
        df = pd.read_parquet(str(self.input_path))
        df = self._process_df(df, llm)
        df.to_parquet(output_path, index=True, compression="snappy")
        logging.info(f"Processed {self.input_path} -> {output_path}")
        self.force = False


class GenericBatchWrapper(luigi.WrapperTask):
    """
    A generic Luigi WrapperTask that, given any `task_cls`,
    will glob a batch of inputs and fan out instances of that class.
    """

    # **THIS** is injection point:
    DATA = "data"
    task_cls = None  # ← subclasses must set this to a Luigi Task subclass
    input_dir = None
    step_id = None

    # batch selectors

    lang = luigi.Parameter(default="*")
    split = luigi.Parameter(default="*")
    identifier = luigi.Parameter(default="*")
    part = luigi.Parameter(default="*")
    force = luigi.BoolParameter(default=False)
    resource_type = luigi.Parameter(default="NO_PARALLELISM")
    resource_list = luigi.Parameter(default="_")

    # shared LLM params
    model_name = luigi.EnumParameter(enum=ModelName)
    model_provider = luigi.EnumParameter(enum=ModelProvider)
    model_mode = luigi.EnumParameter(enum=ModelMode)
    prompt_id = luigi.Parameter()
    max_iterations = luigi.IntParameter(default=1)
    mode = luigi.Parameter(default=ModelMode.CHAT)
    temperature = luigi.FloatParameter(default=0.0)
    seed = luigi.IntParameter(default=0)

    def _get_output_id(self):
        return f"{self.model_name}-{self.prompt_id}"

    def _get_input_mask(self):
        return f"{self.DATA}/{self.split}/{self.split}-{self.lang}/batch_{self.part}.parquet"

    def requires(self):
        if self.task_cls is None:
            raise RuntimeError("`task_cls` must be set on the wrapper subclass")
        if self.step_id is None:
            raise RuntimeError("`step_id` must be set on the wrapper subclass")
        if self.input_dir is None:
            raise RuntimeError("`input_dir` must be set on the wrapper subclass")

        output_id = self._get_output_id()
        input_dir = Path(self.input_dir)
        output_dir = Path(self.DATA) / self.step_id / self.version / self.identifier

        for idx, input_path in enumerate(input_dir.glob(self._get_input_mask())):
            yield self.task_cls(
                # the “fixed” I/O shape
                input_path=str(input_path),
                input_dir=input_dir,
                output_dir=output_dir,
                identifier=output_id,
                force=self.force,
                resource_id=self.resource_type
                + self.resource_list[idx % len(self.resource_list)],
                # pass along all the shared LLM params
                model_name=self.model_name,
                provider=self.provider,
                step_id=self.step_id,
                prompt_id=self.prompt_id,
                max_iterations=self.max_iterations,
                mode=self.mode,
                temperature=self.temperature,
                seed=self.seed,
            )


if __name__ == "__main__":
    get_logger()
    args = get_args(sys.argv[1:], wrapper="GenericBatchWrapper")
    luigi.run(args)
