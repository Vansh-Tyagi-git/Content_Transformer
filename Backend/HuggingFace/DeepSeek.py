from huggingface_hub import InferenceClient

HF_TOKEN = "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"

client = InferenceClient(
    api_key=HF_TOKEN
)

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3-0324",
    messages=[
        {
            "role": "user",
            "content": "Hello! Explain artificial intelligence in one sentence."
        }
    ],
    max_tokens=100
)

print(response.choices[0].message.content)