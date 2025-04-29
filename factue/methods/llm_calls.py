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
        return response
    else:
        return "Error"


# # Function to run on each row
# def check_claim(llm, layout_version, step_id,:
#     pass
# #     content = template_parts['']
# #     messages = []

# #     if 'system' in
# #     prompt_template = ChatPromptTemplate.from_messages([
# #     SystemMessagePromptTemplate.from_template(prmpt_system + promt_format),
# #     HumanMessagePromptTemplate.from_template(prmpt_user),
# # ])

# #     layout = template["layout"][layout_version]
# #     task = template["task"][task_version]
# #     output = template["output"][output_version]

# #     human_prompt_template = HumanMessagePromptTemplate.from_template(layout)
# #     prompt = human_prompt_template.format(
# #         task=task, output=output, claim=claim, text=text
# #     )
# #     # print(prompt.content)
# #     ai_msg = llm.invoke([prompt])
# #     return ai_msg.content.strip()


# def extract_claim(llm, step_id, prompt_id, variables):
#     template_file = project_root / "factue/methods/prompts/prmpt_extract.json"
#     template = json.load(open(template_file, "r"))

#     layout = template["layout"][layout_version]
#     task = template["task"][task_version]
#     output = template["output"][output_version]

#     human_prompt_template = HumanMessagePromptTemplate.from_template(layout)
#     prompt = human_prompt_template.format(task=task, output=output, text=text)
#     # print(prompt.content)
#     ai_msg = llm.invoke([prompt])
#     return ai_msg.content.strip()
