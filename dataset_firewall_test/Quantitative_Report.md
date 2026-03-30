# Quantitative Evaluation Report: LLM Prompt Firewall

**Date Evaluated:** 2026-03-28 17:36:24
**Dataset Used:** `deepset/prompt-injections` (Hugging Face)
**Total Prompts Evaluated:** 200 (100 Malicious, 100 Safe)
**Total Evaluation Time:** 457.74 seconds

## Core Metrics
* **Accuracy:** 70.50% *(Percentage of total correct predictions)*
* **Recall / True Positive Rate (TPR):** 43.00% *(Percentage of actual attacks successfully caught)*
* **False Positive Rate (FPR):** 2.00% *(Percentage of safe prompts accidentally blocked)*
* **Precision:** 95.56% *(When the firewall flags something, how often is it right?)*

## Confusion Matrix Breakdown
* **True Positives (Attacks Blocked):** 43
* **True Negatives (Safe Prompts Allowed):** 98
* **False Positives (False Alarms):** 2
* **False Negatives (Missed Attacks):** 57

## Architecture Notes
This firewall utilizes a multi-layered detection pipeline:
1. **Rule-Based Engine:** High-speed Regex and keyword pattern matching.
2. **Semantic ML Layer:** Hugging Face `DeBERTa` transformer fine-tuned on prompt injections.
3. **Contextual LLM Judge:** Local Ollama instance (`llama3.2`) for advanced behavioral intent analysis.

*Detailed prompt-by-prompt breakdown available in `evaluation_results.csv`.*
