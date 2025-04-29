from config.config import *
from data.data_manager import *
from models.evaluators import *
from plot.plot import *

class TaskManager:
    def __init__(self, config, plot):
        self.config = config
        self.plot = plot
        self.initialize_dataset()

    def initialize_dataset(self):
        self.ds = DataManager(self.config[0], split_mode=self.config[1], weights=self.config[2], k_groups=self.config[3])
    
    def initialize_model(self):
        self.evaluator = Evaluator(self.config[0], self.ds.tokenizer, DEVICE, self.ds.dataset_dict)
    
    def run_classifier(self):
        self.initialize_model()
        self.plot.plot_confusion_matrix(['Detection'], [['0', '1']], [[pred] for pred in self.evaluator.preds], [[label] for label in self.evaluator.predictions.label_ids])
        if self.config[1] == 'K-fold cross-validation' and self.ds.k_eval < self.ds.k_groups:
            self.ds.update_distribution_folds()
            self.ds.tokenize_dataset()
            self.run_classifier()
