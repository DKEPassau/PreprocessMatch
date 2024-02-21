import requests
import time
import pandas as pd
from collections import Counter
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the directory containing the imported script
os.chdir(current_directory)


WIKIDATA_API_ENDPOINT = "https://www.wikidata.org/w/api.php"

# def get_wikidata_entity(cell_value):
#     # No preprocessing, request the API with the same given cell input
#     params = {
#         "action": "wbsearchentities",
#         "format": "json",
#         "language": "en",
#         "search": cell_value
#     }

#     try:
#         response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
#         data = response.json()

#         if "search" in data:
#             # If the API find an associated entity for the input
#             if len(data["search"]) != 0:
#                 return data["search"][0]["concepturi"].split("/")[-1] # get entity from http://www.wikidata.org/entity/entity_id
#         return ""

#     except requests.exceptions.RequestException as e:
#         print("An error occurred while connecting to the Wikidata API:", str(e))

#     return None


def get_wikidata_types(entity_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    response = requests.get(url)
    data = response.json()

    types = []
    if "entities" in data and entity_id in data["entities"]:
        entity = data["entities"][entity_id]
        if "claims" in entity and "P31" in entity["claims"]:
            for claim in entity["claims"]["P31"]:
                if "mainsnak" in claim and "datavalue" in claim["mainsnak"]:
                    datavalue = claim["mainsnak"]["datavalue"]
                    if "value" in datavalue and "id" in datavalue["value"]:
                        types.append(datavalue["value"]["id"])

    return types


def annotate_column_cells(table_name, column_index):
    result_column = []
    df_cea = pd.read_csv(
        f"Dataset/output/cea annotation/cea_wikidata_second_experiment.csv")
    annotations = df_cea[(df_cea.iloc[:, 0] == table_name)
                         & (df_cea.iloc[:, 2] == column_index)]
    annotations = annotations.iloc[:, 3].values
    print(annotations)
    for annotation in annotations:
        if (type(annotation) != float):
            q_annotation = annotation.split("/")[-1]
            result_column.append(q_annotation)

    return result_column


def annotate_column(table_name, column_index):

    # column = df_target.iloc[:, column_index]

    # Annotate cells in a column
    annotated_column_values = annotate_column_cells(table_name, column_index)

    # Annotate the column
    retrieved_annotations = []
    for entity in annotated_column_values:
        entity_types = get_wikidata_types(entity)
        if len(entity_types) > 0:
            perfect_annotation = entity_types[0]
            # okay_annotations = [entity_types[0]]
            # wrong_annotations = entity_types[1:]

            # retrieved_annotations.append({
            #     "entity": entity,
            #     "perfect_annotation": perfect_annotation,
            #     # "okay_annotations": okay_annotations,
            #     # "wrong_annotations": wrong_annotations
            # })
            retrieved_annotations.append(perfect_annotation)

    print(retrieved_annotations)

    if (len(retrieved_annotations) != 0):
        # Use Counter to count the occurrences of each item
        item_counts = Counter(retrieved_annotations)

        # Find the item with the highest frequency
        most_common_item = item_counts.most_common(1)[0][0]

        # for annotation in retrieved_annotations:
        #     print("Entity:", annotation["entity"])
        #     print("Perfect Annotation:", annotation["perfect_annotation"])
        #     # print("Okay Annotations:", annotation["okay_annotations"])
        #     # print("Wrong Annotations:", annotation["wrong_annotations"])

        return "http://www.wikidata.org/entity/" + most_common_item
    return None


def annotate_columns():
    df_cta_targets = pd.read_csv(
        "Dataset/Valid/targets/cta_targets.csv", header=None)
    df_annotated = df_cta_targets.copy()

    df_annotated[3] = df_annotated.apply(
        lambda row: annotate_column(row[0], row[1]), axis=1)

    # Save the annotated df
    df_annotated.to_csv(
        'Dataset/output/cta annotation/cta_wikidata_second_experiment.csv', index=False, header=False)


# Example usage
# column_data = ["Q4667881", "Q5158874", "Q5158879"]
# column_data = ["Banana", "Apple", "Orange"]

if __name__ == "__main__":
    # Start the timer
    start_time = time.time()

    annotate_columns()

    # End the timer
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    # Print the elapsed time
    print(f"Elapsed time: {elapsed_time} seconds")
