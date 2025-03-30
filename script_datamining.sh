#!/bin/bash

# Set the dataset name
DATASET="my_data"

# Run module usage analysis
python main.py --dataset $DATASET datamine-stage --options '{"num_modules":25}' --path "datamine/module_usage_analysis.py"


echo "module_usage_analysis.py finished"

# Run module correlations analysis
python main.py --dataset $DATASET datamine-stage --options '{"num_modules":20}' --path "datamine/module_correlations_analysis.py"

echo "module_correlations_analysis.py finished"


# Run module transition analysis
python main.py --dataset $DATASET datamine-stage --options '{"num_modules":20}' --path "datamine/module_transition_analysis.py"

echo "module_transition_analysis.py finished"


# Run argument usage analysis
python main.py --dataset $DATASET datamine-stage --options '{"num_arguments":25}' --path "datamine/argument_usage_analysis.py"

echo "argument_usage_analysis.py finished"


# Run loop usage analysis
python main.py --dataset $DATASET datamine-stage --options '{"num_modules":20}' --path "datamine/loop_usage_analysis.py"

echo "loop_usage_analysis.py finished"


# Run strong correlations analysis
python main.py --dataset $DATASET datamine-stage --path "datamine/strong_correlations_analysis.py"

echo "strong_correlations_analysis.py finished"


# Run argument correlations analysis
python main.py --dataset $DATASET datamine-stage --options '{"num_arguments":20}' --path "datamine/argument_correlations_analysis.py"

echo "argument_correlations_analysis.py finished"


# Run when condition usage analysis
python main.py --dataset $DATASET datamine-stage --options '{"num_arguments":20}' --path "datamine/when_usage_analysis.py"

echo "when_usage_analysis.py finished"


# Run module condition analysis (when conditions)
python main.py --dataset $DATASET datamine-stage --options '{"num_modules":25}' --path "datamine/conditions_percentage_analysis.py"

echo "conditions_percentage_analysis.py finished"


echo "All analyses have been executed."
