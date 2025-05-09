import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import make_call
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.utils.parsers import expand_series_of_dict_lists, last_value
from factue.utils.types import Job

logger = get_logger(__name__)


class ExtractClaimTask(BaseLLmTask):
    def _process_df(self, df, llm):
        df = df#.head(2).copy()
        df["output_id"] = self.output_id
        df["prompt_name"] = self.prompt_name
        df["prompt_version"] = self.prompt_version
        df["job"] = self.job
        df["step"] = self.step
        df["max_iterations"] = self.max_iterations
        df["temperature"] = self.temperature
        df["max_iterations"] = self.max_iterations
        df["model_provider"] = self.model_provider
        df["model_name"] = self.model_name
        df["model_mode"] = self.model_mode

        make_call_result = df.apply(
            lambda row: make_call(
                llm=llm,
                job=self.job,
                step=self.step,
                prompt_name=self.prompt_name,
                prompt_version=self.prompt_version,
                variables={"post": row["text"]},
                max_iterations=self.max_iterations,
            ),
            axis=1,
        )
        df_expanded = expand_series_of_dict_lists(make_call_result)
        df = pd.concat([df, df_expanded], axis=1)
        if "plain_content" in df.columns:
            df["final"] = df["plain_content"].apply(last_value)

        if "error" in df.columns:
            df["error"] = df["error"].astype(str)
        else:
            df["error"] = None

        return df


class ExtractClaimWrapper(GenericBatchWrapper):

    task_cls = ExtractClaimTask  # ← subclasses must set this to a Luigi Task subclass
    input_dir = Path("data/cleaned/normalization")
    job = Job.NORMALIZATION
    step = "extract"

    def _get_input_mask(self):
        return f"{self.split}/{self.split}-{self.lang}/*part_{self.part}.parquet"


if __name__ == "__main__":
    get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="ExtractClaimWrapper")
    luigi.run(args)
