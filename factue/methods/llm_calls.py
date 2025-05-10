import yaml
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)

from factue.utils.logger import get_logger
from factue.utils.parsers import validate_response
from factue.utils.vars import PROJECT_ROOT

logger = get_logger(__name__)

METADATA_PART_NAME = "metadata"
SYSTEM_PART_NAME = "system"
USER_PART_NAME = "user"
SCHEMA_PART_NAME = "schema"
CUMULATED_FIELDS_NAME = "cumulated_fields"
PROMPTS_DIR = "prompts"


def load_template_list(job, step, prompt_version):

    prompt_path = PROJECT_ROOT / PROMPTS_DIR / job / step / prompt_version
    prompt_content_path = prompt_path / "prompt_content"
    # prompt_layout_path = prompt_path / "prompt_layout"

    with open(prompt_content_path.with_suffix(".yaml"), "r") as f:
        prompt_contents = yaml.safe_load(f)

    return prompt_contents


def load_template_parts(job, step, prompt_name, prompt_version):

    prompt_path = PROJECT_ROOT / PROMPTS_DIR / job / step / prompt_version
    prompt_content_path = prompt_path / "prompt_content"
    prompt_layout_path = prompt_path / "prompt_layout"

    with open(prompt_layout_path.with_suffix(".yaml"), "r") as f:
        prompt_layout = yaml.safe_load(f)

    with open(prompt_content_path.with_suffix(".yaml"), "r") as f:
        prompt_contents = yaml.safe_load(f)

    prompt_content = prompt_contents[prompt_name]

    return prompt_layout, prompt_content


def build_prompt(job, step, prompt_name, prompt_version, variables):
    prompt_layout, prompt_content = load_template_parts(
        job, step, prompt_name, prompt_version
    )
    messages = []
    # logger.info(f"prompt_content:{prompt_content}")
    # logger.info(f"prompt_layout:{prompt_layout}")

    if SCHEMA_PART_NAME in prompt_layout:
        json_schema = prompt_layout[SCHEMA_PART_NAME]
    else:
        json_schema = None

    if CUMULATED_FIELDS_NAME in prompt_layout:
        cumulated_fields = prompt_layout[CUMULATED_FIELDS_NAME]
    else:
        cumulated_fields = None

    if SYSTEM_PART_NAME in prompt_layout:
        messages.append(
            SystemMessagePromptTemplate.from_template(prompt_layout[SYSTEM_PART_NAME])
        )
    if USER_PART_NAME in prompt_layout:
        messages.append(
            HumanMessagePromptTemplate.from_template(prompt_layout[USER_PART_NAME])
        )

    if not messages:
        return [{"error": "Invalid template"}]

    prompt_template = ChatPromptTemplate.from_messages(messages)
    placeholders = {**variables, **prompt_content}

    messages = prompt_template.format_messages(**placeholders)
    return messages, json_schema, cumulated_fields


def make_call(
    llm,
    job,
    step,
    prompt_name,
    prompt_version,
    variables,
    max_iterations,
    max_retries=3,
):

    current_variables = variables
    response = []

    for i in range(max_iterations):
        messages, json_schema, cumulated_fields = build_prompt(
            job, step, prompt_name, prompt_version, current_variables
        )

        retries = 0
        if json_schema is None:
            max_retries = 0
        # logger.info(f"Cumulated_fields: {cumulated_fields}")
        while retries <= max_retries:
            try:
                # logger.info(f"Prompt: {messages}")
                raw_msg = llm.invoke(messages)
                raw_content = raw_msg.content.strip()
                validated_msg = validate_response(raw_content, json_schema)
                logger.info(f"is valid: {validated_msg['is_valid']}")
                if validated_msg["is_valid"]:
                    response.append(validated_msg)
                    break  # Exit retry loop if successful
                else:
                    retries += 1

            except Exception as e:
                try:
                    if hasattr(e, "response"):
                        error_json = e.response.json()
                        error_details = error_json.get("error", {})
                        return [validate_response(None, None, error=error_details)]
                except Exception as json_err:
                    logger.warning(f"Could not parse error response JSON: {json_err}")
                logger.exception("Unhandled exception during LLM call")
                return [
                    validate_response(
                        None, None, error="Unhandled exception during LLM call"
                    )
                ]
            logger.info(f"Cumulated_fields: {cumulated_fields}")
        if cumulated_fields is not None:
            no_change_flag = True
            for field_in, field_out in cumulated_fields.items():
                if current_variables[field_in] != validated_msg[field_out]:
                    logger.info(f"REPLACE:{current_variables[field_in]}")
                    logger.info(f"WITH:{validated_msg[field_out]}")
                    current_variables[field_in] = validated_msg[field_out]

                    no_change_flag = False
            if no_change_flag:
                logger.info("BREAK LOOP - no improvements")
                break

        else:
            pass
            # Reached max_retries without success
            # response.append(
            #     validated_msg
            # )  # {'error': f"Failed after {max_retries} retries"})

    return (
        response
        if response
        else [validate_response(None, None, error="Empty response")]
    )
