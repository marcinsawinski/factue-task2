import sys
from pathlib import Path

import luigi
import pandas as pd

from factue.methods.llm_calls import (load_technique_from_template_parts,
                                      make_call)
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.utils.parsers import (extract_all_fields_from_list_of_json_strings,
                                  most_frequent)
from factue.utils.types import Job


class PersuasionDetectTask(BaseLLmTask):
    def _process_df(self, df, llm):
        df["identifier"] = self.identifier
        technique = load_technique_from_template_parts(
            self.job, self.step, self.prompt_id
        )
        df["technique"] = technique
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
        df["gold"] = df["labels_multi"].apply(lambda x: technique in x)

        return df


class PersuasionDetectWrapper(GenericBatchWrapper):

    task_cls = (
        PersuasionDetectTask  # ← subclasses must set this to a Luigi Task subclass
    )
    input_dir = Path("data/preprocessed/persuasion")
    job = Job.PERSUASION
    step = "detect"


if __name__ == "__main__":
    get_logger()
    args = get_args(sys.argv[1:], wrapper="PersuasionDetectWrapper")
    luigi.run(args)
