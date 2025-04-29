import numpy as np
from scipy.stats import norm

class StatisticalAnalyzer:
    def __init__(self, metric_names, evaluation_metrics):
        self.metric_names = metric_names
        self.evaluation_metrics = evaluation_metrics
        self.calculate_statistical_param()
                
    def calculate_statistical_param(self):
        self.statistical_param_names = ['mean', 'std', 'min', 'max']
        self.statistical_param_funcs = [np.mean, np.std, np.min, np.max]
        self.statistical_params = {}
        for metric_name in self.metric_names:
            metric_values = [run[metric_name] for run in self.evaluation_metrics]
            stats = {param_name: param_func(metric_values) for param_name, param_func in zip(self.statistical_param_names, self.statistical_param_funcs)}
            self.statistical_params[metric_name] = stats

    def print_analysis(self):
        for metric_name in self.metric_names:
            print(f'\nMetric: {metric_name.capitalize()}')
            for param_name in self.statistical_param_names:
                value = self.statistical_params[metric_name][param_name]
                print(f'{param_name.capitalize():<6}: {value:.2%}')