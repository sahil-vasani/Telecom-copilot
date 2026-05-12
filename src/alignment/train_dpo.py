import os

os.environ["HF_HOME"] = "D:/huggingface"

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel
from trl import DPOTrainer, DPOConfig

from src.alignment.dpo_utils import load_dpo_dataset


MODEL_PATH = "checkpoints/generator"
OUTPUT_DIR = "checkpoints/dpo_generator"


def main():

    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

    print("Loading generator model...")
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)

    print("Loading DPO dataset...")
    dataset = load_dpo_dataset()

    print(dataset)

    training_args = DPOConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=5e-6,
        num_train_epochs=1,
        logging_steps=5,
        save_steps=50,
        fp16=False,
    )

    trainer = DPOTrainer(
        model=model,
        ref_model=None,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    print("\nStarting DPO training...")
    trainer.train()

    print("\nSaving DPO model...")
    trainer.save_model(OUTPUT_DIR)

    print(f"\nDPO model saved → {OUTPUT_DIR}")


if __name__ == "__main__":
    main()