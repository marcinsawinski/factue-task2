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


class PersuasionDefineTask(BaseLLmTask):
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

        df["technique_name"] = df["technique_id"].apply(lambda x: x.replace("_", " "))

        results = []
        definition_prev = None

        for idx, row in df.iterrows():
            definition_base = row["definition_initial"] if definition_prev is None else definition_prev
            variables = {
                "technique_name": row["technique_name"],
                "definition_base": definition_base,
                "definition_update": row["definition_update"],
            }

            call_result = make_call(
                llm=llm,
                job=self.job,
                step=self.step,
                prompt_name=self.prompt_name,
                prompt_version=self.prompt_version,
                variables=variables,
                max_iterations=self.max_iterations,
            )
            call_result[0]['definition_base'] = definition_base
            raw = call_result[0].get("raw", None)
            logger.info(f"raw: {raw}")
            if raw is None or len(raw)<10:
                definition_prev = definition_base
                logger.info("KEEPING SAME BASE")
            else:
                definition_prev = raw
                logger.info("ADDING NEW BASE")


            logger.info(f"call_result: {call_result}")
            logger.info(f"definition_prev: {definition_prev}")
            results.append(call_result)

        make_call_result = pd.Series(results, index=df.index)
        df_expanded = expand_series_of_dict_lists(make_call_result)
        df = pd.concat([df, df_expanded], axis=1)
        return df


class PersuasionDefineWrapper(GenericBatchWrapper):

    task_cls = (
        PersuasionDefineTask  # ← subclasses must set this to a Luigi Task subclass
    )
    input_dir = Path("data/definitions/persuasion")
    job = Job.PERSUASION
    step = "define"

    def _get_output_id(self):
        return f"{self.model_name.name}/{self.prompt_version}/{self.prompt_name}"

    def _get_input_mask(self):
        return f"{self.part}.parquet"

if __name__ == "__main__":
    logger = get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="PersuasionDefineWrapper")
    luigi.run(args)
