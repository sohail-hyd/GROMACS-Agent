# Fine-tuning status

GROMACS-Agent includes supervised fine-tuning data and a training script for two roles:

1. GromacsWorkerAgent
2. GromacsEvaluatorAgent

## Current data

- GSCF_GromacsWorker_SFT_Alpaca.json: 100 instruction-output records
- GEQS_GromacsEvaluator_SFT_Alpaca.json: 100 instruction-output records

## Training script

fine_tuning/train_sft_trl.py

## Dataset validation commands

python3 fine_tuning/train_sft_trl.py --dataset worker --check-only
python3 fine_tuning/train_sft_trl.py --dataset evaluator --check-only

## Current validation result

- Worker SFT records: 100
- Evaluator SFT records: 100

## Note

Actual fine-tuning should be performed on a GPU environment such as a workstation or Google Colab. The current repository provides fine-tuning-ready datasets and a training script.
