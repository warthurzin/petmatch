# Name

xxx

## Requirements

- Before running the project, install the required dependencies. Run the following command:
    - *pip install -r requirements.txt*

## How to Use

- This script can be run from the command line. In the folder src of the project, run the default usage:
    - *python main.py*

**Remark:** 
- The accepted parameters are:
    - *--model_name=<model_name>* (Optional): Name of the model to be used, the default value is 'adalbertojunior/distilbert-portuguese-cased'.
    - *--num_iter<num_iterations>* (Optional): A int value representing the number of iterations. If not, provided, the default value is 1.
    - *--split_mode=<split_mode>* (Optional): Defines Dataset splitting strategy (options: 'Hold-out' and 'K-fold cross-validation'). If not provided, the default value is 'Hold-out'.
    - *--weights=<weights>* (Optional): Proportions for training and validation splits (Format: train_prop, val_prop — test set prop is the remainder, the default is: 0.7, 0.1).
    - *--k_groups=<k_groups>* (Optional): Number of groups for splitting if the split_mode == 'K-fold cross-validation' (default: 8).
    - *-h* or *--help*: Displays the help message with details on how to use the script.