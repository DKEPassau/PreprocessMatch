import csv
import requests
import pandas as pd
import time
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the directory containing the imported script
os.chdir(current_directory)


WIKIDATA_API_ENDPOINT = "https://www.wikidata.org/w/api.php"


def get_wikidata_entity(table_name, row_index, column_index):
    print(table_name)

    df_target = pd.read_csv(
        f"Dataset/val/tables/{table_name}.csv")
    cell_value = df_target.iloc[row_index, column_index]
    print(cell_value)

    cell_value_items = cell_value.split(",")
    returned_annotation = ""
    for item in cell_value_items:
        # No preprocessing, request the API with the same given cell input
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": item
        }

        try:
            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    if (returned_annotation != ""):
                        returned_annotation = returned_annotation + \
                            "," + data["search"][0]["concepturi"]
                    else:
                        returned_annotation = returned_annotation + \
                            data["search"][0]["concepturi"]

        except requests.exceptions.RequestException as e:
            print("An error occurred while connecting to the Wikidata API:", str(e))

    return returned_annotation

# Add annotation to the csv files


def annotate_cells():
    df_cea_targets = pd.read_csv(
        "Dataset/val/targets/cea_targets.csv", header=None)
    df_annotated = df_cea_targets.copy()

    # Create Annotation column
    df_annotated[3] = df_annotated.apply(
        lambda row: get_wikidata_entity(row[0], row[2] - 1, row[1]), axis=1)

    # Save the annotated df
    df_annotated.to_csv(
        'Dataset/val/cea annotation/cea_tfood_third_experiment.csv', index=False, header=False)


if __name__ == "__main__":
    # Start the timer
    start_time = time.time()
    annotate_cells()

    # End the timer
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    # Print the elapsed time
    print(f"Elapsed time: {elapsed_time} seconds")
