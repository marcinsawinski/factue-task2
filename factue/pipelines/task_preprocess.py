import logging
from datetime import datetime

import duckdb
import luigi
import pandas as pd

from factue.utils.vars import duckdb_file


class PreprocessTextTask(luigi.Task):
    def run(self):
        logger = logging.getLogger("luigi-interface")

        # Fetch sites from the DuckDB database.
        logger.info("Process files")
        with duckdb.connect(duckdb_file) as conn:
            # sites_df = conn.execute(self.SITE_QUERY).df()

    def output(self):
        output_file = path.gfcta.raw_file(
            f"gfcta_results_{datetime.today().strftime("%Y%m%d_%H%M%S")}.jsonl.gz"
        )
        return luigi.LocalTarget(output_file)

    # def resources(self):
    #     return {"webscrapping": 1}


if __name__ == "__main__":
    logger = logging.getLogger("luigi-interface")
    logger.info("Starting the preprocessing task")
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    luigi.build(
        [PreprocessTextTask()],
        local_scheduler=False,
    )
