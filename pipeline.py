# main.py
import sys
import tFood.evaluate_CEA as tfood_evaluate_CEA
import tFood.CEA_Tfood_third_experiment as CEA_Tfood_third_experiment
import tFood.CEA_Tfood_first_experiment as CEA_Tfood_first_experiment
import BioDiv.evaluate_CEA as biodiv_evaluate_CEA
import BioDiv.CEA_BioDiv_third_experiment as CEA_BioDiv_third_experiment
import BioDiv.CEA_BioDiv_second_experiment as CEA_BioDiv_second_experiment
import BioDiv.CEA_BioDiv_first_experiment as CEA_BioDiv_first_experiment
import Wikidata.evaluate_CEA as wikidata_evaluate_CEA
import Wikidata.CEA_Wikidata_third_experiment as CEA_Wikidata_third_experiment
import Wikidata.CEA_Wikidata_second_experiment as CEA_Wikidata_second_experiment
import Wikidata.CEA_Wikidata_first_experiment as CEA_Wikidata_first_experiment

# Following are some imortant pipeline functions 
def run_experiment(dataset, experiment):
    # Check if dataset and experiment arguments are provided and have valid values
    # Add your valid dataset names
    valid_datasets = ["wikidata", "biodiv", "tfood"]
    # Add your valid experiment names
    valid_experiments = ["first", "second", "third"]

    if dataset not in valid_datasets:
        print(
            f"Invalid dataset. Valid datasets are: {', '.join(valid_datasets)}")
        sys.exit(1)

    if experiment not in valid_experiments:
        print(
            f"Invalid experiment. Valid experiments are: {', '.join(valid_experiments)}")
        sys.exit(1)

    if dataset == "wikidata":
        print("Performing annotation for Wikidata Tables")
        if experiment == 'first':
            # Call the function from your script
            CEA_Wikidata_first_experiment.annotate_cells()
        elif experiment == 'second':
            # Call the function from your script
            CEA_Wikidata_second_experiment.annotate_cells()
        elif experiment == 'third':
            # Call the function from your script
            CEA_Wikidata_third_experiment.annotate_cells()

        print("Performing Evaluation")
        experiment_file = f"Dataset/output/cea annotation/cea_wikidata_{experiment}_experiment.csv"
        wikidata_evaluate_CEA.run(experiment_file)

    elif dataset == "biodiv":
        print("Performing annotation for BioDiversity Tables")
        if experiment == 'first':
            # Call the function from your script
            CEA_BioDiv_first_experiment.annotate_cells()
        elif experiment == 'second':
            # Call the function from your script
            CEA_BioDiv_second_experiment.annotate_cells()
        elif experiment == 'third':
            # Call the function from your script
            CEA_BioDiv_third_experiment.annotate_cells()

        print("Performing Evaluation")
        experiment_file = f"Dataset/output/cea annotation/cea_biodiv_{experiment}_experiment.csv"
        biodiv_evaluate_CEA.run(experiment_file)

    elif dataset == "tfood":
        print("Performing annotation for tFood Tables")
        if experiment == 'first':
            # Call the function from your script
            CEA_Tfood_first_experiment.annotate_cells()
        elif experiment == 'second':
            print("The second experiment cannot be performed since the number of columns in tFood dataset is equal to 2 and no relationship exist")
        elif experiment == 'third':
            # Call the function from your script
            CEA_Tfood_third_experiment.annotate_cells()

        if experiment != "second":
            print("Performing Evaluation")
            experiment_file = f"Dataset/output/cea annotation/cea_tfood_{experiment}_experiment.csv"
            tfood_evaluate_CEA.run(experiment_file)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <dataset> <experiment>")
        sys.exit(1)

    else:
        dataset = sys.argv[1]
        experiment = sys.argv[2]

        run_experiment(dataset, experiment)
