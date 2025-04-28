import json

from langchain.prompts import \
    HumanMessagePromptTemplate  # , ChatPromptTemplate

# from factue.methods.llm_langchain.lms import init_lms
# from factue.methods.llm_langchain.ollama import init_ollama
# from factue.methods.llm_langchain.azure_openai import init_azure_openai
from factue.utils.vars import project_root

# from langchain_core.messages import HumanMessage


# "llama3.1:8b"
# "deepseek-r1:8b"
# llm = init_ollama(model="llama3.1:8b", temperature=0.0, mode="chat")
# llm = init_azure_openai(temperature=0.0, mode="chat")
# json_file = project_root / "factue/methods/prompts/check_claim.json"
# check_claim_templates = json.load(open(json_file, "r"))


# Function to run on each row
def check_claim(llm, layout_version, task_version, output_version, text, claim):
    template_file = project_root / "factue/methods/prompts/prmpt_check.json"
    template = json.load(open(template_file, "r"))

    layout = template["layout"][layout_version]
    task = template["task"][task_version]
    output = template["output"][output_version]

    human_prompt_template = HumanMessagePromptTemplate.from_template(layout)
    prompt = human_prompt_template.format(
        task=task, output=output, claim=claim, text=text
    )
    # print(prompt.content)
    ai_msg = llm.invoke([prompt])
    return ai_msg.content.strip()


def extract_claim(llm, layout_version, task_version, output_version, text):
    template_file = project_root / "factue/methods/prompts/prmpt_extract.json"
    template = json.load(open(template_file, "r"))

    layout = template["layout"][layout_version]
    task = template["task"][task_version]
    output = template["output"][output_version]

    human_prompt_template = HumanMessagePromptTemplate.from_template(layout)
    prompt = human_prompt_template.format(task=task, output=output, text=text)
    # print(prompt.content)
    ai_msg = llm.invoke([prompt])
    return ai_msg.content.strip()
