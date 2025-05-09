import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import make_call
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.utils.parsers import (expand_series_of_dict_lists, most_frequent,
                                  normalize_binary_list)
from factue.utils.types import Job

logger = get_logger(__name__)


class CleanupClaimTask(BaseLLmTask):
    def _process_df(self, df, llm):
        df = df  # .head(2).copy()
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
                variables={"post": row["text"], "claim": row["reference"]},
                max_iterations=self.max_iterations,
            ),
            axis=1,
        )
        df_expanded = expand_series_of_dict_lists(make_call_result)
        df = pd.concat([df, df_expanded], axis=1)
        df["check_result"] = 0
        for field in ["complete_mismatch", "media_reference", "added_information"]:
            if field in df.columns:
                df[field] = df[field].apply(normalize_binary_list)
                df[field] = df[field].apply(most_frequent)
                df["check_result"] = df["check_result"] + df[field]

        if "error" in df.columns:
            df["error"] = df["error"].astype(str)
        else:
            df["error"] = None

        return df


class CleanupClaimWrapper(GenericBatchWrapper):

    task_cls = CleanupClaimTask  # ← subclasses must set this to a Luigi Task subclass
    input_dir = Path("data/preprocessed/normalization")
    job = Job.NORMALIZATION
    step = "cleanup"

    def _get_input_mask(self):
        return f"{self.split}/{self.split}-{self.lang}/batch_{self.part}.parquet"


if __name__ == "__main__":
    get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="CleanupClaimWrapper")
    luigi.run(args)
