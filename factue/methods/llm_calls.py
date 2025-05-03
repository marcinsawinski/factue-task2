from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)

from factue.methods.prompts import template_lib

SYSTEM_PART_NAME = "system"
USER_PART_NAME = "user"


def make_call(llm, step_id, prompt_id, variables, max_iterations):
    template_parts = template_lib[step_id][prompt_id]
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
