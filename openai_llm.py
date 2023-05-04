
import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from prompt import get_template
from dotenv import load_dotenv
import time

load_dotenv()

def get_openai_result(query, template_name, max_attempts=4, retry_interval=15):
    """
    Method to get the OpenAI results
    """

    prompt = get_template(template_name)

   

    attempts = 0
    while attempts < max_attempts:
        try:
            gen_prompt = prompt.format(query=query)
            # print(gen_prompt)
            llm = ChatOpenAI(max_tokens=1024, temperature=0.5, model_name='gpt-4')
            chain = LLMChain(llm=llm, prompt=prompt)
            result = chain.run(query)
            return result
        except Exception as e:
            attempts += 1
            print(f"Attempt {attempts} failed. Retrying in {retry_interval} seconds. Error: {e}")
            time.sleep(retry_interval)

    raise RuntimeError("Failed to get OpenAI result after maximum number of attempts.")
