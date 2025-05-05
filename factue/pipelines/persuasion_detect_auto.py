import sys
from pathlib import Path

import luigi

from factue.utils.args import get_args
from factue.utils.logger import get_logger
from factue.pipelines.persuasion_detect import PersuasionDetectWrapper


if __name__ == "__main__":
    get_logger()
    args = get_args(sys.argv[1:], wrapper="PersuasionDetectWrapper")
   

    base_path = Path("prompts/persuasion/detect")
    yaml_files = list(base_path.rglob("*.yaml"))

    for file in yaml_files:
        prompt_id = str(file.relative_to(base_path))
        print("*"*50,prompt_id,"*"*50,sep='\n')
        print(args+['--prompt-id', prompt_id])
        luigi.run(args+['--prompt-id', prompt_id])
    
