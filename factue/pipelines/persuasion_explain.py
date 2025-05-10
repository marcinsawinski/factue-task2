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


class PersuasionExplainTask(BaseLLmTask):
    def _process_df(self, df, llm):
        technique_id = self.prompt_name
        technique_name = technique_id.replace("_", " ")
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

        df["gold"] = (
            df["label_multi"]
            .apply(lambda x: self.prompt_name in x)
            .apply(normalize_binary_list)
        )

        yes = f"Yes, the {technique_name} technique is used in the input."
        no = f"No, the {technique_name} technique is not used in the input."
        df["gold_text"] = df["gold"].apply(lambda x: yes if x else no)
        df["spans"] = df[technique_id].apply(lambda x: f'"{" ".join(x)}"')

        make_call_result = df.apply(
            lambda row: make_call(
                llm=llm,
                job=self.job,
                step=self.step,
                prompt_name=self.prompt_name,
                prompt_version=self.prompt_version,
                variables={
                    "text": row["text"],
                    "gold_text": row["gold_text"],
                    "spans": row["spans"],
                },
                max_iterations=self.max_iterations,
            ),
            axis=1,
        )
        df_expanded = expand_series_of_dict_lists(make_call_result)
        df = pd.concat([df, df_expanded], axis=1)
        if "verdict" in df.columns:
            df["verdict"] = df["verdict"].apply(normalize_binary_list)
            df["pred"] = df["verdict"].apply(most_frequent)

        return df


class PersuasionExplainWrapper(GenericBatchWrapper):

    task_cls = (
        PersuasionExplainTask  # ← subclasses must set this to a Luigi Task subclass
    )
    input_dir = Path("data/preprocessed/persuasion")
    job = Job.PERSUASION
    step = "explain"


if __name__ == "__main__":
    logger = get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="PersuasionExplainWrapper")
    luigi.run(args)
