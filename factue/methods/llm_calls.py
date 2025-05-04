import yaml
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)

from factue.utils.vars import PROJECT_ROOT

SYSTEM_PART_NAME = "system"
USER_PART_NAME = "user"
TECHNIQUE_PART_NAME = "technique"
PROMPTS_DIR = "prompts"


def load_template_parts(job, step, prompt_id):
    prompt_template_file = PROJECT_ROOT / PROMPTS_DIR / job / step / prompt_id
    with open(prompt_template_file.with_suffix(".yaml"), "r") as f:
        prompt_defs = yaml.safe_load(f)

    return prompt_defs


def load_technique_from_template_parts(job, step, prompt_id):
    prompt_defs = load_template_parts(job, step, prompt_id)
    return prompt_defs[TECHNIQUE_PART_NAME]


def make_call(llm, job, step, prompt_id, variables, max_iterations):
    template_parts = load_template_parts(job, step, prompt_id)
    messages = []
    if SYSTEM_PART_NAME in template_parts:
        messages.append(
            SystemMessagePromptTemplate.from_template(template_parts[SYSTEM_PART_NAME])
        )
    if USER_PART_NAME in template_parts:
        messages.append(
            HumanMessagePromptTemplate.from_template(template_parts[USER_PART_NAME])
        )

    if messages:
        prompt_template = ChatPromptTemplate.from_messages(messages)
        response = []
        for i in range(max_iterations):
            prompt = prompt_template.invoke(variables)

            ai_msg = llm.invoke(prompt.to_messages())
            response.append(ai_msg.content.strip())
        return list(set(response))
    else:
        return "Error"
