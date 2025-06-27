from openai import OpenAI
import json
from secreats_util import get_secret

secret = get_secret()

openai_api_key = json.loads(secret)["openai_api_key"]  
client = OpenAI(api_key=openai_api_key)

def send_request(prompt, model, temperature, top_p, report_id=None, cached_tokens=0):
    # Envia o prompt para a API
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        top_p=top_p,        
        messages=[{"role": "user", "content": prompt}]
    )
    resposta = response.choices[0].message.content

    return resposta

