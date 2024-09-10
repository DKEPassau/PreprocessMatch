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


if __name__ == "__main__":
    df_true = pd.read_csv("Dataset/Valid/gt/cpa_gt.csv", header=None)
    print("Scores for first experiment")
    df_annotated = pd.read_csv(
        "Dataset/output/cpa annotation/cpa_wikidata_first_experiment.csv", header=None)
    evaluate(df_annotated, df_true)
    print("----------------------------")

    print("Scores for second experiment")
    df_annotated = pd.read_csv(
        "Dataset/output/cpa annotation/cpa_wikidata_second_experiment.csv", header=None)
    evaluate(df_annotated, df_true)
    print("----------------------------")

    print("Scores for third experiment")
    df_annotated = pd.read_csv(
        "Dataset/output/cpa annotation/cpa_wikidata_third_experiment.csv", header=None)
    evaluate(df_annotated, df_true)
    print("----------------------------")
