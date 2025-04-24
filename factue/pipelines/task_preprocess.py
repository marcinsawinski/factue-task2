from pathlib import Path
import luigi
import pandas as pd
import fasttext
from factue.utils.vars import fasttetxt_model_path

model = fasttext.load_model(fasttetxt_model_path)


class PreprocessTask(luigi.Task):
    version = luigi.Parameter(default="v2", significant=True)
    input_path = luigi.Parameter()
    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    # Define a function to detect language
    def _detect_lang(sel, text):
        if not text or not isinstance(text, str):
            return None
        prediction = model.predict(text)
        return prediction[0][0].replace("__label__", "")

    def output(self):
        relative_path = Path(self.input_path).relative_to(self.input_dir)
        relative_path = relative_path.with_suffix(".parquet")
        output_path = self.output_dir / relative_path
        return luigi.LocalTarget(str(output_path))

    def run(self):
        output_path = Path(self.output().path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.read_parquet(self.input_path)
        df["lang"] = df["post"].apply(self._detect_lang)
        df.to_parquet(output_path, index=False)
        print(f"Converted {self.input_path} -> {output_path}")


class PreprocessAll(luigi.WrapperTask):
    def requires(self):

        input_dir = Path("data/parquet/input")
        output_dir = Path("data/parquet/preprocessed")
        return [
            PreprocessTask(
                input_path=str(input_file),
                input_dir=input_dir,
                output_dir=output_dir,
                version="v3",
            )
            for input_file in input_dir.glob("**/*.parquet")
        ]


if __name__ == "__main__":
    luigi.run(["PreprocessAll", "--local-scheduler"])
