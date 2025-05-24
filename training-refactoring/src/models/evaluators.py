import torch
import numpy as np
import evaluate
import time
from transformers import DataCollatorWithPadding, Trainer, AutoModelForSequenceClassification, TrainingArguments
from sklearn.metrics import cohen_kappa_score

class Evaluator:
    def __init__(self, model_name, tokenizer, device, dataset, num_labels=5, max_length=512, output_dir='./result'):
        self.model_name = model_name
        self.tokenizer = tokenizer
        self.device = device
        self.dataset = dataset
        self.num_labels = num_labels
        self.max_length = max_length
        self.output_dir = output_dir
        self.run_training_pipeline()
        self.predict()
        self.evaluate_performance()

    def empty_cache(self):
        torch.cuda.empty_cache()

    def start_model(self):
        print('\nModel name: ', self.model_name, '\n')
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=self.num_labels).to(self.device)
        print(f'\nTotal params of the model: {sum(p.numel() for p in self.model.parameters())}\n')
        self.data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)

    def setup_train(self, learning_rate=2e-5, batch_size=8, epochs=8):
        training_args = TrainingArguments(output_dir=self.output_dir,
                                        learning_rate=learning_rate,
                                        per_device_train_batch_size=batch_size,
                                        per_device_eval_batch_size=batch_size,
                                        num_train_epochs=epochs,
                                        no_cuda=(self.device == 'cpu'),
                                        save_strategy='epoch', 
                                        save_total_limit=2)
        self.trainer = Trainer(model=self.model,
                            args=training_args,
                            train_dataset=self.dataset['train'],
                            eval_dataset=self.dataset['eval'],
                            tokenizer=self.tokenizer,
                            data_collator=self.data_collator)
    
    def train(self):
        self.trainer.train()
        print('\nSuccessful training!\n')
        #self.trainer.save_model(self.output_dir)
    
    def predict(self):
        time_start = time.time()
        self.predictions = self.trainer.predict(self.dataset['test'])
        self.total_time = time.time()-time_start
        self.time_by_samples = self.total_time/len(self.predictions.predictions)
        self.preds = np.argmax(self.predictions.predictions, axis=-1)
    
    def evaluate_performance(self, task='mrpc'):
        qwk = cohen_kappa_score(self.predictions.label_ids, self.preds, weights='quadratic')
        self.performance = {'quadratic_kappa': qwk}
        print('\nPerformance results: ', self.performance)
        print(f'\nAverage time by sample: {self.time_by_samples:.6f}s\n')
            
    def run_training_pipeline(self):
        self.empty_cache()
        self.start_model()
        self.setup_train()
        self.train()