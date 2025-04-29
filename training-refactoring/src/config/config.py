import torch

PARAMETERS_NAME = ['--model_name', '--num_iter', '--split_mode', '--weights', '--k_groups']
DEFAULT_VALUES = ['adalbertojunior/distilbert-portuguese-cased', 1, 'Hold-out', [0.7, 0.1], 8]
TYPES = ['string', 'int', 'string', 'list', 'int']
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print('\nDEVICE: ', DEVICE, '\n')

def print_help():
    print('\nUsage: python main.py [OPTIONS]\n')
    print('Options:')
    print('--model_name <string>       Name of the model to be used (default: \'adalbertojunior/distilbert-portuguese-cased\')')
    print('--num_iter <int>            Number of iterations (default: 1)')
    print('--split_mode <string>       Dataset splitting strategy (options: \'Hold-out\', \'K-fold cross-validation\', etc. - default: \'Hold-out\')')
    print('--weights <list<float>>     Proportions for training and validation splits (Format: train_prop, val_prop — test set prop is the remainder - default: 0.7, 0.1)')
    print('--k_groups <int>            Number of groups for splitting if the split_mode == \'K-fold cross-validation\' (default: 8)')
    print('-h or --help                Show this help message and exit.\n')

def print_error(error):
    if error == True:
        print_help()
        exit(1)

def set_parameter(args, param_name, default_value, type):
    param = None
    for arg in args:
        if arg.startswith(param_name):
            if type == 'int':
                param = int(arg.split('=')[1])
            elif type == 'float':
                param = float(arg.split('=')[1])
            elif type == 'bool':
                param = bool(arg.split('=')[1])
            elif type == 'string':
                param = str(arg.split('=')[1])
            else:
                param = list(map(float, arg.split('=')[1].split(',')))
    return param if param is not None else default_value

def get_configs(args):
    return [set_parameter(args, parameter_name, default_value, s_type) for parameter_name, default_value, s_type in zip(PARAMETERS_NAME, DEFAULT_VALUES, TYPES)]