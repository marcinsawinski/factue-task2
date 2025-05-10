import sys
from pathlib import Path

import luigi
import pandas as pd
import numpy as np
from factue.methods.llm_calls import make_call
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.utils.parsers import expand_series_of_dict_lists, last_value
from factue.utils.types import Job

logger = get_logger(__name__)

def dedup_claims(x):
    if isinstance(x, (list, np.ndarray)):
        return list(dict.fromkeys(x.tolist() if isinstance(x, np.ndarray) else x))
    return x  # in case it's NaN or something unexpected

class ImproveClaimTask(BaseLLmTask):
    def _process_df(self, df, llm):
        df["original_index"] = df.index
        cols_to_keep = [
            "text",
            "reference",
            "split",
            "lang",
            "init_part_no",
            "claim_candidate",
            "original_index",
        ]
        cols_to_keep = [x for x in cols_to_keep if x in df.columns]
        df['claim_candidate'] = df['claim_candidate'].apply(dedup_claims)
        df = df[cols_to_keep].explode("claim_candidate")
        df["claim_candidate_order"] = df.groupby(level=0).cumcount() + 1

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
                variables={"post": row["text"], "claim": row["claim_candidate"]},
                max_iterations=self.max_iterations,
            ),
            axis=1,
        )
        df_expanded = expand_series_of_dict_lists(make_call_result)
        df = pd.concat([df, df_expanded], axis=1)
        df["check_result"] = 0
        if "plain_content" in df.columns:
            df["claim_improved"] = df["plain_content"].apply(last_value)

        if "error" in df.columns:
            df["error"] = df["error"].astype(str)
        else:
            df["error"] = None

        return df


class ImproveClaimWrapper(GenericBatchWrapper):

    task_cls = ImproveClaimTask  # ← subclasses must set this to a Luigi Task subclass
    input_dir = Path("data/llm_output/normalization/extract")
    job = Job.NORMALIZATION
    step = "improve"

    def _get_output_id(self):
        return ""

    def _get_input_mask(self):
        # return f"{self.model_name.name}/{self.prompt_version}/{self.prompt_name}/{self.split}/*-{self.lang}/*part_{self.part}.parquet"
        return f"{self.model_name.name}/{self.prompt_version}/{self.prompt_name}/{self.split}/*-{self.lang}/*_{self.part}.parquet"


if __name__ == "__main__":
    get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="ImproveClaimWrapper")
    luigi.run(args)
