from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "openai-community/gpt2"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID)

# Input prompt
prompt = "Artificial intelligence is"

# Convert text to tokens
inputs = tokenizer(prompt, return_tensors="pt")

# Generate text
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    do_sample=True,
    temperature=0.7
)

# Convert tokens back to text
text = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(text)