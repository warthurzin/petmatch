from config.config import *
from data.data_manager import *
from models.evaluators import *

class TaskManager:
    def __init__(self, config):
        self.config = config
        self.initialize_dataset()

    def initialize_dataset(self):
        self.ds = DataManager(self.config[0], split_mode=self.config[1], weights=self.config[2], k_groups=self.config[3])
    
    def initialize_model(self):
        self.evaluator = Evaluator(self.config[0], self.ds.tokenizer, DEVICE, self.ds.dataset_dict)
    
    def run_classifier(self):
        self.initialize_model()
        if self.config[1] == 'K-fold cross-validation' and self.ds.k_eval < self.ds.k_groups:
            self.ds.update_distribution_folds()
            self.ds.tokenize_dataset()
            self.run_classifier()
