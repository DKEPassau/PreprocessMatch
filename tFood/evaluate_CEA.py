import pandas as pd
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the directory containing the imported script
os.chdir(current_directory)


def evaluate(df_annotated, df_true):
    # Number of correct annotations
    correct_annotations = (df_annotated.iloc[:, 3] == df_true.iloc[:, 3]).sum()
    # Number of wrong annotations
    wrong_annotations = ((df_annotated.iloc[:, 3] != df_true.iloc[:, 3]) & (
        df_annotated.iloc[:, 3].notna())).sum()
    # Number of empty annotations
    empty_annotations = (df_annotated.iloc[:, 3].isna()).sum()
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
    df_true = pd.read_csv("Dataset/val/gt/cea_gt.csv", header=None)
    df_annotated = pd.read_csv(csv_path, header=None)
    print(f"Scores for experiment with file: {csv_path}")
    evaluate(df_annotated, df_true)
    print("----------------------------")


if __name__ == "__main__":
    # Second experiment has exactly same results as the first experiment since there is only two columns in tables
    # Thus ignored
    experiment_files = [
        "Dataset/output/cea annotation/cea_tfood_first_experiment.csv",
        "Dataset/output/cea annotation/cea_tfood_third_experiment.csv",
    ]

    for file in experiment_files:
        run(file)
