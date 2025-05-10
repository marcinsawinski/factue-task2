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
                job=self.job,
                step=self.step,
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
    input_dir = Path("data/preprocessed/normalization")
    step_id = "extract"

    def _get_output_id(self):
        return f"{self.model_name}-{self.prompt_id}"

    def _get_input_mask(self):
        return f"{self.input_dir}/{self.split}/{self.split}-{self.lang}/batch_{self.part}.parquet"


if __name__ == "__main__":
    get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="GenericBatchWrapper")
    luigi.run(args)
