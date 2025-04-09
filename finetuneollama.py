import os
import torch
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
# Set device (Use GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model and output directory
MODEL_NAME = "meta-llama/Llama-3.2-3B"  # LLaMA 3.2 3B model
OUTPUT_DIR = "./finetuned_llama32_3b"

# LoRA parameters
LORA_ALPHA = 16
LORA_DROPOUT = 0.1
LORA_R = 8

# Training parameters
MAX_SEQ_LEN = 512
BATCH_SIZE = 1  # Adjust based on VRAM availability
GRAD_ACCUMULATION_STEPS = 16
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3

# Hugging Face Token (Ensure you are logged in or pass your token securely)
HF_TOKEN = os.getenv("HF_TOKEN")  # Set this in your environment for security
if not HF_TOKEN:
    raise ValueError("Hugging Face token is required. Set it using 'export HF_TOKEN=your_token'")

# Load Excel dataset
EXCEL_FILE_PATH = "D:/LLM/SOP_Log_Verification_Dataset.xlsx"  # Update with your Excel file path
df = pd.read_excel(EXCEL_FILE_PATH)
print(f"Loaded dataset with {len(df)} rows and columns: {df.columns.tolist()}")

# Validate required columns
required_columns = {"Instruction", "Input", "Output"}
if not required_columns.issubset(df.columns):
    raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")

# Convert pandas DataFrame to Hugging Face Dataset
train_dataset = Dataset.from_pandas(df)

# Configure 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
# Ensure the tokenizer has a padding token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token  # Use the EOS token as the pad token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    use_auth_token=HF_TOKEN
)

# Prepare model for QLoRA training
model = prepare_model_for_kbit_training(model)

# Configure LoRA
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
)

# Apply LoRA
tuned_model = get_peft_model(model, lora_config)

tuned_model.print_trainable_parameters()

# Function to format dataset
def format_instruction_dataset(examples):
    formatted_prompts = []
    for instruction, input_text, output_text in zip(
        examples["Instruction"], examples["Input"], examples["Output"]
    ):
        input_text = input_text if isinstance(input_text, str) else ""
        prompt = (
            f"<|system|>\nYou are a helpful assistant.\n"
            f"<|user|>\n{instruction}\n{input_text}\n"
            f"<|assistant|>\n{output_text}"
            if input_text else
            f"<|system|>\nYou are a helpful assistant.\n"
            f"<|user|>\n{instruction}\n"
            f"<|assistant|>\n{output_text}"
        )
        formatted_prompts.append(prompt)

    tokenized_inputs = tokenizer(
        formatted_prompts,
        truncation=True,
        max_length=MAX_SEQ_LEN,
        padding="max_length",
        return_tensors="pt"
    )
    tokenized_inputs["labels"] = tokenized_inputs["input_ids"].clone()
    return tokenized_inputs

# Prepare dataset
tokenized_dataset = train_dataset.map(
    format_instruction_dataset,
    batched=True,
    remove_columns=train_dataset.column_names
)

# Configure training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUMULATION_STEPS,
    learning_rate=LEARNING_RATE,
    num_train_epochs=NUM_EPOCHS,
    logging_steps=10,
    save_steps=100,
    save_total_limit=3,
    fp16=True,
    remove_unused_columns=False,
    report_to="none"
)

# Data collator for causal LM
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Create trainer
trainer = Trainer(
    model=tuned_model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator
)

# Start training
trainer.train()

# Save the fine-tuned model
tuned_model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Model saved to:", OUTPUT_DIR)
print("Now you need to create an Ollama model from the saved adapter.")
