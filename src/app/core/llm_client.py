from openai import OpenAI
from typing import List
import json
def llm(prompt, llm_model_name = "gpt-4o-mini"):
    base_url = 'https://api.avalai.ir/v1'
    api_key = "aa-gH48KCQ475w3ffeBXXRweoiKcwZORnwxoYYBEjsWOp8nOY93" # aa-...
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    message = [
        {"role": "system", "content": "system message"},
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model=llm_model_name,
        messages=message,
    )

    result = response.choices[0].message.content
    return 200, "successful", result