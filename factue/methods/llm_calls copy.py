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
    
# registry for task functions
TASKS = {}

def register_task(name):
    """
    Decorator to register a function under a given task name.
    Usage: @register_task('check')
    """
    def decorator(func):
        TASKS[name] = func
        return func
    return decorator

@register_task('check')
def func_check():
    print("Running check…")
    # your check logic here

@register_task('extract')
def func_extract():
    print("Running extract…")
    # your extract logic here

def run_task(task_name, *args, **kwargs):
    """
    Looks up task_name in the TASKS registry and calls it.
    Raises ValueError if no such task is registered.
    """
    try:
        fn = TASKS[task_name]
    except KeyError:
        raise ValueError(f"Unknown task: {task_name!r}") from None
    return fn(*args, **kwargs)

if __name__ == '__main__':
    for task in ('check', 'extract', 'delete'):
        try:
            run_task(task)
        except ValueError as e:
            print(e)