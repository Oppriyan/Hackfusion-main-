from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {"role":"system","content":"You are helpful"},
        {"role":"user","content":"Say hello"}
    ]
)

print(response.choices[0].message.content)