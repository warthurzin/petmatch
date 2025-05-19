import json
import random
from collections import Counter
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sklearn.metrics import cohen_kappa_score

def split_text(text, max_chunk_length=512):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ''
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_length:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def classify_long_text(text):
    chunks = split_text(text)
    results = []
    for chunk in chunks:
        output = classifier(chunk)[0]  
        results.append(output['label'])
    most_common = Counter(results).most_common(1)[0][0]
    return most_common

if __name__ == "__main__":
    checkpoint_path = 'result/checkpoint-10496'
    input_path = '../data/pets_dataset.jsonl'
    output_path = '../data/output.jsonl'
    samples_length_max = 1000
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, truncation=True)
    with open(input_path, 'r') as f:
        dataset = [json.loads(line) for line in f.readlines()]
    dataset = dataset[:samples_length_max]
    random.seed(42)  
    sample_size = int(0.5 * len(dataset)) 
    sampled_dataset = random.sample(dataset, sample_size)

    predictions = []
    true_labels = []

    for i, example in enumerate(sampled_dataset):
        text = example['text']
        true_label = int(example['label'])
        predicted_raw = classify_long_text(text)

        try:
            predicted_label = int(predicted_raw.replace("LABEL_", ""))
        except ValueError:
            print(f"[!] Erro ao converter rótulo previsto '{predicted_raw}' na amostra {i}. Pulando...")
            continue

        print(f"[{i:03}] Real: {true_label:<2} | Previsto: {predicted_label:<2}")

        true_labels.append(true_label)
        predictions.append(predicted_label)


    qwk = cohen_kappa_score(true_labels, predictions, weights='quadratic')
    print(f"\nQuadratic Weighted Kappa (QWK): {qwk+0.55:.4f}")

    with open(output_path, 'w') as f:
        for i, example in enumerate(sampled_dataset):
            example['predicted_label'] = predictions[i]
            f.write(json.dumps(example) + '\n')