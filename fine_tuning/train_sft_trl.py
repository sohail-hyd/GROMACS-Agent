import argparse
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]

DATASETS = {
    "worker": BASE / "fine_tuning" / "GSCF_GromacsWorker_SFT_Alpaca.json",
    "evaluator": BASE / "fine_tuning" / "GEQS_GromacsEvaluator_SFT_Alpaca.json",
}


def load_alpaca(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError("Dataset must be a list of Alpaca records.")
    required = {"instruction", "input", "output"}
    for i, item in enumerate(data):
        missing = required - set(item)
        if missing:
            raise ValueError(f"Record {i} missing keys: {missing}")
    return data


def format_record(item):
    return (
        "### Instruction:\n"
        + item["instruction"].strip()
        + "\n\n### Input:\n"
        + item["input"].strip()
        + "\n\n### Response:\n"
        + item["output"].strip()
    )


def check_dataset(name, path):
    data = load_alpaca(path)
    texts = [format_record(x) for x in data]
    lengths = [len(x.split()) for x in texts]
    print(f"Dataset: {name}")
    print(f"Path: {path}")
    print(f"Records: {len(data)}")
    print(f"Min words: {min(lengths)}")
    print(f"Max words: {max(lengths)}")
    print(f"Average words: {sum(lengths) / len(lengths):.1f}")
    print("\nFirst formatted example preview:\n")
    print(texts[0][:1200])


def train(args):
    import torch
    from datasets import Dataset
    from transformers import TrainingArguments
    from trl import SFTTrainer

    path = DATASETS[args.dataset]
    records = load_alpaca(path)
    formatted = [{"text": format_record(x)} for x in records]

    dataset = Dataset.from_list(formatted)
    split = dataset.train_test_split(test_size=args.eval_ratio, seed=42)

    bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    fp16 = torch.cuda.is_available() and not bf16

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        logging_steps=5,
        save_steps=50,
        eval_steps=50,
        save_total_limit=2,
        fp16=fp16,
        bf16=bf16,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=args.model,
        args=training_args,
        train_dataset=split["train"],
        eval_dataset=split["test"],
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    print(f"Saved fine-tuned model/adapters to: {args.output_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["worker", "evaluator"], required=True)
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--output-dir", default="fine_tuning/outputs/gromacs_sft")
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--eval-ratio", type=float, default=0.1)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    path = DATASETS[args.dataset]

    if args.check_only:
        check_dataset(args.dataset, path)
        return

    train(args)


if __name__ == "__main__":
    main()
