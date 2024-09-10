import csv
import requests
import pandas as pd
import time
from SPARQLWrapper import SPARQLWrapper, JSON
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the directory containing the imported script
os.chdir(current_directory)


WIKIDATA_API_ENDPOINT = "https://www.wikidata.org/w/api.php"


def get_wikidata_entity(table_name, row_index, column_index):
    print(table_name)

    df_target = pd.read_csv(
        f"Dataset/val/tables/{table_name}.csv", header=None)
    cell_value = df_target.iloc[row_index, column_index]
    print(cell_value)
    # No preprocessing, request the API with the same given cell input
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        # Increasing limit to the maximal value helps on retrieving all possible entities
        "limit": 50,  # Max is 50
        "search": cell_value
    }

    # props_params = {
    #     'action': 'wbgetentities',
    #     'ids': entity,
    #     'props': 'claims',
    #     'languages': 'en',
    #     'format': 'json'
    # }

    # Retry parameters (retry for the wikidata API)
    max_retries = 3
    retry_count = 0
    retry_delay = 5  # seconds

    # Make a request to the Wikidata API with retry logic
    while retry_count < max_retries:
        try:
            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    # Retrieve all possible entities
                    possible_entities = [url["concepturi"].split(
                        "/")[-1] for url in data["search"]]

                    # retrieve other columns values of same row
                    row_values = df_target.iloc[row_index, :column_index].values.tolist(
                    ) + df_target.iloc[row_index, column_index+1:].values.tolist()

                    # print(possible_entities)
                    # iterate through all possible entities, retrieve the props and check if the other column's values exist on there
                    for entity in possible_entities:
                        # props_params = {
                        #     'action': 'wbgetentities',
                        #     'ids': entity,
                        #     'props': 'claims',
                        #     'languages': 'en',
                        #     'format': 'json'
                        # }
                        # # Send the API request
                        # response = requests.get(WIKIDATA_API_ENDPOINT, params=props_params)
                        # claims = response.text
                        sparql_endpoint_url = "https://query.wikidata.org/sparql"
                        query = """
                            SELECT ?wdLabel ?ooLabel
                            WHERE {
                            VALUES (?s) {(wd:%s)}
                            ?s ?wdt ?o .
                            ?wd wikibase:directClaim ?wdt .
                            ?wd rdfs:label ?wdLabel .
                            OPTIONAL {
                                ?o rdfs:label ?oLabel .
                                FILTER (lang(?oLabel) = "en")
                            }
                            FILTER (lang(?wdLabel) = "en")
                            BIND (COALESCE(?oLabel, ?o) AS ?ooLabel)
                            } ORDER BY xsd:integer(STRAFTER(STR(?wd), "http://www.wikidata.org/entity/P"))
                        """ % (entity)

                        claims = None

                        while claims == None:
                            try:
                                sparql = SPARQLWrapper(
                                    sparql_endpoint_url, agent='example-UA (https://example.com/; mail@example.com)')
                                sparql.setQuery(query)
                                sparql.setReturnFormat(JSON)
                                claims = str(sparql.query().convert())
                                if 'results' not in claims:
                                    claims = None
                            except:
                                time.sleep(10)
                                continue

                        test_is_right_entity = True

                        for value in row_values:
                            # if type(value) == float or type(value) == int:
                            #     value = f"+{value}"
                            try:
                                if (type(value) == float):
                                    if (not np.isnan(value)):
                                        if f"'value': '{value}'" not in claims:
                                            test_is_right_entity = False
                                    else:
                                        continue
                                else:
                                    # sure not a NaN value
                                    if f"'value': '{value}'" not in claims:
                                        test_is_right_entity = False
                            except:
                                # The value is nan
                                continue
                        # Assuming there is one only entity annotation we break where we find it
                        if (test_is_right_entity == True):
                            return "https://www.wikidata.org/wiki/" + entity

                    # Case where all other row values are nan, we return first possible annotation
                    return "https://www.wikidata.org/wiki/" + possible_entities[0]

            return ""

        except requests.exceptions.RequestException as e:
            retry_count = retry_count + 1
            if retry_count < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

            # print("An error occurred while connecting to the Wikidata API:", str(e))

    return None

# Add annotation to the csv files


def annotate_cells():
    # To modify
    df_cea_targets = pd.read_csv(
        "Dataset/val/gt/CEA_biodivtab_selected_tables_gt.csv", header=None)
    # df_cea_targets = pd.read_csv("DataSets/Valid/cea annotation/wrong_annotations.csv", header=None)

    df_annotated = df_cea_targets.copy()

    # For testing
    # df_annotated = df_annotated.iloc[3605:3710,:]

    # Create Annotation column
    df_annotated[3] = df_annotated.apply(
        lambda row: get_wikidata_entity(row[0], row[2], row[1]), axis=1)

    # Save the annotated df
    df_annotated.to_csv(
        'Dataset/output/cea annotation/cea_biodiv_second_experiment.csv', index=False, header=False)


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
