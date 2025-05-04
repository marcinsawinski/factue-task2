import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import (load_metadata_from_template_parts,
                                      make_call)
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.utils.parsers import (extract_all_fields_from_list_of_json_strings,
                                  most_frequent)
from factue.utils.types import Job


class PersuasionDetectTask(BaseLLmTask):
    def _process_df(self, df, llm):
        df["output_id"] = self.output_id
        df["job"] = self.job
        df["step"] = self.step
        df["prompt_id"] = self.prompt_id
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
        df["raw_result"] = df.apply(
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
        extracted = df["raw_result"].apply(extract_all_fields_from_list_of_json_strings)
        extracted_df = pd.DataFrame(extracted.tolist()).fillna(value=pd.NA)
        df = pd.concat([df, extracted_df], axis=1)
        df["pred"] = df["Verdict"].apply(most_frequent)
        df["gold"] = df["labels_multi"].apply(lambda x: technique_id in x)

        return df


class PersuasionDetectWrapper(GenericBatchWrapper):

    task_cls = (
        PersuasionDetectTask  # ← subclasses must set this to a Luigi Task subclass
    )
    input_dir = Path("data/preprocessed/persuasion")
    job = Job.PERSUASION.value
    step = "detect"


if __name__ == "__main__":
    get_logger()
    args = get_args(sys.argv[1:], wrapper="PersuasionDetectWrapper")
    luigi.run(args)
