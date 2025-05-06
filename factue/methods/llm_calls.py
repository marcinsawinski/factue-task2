import yaml
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)
from factue.utils.parsers import validate_response
from factue.utils.vars import PROJECT_ROOT
from factue.utils.logger import get_logger

logger = get_logger(__name__)

METADATA_PART_NAME = "metadata"
SYSTEM_PART_NAME = "system"
USER_PART_NAME = "user"
CONST_PART_NAME = "constants"
PROMPTS_DIR = "prompts"



def load_template_parts(job, step, prompt_id):
    prompt_template_file = PROJECT_ROOT / PROMPTS_DIR / job / step / prompt_id
    with open(prompt_template_file.with_suffix(".yaml"), "r") as f:
        template_parts = yaml.safe_load(f)

    return template_parts


def load_metadata_from_template_parts(job, step, prompt_id):
    template_parts = load_template_parts(job, step, prompt_id)
    return template_parts.get(METADATA_PART_NAME, {})


def make_call(llm, job, step, prompt_id, variables, max_iterations, max_retries=3, json_schema=None):
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

    if not messages:
        return [{'error': "Invalid template"}]

    prompt_template = ChatPromptTemplate.from_messages(messages)
    constants = template_parts.get(CONST_PART_NAME, {})
    placeholders = {**variables, **constants}
    response = []

    for i in range(max_iterations):
        retries = 0
        if json_schema is None:
            max_retries = 0
        while retries <= max_retries:
            try:
                prompt = prompt_template.invoke(placeholders)
                raw_msg = llm.invoke(prompt.to_messages())
                raw_content = raw_msg.content.strip()
                validated_msg = validate_response(raw_content, json_schema)
                logger.info("response is valid: ":validated_msg['is_valid'])
                if validated_msg['is_valid']:
                    response.append(validated_msg)
                    break  # Exit retry loop if successful
                else:
                    retries += 1

            except Exception as e:
                try:
                    if hasattr(e, "response"):
                        error_json = e.response.json()
                        error_details = error_json.get("error", {})
                        return [{'error': error_details}]
                except Exception as json_err:
                    logger.warning(f"Could not parse error response JSON: {json_err}")
                logger.exception("Unhandled exception during LLM call")
                return [{'error': "Unhandled exception during LLM call"}]

        else:
            # Reached max_retries without success
            response.append(validated_msg)#{'error': f"Failed after {max_retries} retries"})

    return response if response else [{'error': "Empty response"}]