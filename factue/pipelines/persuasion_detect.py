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


class PersuasionDetectTask(BaseLLmTask):
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
                variables={"text": row["text"], "text_lang": row["text_lang"]},
                max_iterations=self.max_iterations,
            ),
            axis=1,
        )
        df_expanded = expand_series_of_dict_lists(make_call_result)
        df = pd.concat([df, df_expanded], axis=1)
        if "verdict" in df.columns:
            df["verdict"] = df["verdict"].apply(normalize_binary_list)
            df["pred"] = df["verdict"].apply(most_frequent)

        if "label_multi" in df.columns:
            df["gold"] = (
                df["label_multi"]
                .apply(lambda x: self.prompt_name in x)
                .apply(normalize_binary_list)
            )
        if "error" in df.columns:
            df['error']=df['error'].astype(str)

        return df


class PersuasionDetectWrapper(GenericBatchWrapper):

    task_cls = (
        PersuasionDetectTask  # ← subclasses must set this to a Luigi Task subclass
    )
    input_dir = Path("data/preprocessed/persuasion")
    job = Job.PERSUASION.value
    step = "detect"


if __name__ == "__main__":
    logger = get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="PersuasionDetectWrapper")
    luigi.run(args)
