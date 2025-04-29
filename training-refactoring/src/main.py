import sys
from config.config import *
from data.statistical_tools import *
from task_manager import *

PARAMS_LEN = 5 #main.py --model_name=<model_name> --num_iter=<num_iterations> --split_mode=<split_mode> --weights='<weights>' --k_groups=<k_groups>

if __name__ == '__main__':
    params = sys.argv
    
    if '-h' in params or '--help' in params:
        print_help()
        exit(0)

    config = get_configs(params[1:])
    num_iter = config[1]
    config = [config[0]] + config[2:]
    plot = PlotManager()
    global_evaluation_metrics_by_run = []
    
    for iter in range(num_iter):
        print('\nIteration {}\n' .format(iter+1))
        manager = TaskManager(config, plot)
        manager.run_classifier()
        global_evaluation_metrics_by_run.append(manager.evaluator.performance)

    manager.plot.save_all_images()
    print(global_evaluation_metrics_by_run)
    analyser = StatisticalAnalyzer(['accuracy', 'f1', 'precision', 'recall'], global_evaluation_metrics_by_run)
    analyser.print_analysis()
    print('Done!')
    exit(0)