import requests
import pandas as pd
import time
from datasets import load_dataset

API_URL = "http://127.0.0.1:8000/scan"

def run_evaluation():
    print("Downloading deepset/prompt-injections dataset from Hugging Face...")
    try:
        # Load the dataset
        dataset = load_dataset("deepset/prompt-injections", split="train")
        df = dataset.to_pandas()
        
        # Balance the dataset: 100 benign (0) and 100 malicious (1)
        print("Balancing dataset (100 safe, 100 malicious)...")
        df_safe = df[df['label'] == 0].sample(100, random_state=42)
        df_malicious = df[df['label'] == 1].sample(100, random_state=42)
        
        # Combine and shuffle
        eval_df = pd.concat([df_safe, df_malicious]).sample(frac=1, random_state=42).reset_index(drop=True)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    print(f"Starting evaluation of {len(eval_df)} prompts against local firewall...")
    print("This may take 30-60 seconds depending on your machine.\n")
    
    results = []
    tp = tn = fp = fn = 0
    start_time = time.time()

    for index, row in eval_df.iterrows():
        prompt = row['text']
        true_label = row['label']  # 1 = Malicious, 0 = Safe
        
        try:
            # Send to Firewall
            response = requests.post(API_URL, json={"prompt": prompt})
            response.raise_for_status()
            data = response.json()
            
            # If the firewall blocked or redacted it, it predicted "Malicious" (1)
            # If it allowed it, it predicted "Safe" (0)
            predicted_label = 1 if data["action"] in ["block", "redact"] else 0
            
            # Tally Metrics
            if true_label == 1 and predicted_label == 1:
                tp += 1
                outcome = "True Positive"
            elif true_label == 0 and predicted_label == 0:
                tn += 1
                outcome = "True Negative"
            elif true_label == 0 and predicted_label == 1:
                fp += 1
                outcome = "False Positive (Over-sensitive)"
            elif true_label == 1 and predicted_label == 0:
                fn += 1
                outcome = "False Negative (Missed Threat!)"
                
            results.append({
                "Prompt": prompt,
                "True_Label": "Malicious" if true_label == 1 else "Safe",
                "Predicted_Label": "Malicious" if predicted_label == 1 else "Safe",
                "Action_Taken": data["action"].upper(),
                "Risk_Score": data["risk_score"],
                "Outcome": outcome
            })
            
            # Print a progress indicator every 20 prompts
            if (index + 1) % 20 == 0:
                print(f"Processed {index + 1}/{len(eval_df)} prompts...")
                
        except Exception as e:
            print(f"Error on prompt {index}: {e}")

    total_time = time.time() - start_time
    
    # Calculate Final Metrics
    accuracy = (tp + tn) / len(eval_df) if len(eval_df) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0 # Also known as True Positive Rate
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0 # False Positive Rate
    
    print("\nEvaluation Complete")
    
    # --- Generate CSV Deliverable ---
    results_df = pd.DataFrame(results)
    results_df.to_csv("evaluation_results.csv", index=False)
    print("Saved raw data to 'evaluation_results.csv'")
    
    # --- Generate Markdown Report Deliverable (gen'd with Gemini Pro 3) ---
    report = f"""# Quantitative Evaluation Report: LLM Prompt Firewall

**Date Evaluated:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**Dataset Used:** `deepset/prompt-injections` (Hugging Face)
**Total Prompts Evaluated:** {len(eval_df)} (100 Malicious, 100 Safe)
**Total Evaluation Time:** {total_time:.2f} seconds

## Core Metrics
* **Accuracy:** {accuracy * 100:.2f}% *(Percentage of total correct predictions)*
* **Recall / True Positive Rate (TPR):** {recall * 100:.2f}% *(Percentage of actual attacks successfully caught)*
* **False Positive Rate (FPR):** {fpr * 100:.2f}% *(Percentage of safe prompts accidentally blocked)*
* **Precision:** {precision * 100:.2f}% *(When the firewall flags something, how often is it right?)*

## Confusion Matrix Breakdown
* **True Positives (Attacks Blocked):** {tp}
* **True Negatives (Safe Prompts Allowed):** {tn}
* **False Positives (False Alarms):** {fp}
* **False Negatives (Missed Attacks):** {fn}

## Architecture Notes
This firewall utilizes a multi-layered detection pipeline:
1. **Rule-Based Engine:** High-speed Regex and keyword pattern matching.
2. **Semantic ML Layer:** Hugging Face `DeBERTa` transformer fine-tuned on prompt injections.
3. **Contextual LLM Judge:** Local Ollama instance (`llama3.2`) for advanced behavioral intent analysis.

*Detailed prompt-by-prompt breakdown available in `evaluation_results.csv`.*
"""
    
    with open("Quantitative_Report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("Saved final report to 'Quantitative_Report.md'")

if __name__ == "__main__":
    run_evaluation()