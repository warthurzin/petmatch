import time
import numpy as np
from itertools import chain
from datasets import load_dataset, DatasetDict, Dataset
from transformers import AutoTokenizer

class DataManager:
    def __init__(self, model_name, folder_path='../data/', file_name='train_txt', file_type='.jsonl', split_mode='Hold-out', weights=[0.7, 0.1], k_groups=8):
        self.model_name = model_name
        self.folder_path = folder_path
        self.file_name = file_name
        self.file_type = file_type
        self.split_mode = split_mode
        self.weights = weights
        self.k_groups= k_groups
        self.build_dataset()

    def load_dataset(self):
        self.dataset = load_dataset('json', data_files=self.folder_path+self.file_name+self.file_type, split='train')
        self.length = len(self.dataset)

    def update_distribution_folds(self):
        self.dataset_eval = self.dataset.select(self.folds_idx[self.k_eval])
        self.dataset_train =  self.dataset.select(list(chain.from_iterable([self.folds_idx[i] for i in range(self.k_groups) if i != self.k_eval])))
        self.dataset_dict =  DatasetDict({'train': self.dataset_train, 'eval': self.dataset_eval, 'test': self.dataset_test})
        print(self.dataset_dict)
        self.k_eval += 1

    def split_dataset(self):
        self.dataset = self.dataset.shuffle(seed=int(time.time()))
        if self.split_mode == 'Hold-out':
            samples_lengths = [int(np.floor(sum(self.weights[:i+1])*self.length)) for i in range(len(self.weights))]
            self.dataset_train, self.dataset_eval, self.dataset_test = [self.dataset.select(range(start_split, end_split)) for
                                                                        start_split, end_split in zip([0] + samples_lengths, samples_lengths+[self.length])]
            self.dataset_dict =  DatasetDict({'train': self.dataset_train, 'eval': self.dataset_eval, 'test': self.dataset_test})
            print(self.dataset_dict)  
        elif self.split_mode == 'K-fold cross-validation':
            self.k_eval = 0
            test_set_length = int((1-sum(self.weights))*self.length)
            eval_train_set_length = self.length-test_set_length
            samples_lengths = [test_set_length + int(np.floor((i/self.k_groups)*eval_train_set_length)) for i in range(self.k_groups+1)]
            self.folds_idx = [range(samples_lengths[i], samples_lengths[i+1]) for i in range(self.k_groups)]
            self.dataset_test = self.dataset.select(range(0, test_set_length))
            self.update_distribution_folds()
        else:
            raise ValueError(f'Invalid split mode: {self.split_mode}. Expected \'Hold-out\' or \'K-fold cross-validation\'.')         

    def tokenize_dataset(self, tokenizer_args = dict(truncation=True, padding=True, max_length=512)):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, do_lower_case=False, use_fast=True, **tokenizer_args)
        tokenize_batch = lambda batch: self.tokenizer(batch['text'], **tokenizer_args)
        self.dataset_dict = {split: ds.map(tokenize_batch, batched=True) for split, ds in self.dataset_dict.items()}

    def build_dataset(self):
        self.load_dataset()
        self.split_dataset()
        self.tokenize_dataset()