import sys
from pathlib import Path

import luigi

from factue.methods.llm_calls import make_call
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger


class ExtractClaimTask(BaseLLmTask):
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


class ExtractClaimWrapper(GenericBatchWrapper):

    task_cls = ExtractClaimTask  # ← subclasses must set this to a Luigi Task subclass
    input_dir = Path("data/01_preprocessed")
    step_id = "extract"

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
