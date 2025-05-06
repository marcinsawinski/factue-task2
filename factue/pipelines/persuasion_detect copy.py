import sys
from pathlib import Path

import luigi
import pandas as pd
import json

from factue.methods.llm_calls import (load_metadata_from_template_parts,
                                      make_call)
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.parsers import (expand_series_of_dict_lists,
                                  most_frequent,normalize_binary_list)
from factue.utils.types import Job
from factue.utils.logger import get_logger

logger = get_logger(__name__)


class PersuasionDetectTask(BaseLLmTask):
    def _process_df(self, df, llm):
        df = df#.head(2).copy()
        df["output_id"] = self.output_id
        df["prompt_id"] = self.prompt_id
        df["job"] = self.job
        df["step"] = self.step
        df["max_iterations"] = self.max_iterations
        df['temperature'] = self.temperature
        df['max_iterations'] = self.max_iterations
        df['model_provider'] = self.model_provider
        df['model_name'] = self.model_name
        df['model_mode'] = self.model_mode
        metadata = load_metadata_from_template_parts(
            self.job, self.step, self.prompt_id
        )
        technique_id = metadata.get('technique_id', 'missing_metadata')
        df["technique_id"] = technique_id

        schema = {
    "type": "object",
    "properties": {
        "Description": {"type": "string"},
        "Verdict": {"type": "boolean"}
    },
    "required": ["Description", "Verdict"],
    "additionalProperties": True
}
        
        make_call_result = df.apply(
            lambda row: make_call(
                llm=llm,
                job=self.job,
                step=self.step,
                prompt_id=self.prompt_id,
                variables={"text": row["text"], "text_lang": row["text_lang"]},
                max_iterations=self.max_iterations,
                json_schema=schema,
            ),
            axis=1,
        )
        df_expanded = expand_series_of_dict_lists(make_call_result)
        df = pd.concat([df, df_expanded], axis=1)
        if "verdict" in df.columns:
            df['verdict'] = df['verdict'].apply(normalize_binary_list)
        df["pred"] = df["verdict"].apply(most_frequent)
        df["gold"] = df["labels_multi"].apply(lambda x: technique_id in x).apply(normalize_binary_list)

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
