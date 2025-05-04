import sys
from pathlib import Path

import luigi

from factue.methods.llm_calls import make_call
from factue.pipelines.base_llm_task import BaseLLmTask, GenericBatchWrapper
from factue.utils.args import get_args
from factue.utils.logger import get_logger


class PersuasionDetectTask(BaseLLmTask):
    def _process_df(self, df, llm):
        df["result"] = df.apply(
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
        df["identifier"] = self.identifier
        return df


class PersuasionDetectWrapper(GenericBatchWrapper):

    task_cls = (
        PersuasionDetectTask  # ← subclasses must set this to a Luigi Task subclass
    )
    input_dir = Path("data/preprocessed/persuasion")
    step = "detect"

if __name__ == "__main__":
    get_logger()
    args = get_args(sys.argv[1:], wrapper="PersuasionDetectWrapper")
    luigi.run(args)
