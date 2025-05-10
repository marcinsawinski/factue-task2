import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import make_call
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.utils.parsers import expand_series_of_dict_lists
from factue.utils.types import Job

logger = get_logger(__name__)


def format_claim_candidates(claims):
    return "\n\n".join(
        f"claim candidate {i + 1}:\n{claim}" for i, claim in enumerate(claims)
    )


class JudgeClaimTask(BaseLLmTask):
    def _process_df(self, df, llm):
        cols_to_keep = [
            "text",
            "reference",
            "split",
            "lang",
            "init_part_no",
            "claim_candidate",
            "claim_improved",
            "original_index",
        ]

        df = df[cols_to_keep]
        cols_to_collapse = ["claim_candidate", "claim_improved"]  # add more if needed
        cols_constant = [col for col in df.columns if col not in cols_to_collapse]
        agg_dict = {col: list for col in cols_to_collapse}
        agg_dict.update({col: "first" for col in cols_constant})

        # Collapse back by original index
        df = df.groupby(df["original_index"]).agg(agg_dict)

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
                variables={
                    "post": row["text"],
                    "claim_candidates": format_claim_candidates(row["claim_candidate"]),
                },
                max_iterations=self.max_iterations,
            )if isinstance(row["claim_candidate"], list) and len(row["claim_candidate"]) > 1 else (
        {'plain_content': row["claim_candidate"][0]} if isinstance(row["claim_candidate"], list) and len(row["claim_candidate"]) == 1
        else {'plain_content': row["claim_candidate"]}),
            axis=1,
        )
        df_expanded = expand_series_of_dict_lists(make_call_result)
        df = pd.concat([df, df_expanded], axis=1)
        if "plain_content" in df.columns:
            df["claim"] = df["plain_content"]

        if "error" in df.columns:
            df["error"] = df["error"].astype(str)
        else:
            df["error"] = None

        return df


class JudgeClaimWrapper(GenericBatchWrapper):

    task_cls = JudgeClaimTask  # ← subclasses must set this to a Luigi Task subclass
    input_dir = Path("data/llm_output/normalization/improve")
    job = Job.NORMALIZATION
    step = "judge"

    def _get_output_id(self):
        return ""

    def _get_input_mask(self):
        return f"{self.model_name.name}/{self.prompt_version}/*/{self.split}/{self.split}-{self.lang}/*part_{self.part}.parquet"


if __name__ == "__main__":
    get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="JudgeClaimWrapper")
    luigi.run(args)
