import csv
import requests
import pandas as pd
import time
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the directory containing the imported script
os.chdir(current_directory)


WIKIDATA_API_ENDPOINT = "https://www.wikidata.org/w/api.php"

# Retrieve the property using label and QID


def get_property(entity, property_label):
    sparql_endpoint_url = "https://query.wikidata.org/sparql"
    query = """
        SELECT ?property ?propertyLabel ?valueLabel
        WHERE {{
        wd:%s ?property ?valueLabel.
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        FILTER (CONTAINS(LCASE(?valueLabel), "%s"))
        }}
    """ % (entity, property_label)
    claims = None

    while claims == None:
        try:
            sparql = SPARQLWrapper(
                sparql_endpoint_url, agent='example-UA (https://example.com/; mail@example.com)')
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            claims = sparql.query().convert()
            if 'results' not in claims:
                claims = None
        except:
            time.sleep(10)
            continue
    if (len(claims["results"]["bindings"]) > 0):
        return claims["results"]["bindings"][0]["propertyLabel"]["value"]
    return None


def get_annotations_for_column(table_name, column_index):
    df_annotation_retrieved = pd.read_csv(
        f"DataSets/Valid/cea annotation/output_with_special_character_handling_and_correction.csv", header=None)
    return df_annotation_retrieved[(df_annotation_retrieved.iloc[:, 0] == table_name) & (df_annotation_retrieved.iloc[:, 2] == column_index)].values


def get_wikidata_property(table_name, column_one_index, column_two_index):
    print(table_name)

    df_table = pd.read_csv(
        f"DataSets/Valid/tables/{table_name}.csv", header=None)

    # We suppose the first column is always column one and we have CEA annotation for its values
    # column_one = df_table.iloc[:, column_one_index].values
    cea_annotations_column_one = get_annotations_for_column(
        table_name, column_one_index)
    # print(cea_annotations_column_one)

    properties = []
    for row in cea_annotations_column_one:
        if (type(row[3]) != float):
            entity = row[3].split("/")[-1]
            other_column_value = df_table.iloc[row[1], column_two_index]

            print(entity)
            print(other_column_value)
            # Retrieve the property for the pair QID and other column's value
            retrieved_property = get_property(entity, other_column_value)
            if retrieved_property is not None:
                properties.append(get_property(entity, other_column_value))

    print(properties)
    if (len(properties) == 0):
        return None
    else:
        # Use Counter to count the occurrences of each item
        item_counts = Counter(properties)

        # Find the item with the highest frequency
        most_common_item = item_counts.most_common(1)[0][0]

        return most_common_item

# Add annotation to the csv files


def annotate_relationships():
    df_cpa_targets = pd.read_csv(
        "DataSets/Valid/targets/cpa_targets.csv", header=None)
    df_annotated = df_cpa_targets.copy()

    # Create Annotation column
    df_annotated[3] = df_annotated.apply(
        lambda row: get_wikidata_property(row[0], row[1], row[2]), axis=1)

    # Save the annotated df
    df_annotated.to_csv(
        'DataSets/Valid/cpa annotation/output_with_special_character_handling_and_correction.csv', index=False, header=False)


if __name__ == "__main__":
    # Start the timer
    start_time = time.time()
    annotate_relationships()

    # End the timer
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    # Print the elapsed time
    print(f"Elapsed time: {elapsed_time} seconds")


# SELECT ?property ?propertyLabel ?valueLabel
# WHERE {
#   wd:Q6386554 ?property ?valueLabel.
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
#   FILTER (CONTAINS(LCASE(?valueLabel), "25.65"))
# }
