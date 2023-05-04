
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema



def base_prompt():
    template = """
    Instruction: Act as zapier and find the trigger and actions from the text. 
    If its not a automation task, reply like an automation tool ask for the automation task 
    and reply a sorry message if trigger or actions is outside the app names list

    App names: gmail, google-sheets, google-calendar, github, slack

    Example prompt: Send an email for each new row in a Google Sheet
    Output:
    [
    "trigger":["google-sheets"],
    "action":["gmail"]
    ]

    Prompt: {query}
    """
    # print(template)
    prompt = PromptTemplate(
        input_variables=["query"],
        template=template
    )
    return prompt

def parsed_out():
    response_schemas = [
        ResponseSchema(name="trigger", description="identify the trigger in the prompt and return the name of application as array"),
        ResponseSchema(name="action", description="identify the actions in the prompt and return the name of application as array")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = ChatPromptTemplate(
        messages=[
            "Act as zapier and find the trigger and actions as from the text. App names examples: gmail, google_sheets, google_calendar, github, slack \n{format_instructions}\n{query}"
        ],
        input_variables=["query"],
        partial_variables={"format_instructions": format_instructions}
    )
    return prompt, output_parser


def get_template(template_name):
    if template_name == 'base':
        return base_prompt()
    elif template_name == 'parsed_out':
        return parsed_out()
    else:
        print("Prompt template not found")
        raise Exception("Prompt template not found")

