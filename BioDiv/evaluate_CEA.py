import pandas as pd
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the directory containing the imported script
os.chdir(current_directory)


def evaluate(df_annotated, df_true):
    correct_annotations = 0
    empty_annotations = 0
    wrong_annotations = 0
    # Iterate through the dataframe
    for (index1, row1), (index2, row2) in zip(df_annotated.iterrows(), df_true.iterrows()):
        if type(row1[3]) == float:  # NaN value
            empty_annotations = empty_annotations + 1
        else:
            if "," in row2[3]:
                targets = row2[3].split(",")
                if (targets[0] in row1[3] or targets[1] in row1[3]):
                    correct_annotations = correct_annotations + 1
                else:
                    wrong_annotations = wrong_annotations + 1

            elif row1[3] == row2[3]:
                correct_annotations = correct_annotations + 1

            else:
                wrong_annotations = wrong_annotations + 1

    # # Number of correct annotations
    # correct_annotations = (df_annotated.iloc[:, 3] == df_true.iloc[:, 3]).sum()
    # # Number of wrong annotations
    # wrong_annotations = ((df_annotated.iloc[:, 3] != df_true.iloc[:, 3]) & (df_annotated.iloc[:, 3].notna())).sum()
    # print(df_annotated[(df_annotated.iloc[:, 3] != df_true.iloc[:, 3]) & (df_annotated.iloc[:, 3].notna())])
    # # Number of empty annotations
    # empty_annotations = (df_annotated.iloc[:, 3].isna()).sum()
    # Ground truth annotations: is the total number of targets
    ground_truth_annotations = df_true.shape[0]
    # Submitted annotations
    submitted_annotations = ground_truth_annotations - empty_annotations
    print("Correct Annotation")
    print(correct_annotations)
    print("Incorrect Annotations")
    print(wrong_annotations)
    print("Empty Annotations")
    print(empty_annotations)
    precision = correct_annotations / submitted_annotations
    recall = correct_annotations / ground_truth_annotations
    f1_score = (2 * precision * recall) / (precision + recall)
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"f1_score: {f1_score}")


def run(csv_path):
    df_true = pd.read_csv(
        "Dataset/val/gt/CEA_biodivtab_selected_tables_gt.csv", header=None)
    df_annotated = pd.read_csv(csv_path, header=None)
    print(f"Scores for experiment with file: {csv_path}")
    evaluate(df_annotated, df_true)
    print("----------------------------")


if __name__ == "__main__":
    # Second experiment has exactly same results as the first experiment since there is only two columns in tables
    # Thus ignored
    experiment_files = [
        "Dataset/output/cea annotation/cea_biodiv_first_experiment.csv",
        "Dataset/output/cea annotation/cea_biodiv_second_experiment.csv",
        "Dataset/output/cea annotation/cea_biodiv_third_experiment.csv"
    ]

    for file in experiment_files:
        run(file)
