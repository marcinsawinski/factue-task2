import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import make_call,load_template_parts
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.utils.parsers import expand_series_of_dict_lists, last_value
from factue.utils.types import Job

logger = get_logger(__name__)


class PersuasionDefineTask(BaseLLmTask):
    def _process_df(self, df, llm):
        cols_to_keep = [
            "text",
            "reference",
            "claim",
            "split",
            "lang",
        ]
        logger.info(f'columns: {df.columns}')
        cols_to_keep = [x for x in cols_to_keep if x in df.columns]
        df=df[cols_to_keep].copy()
        _, prompt_content = load_template_parts(job=self.job, step="extract", prompt_name='default', prompt_version='v001')
        definition_base = prompt_content.get('instructions')

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

        results = []
        definition_prev = definition_base

        for _, row in df.iterrows():

            variables = {
                "text": row["text"],
                "reference": row["reference"],
                "claim": row["claim"],
                "instructions_base": definition_prev,
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
            
            raw = call_result[0].get("raw", None)
            call_result[0]["definition_base"] = definition_base
            call_result[0]["definition_prev"] = definition_prev
            # logger.info(f"raw: {raw}")
            if raw is None or len(raw) < 10:
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
        logger.info(f'columns after: {df.columns}')
        df['definition_update'] = df['raw'].apply(last_value)
        return df


class PersuasionDefineWrapper(GenericBatchWrapper):

    task_cls = (
        PersuasionDefineTask  # ← subclasses must set this to a Luigi Task subclass
    )
    input_dir = Path("data/llm_output/normalization/judge")
    job = Job.NORMALIZATION
    step = "define"

    def _get_output_id(self):
        return ""

    def _get_input_mask(self):
        return f"{self.model_name.name}/{self.prompt_version}/*/{self.split}/{self.split}-{self.lang}/*_{self.part}.parquet"


if __name__ == "__main__":
    logger = get_logger(__name__)
    args = get_args(sys.argv[1:], wrapper="PersuasionDefineWrapper")
    luigi.run(args)
