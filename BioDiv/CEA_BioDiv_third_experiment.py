from requests_html import HTMLSession
from requests_html import HTML
import urllib
import csv
import requests
import pandas as pd
import time
import re
import pickle
from googlesearch import search
from SPARQLWrapper import SPARQLWrapper, JSON
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the directory containing the imported script
os.chdir(current_directory)


WIKIDATA_API_ENDPOINT = "https://www.wikidata.org/w/api.php"

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the directory containing the imported script
os.chdir(current_directory)

# Load abbreviation annotation mapping (done offline)
with open('abbreviation_annotation_mapping.pkl', 'rb') as pickle_file:
    abbreviation_annotation_mapping = pickle.load(pickle_file)


def get_source(url):
    """Return the source code for the provided URL. 

    Args: 
        url (string): URL of the page to scrape.

    Returns:
        response (object): HTTP response object from requests_html. 
    """

    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def scrape_google(query):

    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)

    links = list(response.html.absolute_links)
    google_domains = ('https://www.google.',
                      'https://google.',
                      'https://webcache.googleusercontent.',
                      'http://webcache.googleusercontent.',
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.')

    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)

    return links


def get_results(query):

    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)

    return response


def parse_results(response):

    css_identifier_result = ".tF2Cxc"
    css_identifier_title = "h3"
    css_identifier_link = ".yuRUbf a"
    css_identifier_text = ".VwiC3b"

    results = response.html.find(css_identifier_result)

    output = []

    for result in results:
        try:
            item = {
                'title': result.find(css_identifier_title, first=True).text,
                'link': result.find(css_identifier_link, first=True).attrs['href'],
                'text': result.find(css_identifier_text, first=True).text
            }

            output.append(item)

        except:
            continue

    return output


def google_search(query):
    response = get_results(query)
    return parse_results(response)


def get_text_inside_brackets(input_string):
    # Split the input string at the first opening parenthesis
    parts = input_string.split('(', 1)

    # If there are two parts (before and after the first opening parenthesis), return the first part
    if len(parts) == 2:
        return parts[1][:-1].strip()

    # If no opening parenthesis is found, return the entire input string
    return input_string.strip()


def get_text_outside_brackets(input_string):
    # Split the input string at the first opening parenthesis
    parts = input_string.split('(', 1)

    # If there are two parts (before and after the first opening parenthesis), return the first part
    if len(parts) == 2:
        return parts[0].strip()

    # If no opening parenthesis is found, return the entire input string
    return input_string.strip()


def extract_species_and_sub(input_string):
    # Define regular expressions to match "species" and "sub" followed by text
    species_pattern = r'species:(\w+)'
    sub_pattern = r'sub:(\w+)'

    # Use re.search to find matches in the input_string
    species_match = re.search(species_pattern, input_string)
    sub_match = re.search(sub_pattern, input_string)

    # Initialize variables to store the extracted values
    species = None
    sub = None

    # Check if "species" was found and extract the value
    if species_match:
        species = species_match.group(1)

    # Check if "sub" was found and extract the value
    if sub_match:
        sub = sub_match.group(1)

    return species, sub


def fix_string(original_string, pattern, new_substring):
    new_string = re.sub(pattern, new_substring, original_string)
    return new_string

# def get_google_search_result(query):
#     ## Google Search query results as a Python List of URLs
#     search_result_list = list(search(query, num_results=1))
#     if len(search_result_list) > 0:
#         return search_result_list[0]
#     return ""


def retrieve_entity_color(cell_value):
    sparql_endpoint_url = "https://query.wikidata.org/sparql"
    query = """
        SELECT ?entity
        WHERE {{
        ?entity wdt:P31 wd:Q1075.  
        ?entity ?property "%s".
        }}    
    """ % (cell_value)
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
        return claims["results"]["bindings"][0]["entity"]["value"].replace("http", "https")
    return None


def get_wikidata_entity(table_name, row_index, column_index):
    print(table_name)

    df_target = pd.read_csv(
        f"Dataset/val/tables/{table_name}.csv", header=None)
    cell_value = df_target.iloc[row_index, column_index]
    print(cell_value)

    try:
        # Handling Color Column
        if (table_name == "18389aef970147c4982d160c7a2d42f9" and column_index == 11 and row_index != 0):
            if ("/" in cell_value):
                string_to_be_returned = ""
                cell_value_1 = cell_value.split("/")[0]
                cell_value_2 = cell_value.split("/")[1]
                entity_1 = retrieve_entity_color(cell_value_1)
                entity_2 = retrieve_entity_color(cell_value_2)
                if (entity_1 and entity_2):
                    return entity_1 + "," + entity_2
                elif (entity_1 and not entity_2):
                    return entity_1
                elif (entity_2 and not entity_1):
                    return entity_2
                else:
                    return None
            else:
                return retrieve_entity_color(cell_value)

        # Handling mg/kg of Boron
        if (table_name == "c59f306bb061463f8b5ce7174d4e450d" and column_index == 7 and row_index != 0):
            new_cell_value = cell_value.split(" of ")[1]
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": new_cell_value
            }

            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    # Concatenate with entity for mg/kg
                    return "https://www.wikidata.org/wiki/Q21091747," + "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]
            return ""

        # Handling Nested Entities: Wenzel Kroeber (Universität Hamburg)
        if ((table_name == "0be7652b187b45f5b111d51905c3c25b" and column_index == 1) or
            (table_name == "89e72a749d764c1aacd9284e01c412a4" and column_index == 4) or
                (table_name == "b0edc48006d5454dae3ca3e41f33e280" and column_index == 12)) and (row_index != 0):
            cell_value_1 = get_text_outside_brackets(cell_value)
            cell_value_2 = get_text_inside_brackets(cell_value)
            params_1 = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": cell_value_1
            }

            params_2 = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": cell_value_2
            }

            response_1 = requests.get(WIKIDATA_API_ENDPOINT, params=params_1)
            response_2 = requests.get(WIKIDATA_API_ENDPOINT, params=params_2)
            data_1 = response_1.json()
            data_2 = response_2.json()
            string_to_be_returned = ""

            if "search" in data_1:
                # If the API find an associated entity for the input
                if len(data_1["search"]) != 0:
                    string_to_be_returned = string_to_be_returned + "https://www.wikidata.org/wiki/" + \
                        data_1["search"][0]["concepturi"].split("/")[-1]

            if "search" in data_2:
                # If the API find an associated entity for the input
                if len(data_2["search"]) != 0:
                    if string_to_be_returned == "":
                        string_to_be_returned = "https://www.wikidata.org/wiki/" + \
                            data_2["search"][0]["concepturi"].split("/")[-1]
                    else:
                        string_to_be_returned = string_to_be_returned + ",https://www.wikidata.org/wiki/" + \
                            data_2["search"][0]["concepturi"].split("/")[-1]

            if string_to_be_returned != "":
                return string_to_be_returned

        # Handling parenthesis special case like 2015 (September) returns September
        elif (table_name == "39a2d36769294a0a846cc209c45234e4" and column_index == 4):
            # Get string between parenthesis
            new_cell_value = get_text_inside_brackets(cell_value)
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": new_cell_value
            }

            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    return "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]
            return ""

        # Handling parenthesis special case like 2015 (September) returns 2015
        elif (table_name == "89e72a749d764c1aacd9284e01c412a4" and column_index == 4):
            # Get string between parenthesis
            new_cell_value = get_text_outside_brackets(cell_value)
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": new_cell_value
            }

            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    return "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]
            return ""

        # Composed Values: seperated by ","
        elif ((table_name == "008851b16aa04124b3a9195676604f35" and column_index == 25) or
              (table_name == "0ffeda696bba402284a382ab877bb9e7" and column_index == 0) or
              (table_name == "11a0fb6a86ba4fef9dbb904fa851066b" and column_index == 1) or
                (table_name == "e749786aff714981a5a7da3da0789128" and column_index == 1)) and (row_index != 0):
            cell_values = cell_value.split(",")
            cell_value_1 = cell_values[0]
            cell_value_2 = cell_values[1]
            params_1 = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": cell_value_1
            }

            params_2 = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": cell_value_2
            }

            response_1 = requests.get(WIKIDATA_API_ENDPOINT, params=params_1)
            response_2 = requests.get(WIKIDATA_API_ENDPOINT, params=params_2)
            data_1 = response_1.json()
            data_2 = response_2.json()
            string_to_be_returned = ""

            if "search" in data_1:
                # If the API find an associated entity for the input
                if len(data_1["search"]) != 0:
                    string_to_be_returned = string_to_be_returned + "https://www.wikidata.org/wiki/" + \
                        data_1["search"][0]["concepturi"].split("/")[-1]

            if "search" in data_2:
                # If the API find an associated entity for the input
                if len(data_2["search"]) != 0:
                    if (string_to_be_returned == ""):
                        string_to_be_returned = "https://www.wikidata.org/wiki/" + \
                            data_2["search"][0]["concepturi"].split("/")[-1]
                    else:
                        string_to_be_returned = string_to_be_returned + ",https://www.wikidata.org/wiki/" + \
                            data_2["search"][0]["concepturi"].split("/")[-1]
            if string_to_be_returned != "":
                return string_to_be_returned

        # Handling special format: species:x_name sub:y_name
        elif (table_name == "d5542ea1fddf44c39d2bb70dc436ddf8" and column_index == 1 and row_index != 0):
            species, sub = extract_species_and_sub(cell_value)
            new_cell_value = species + " " + sub
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": new_cell_value
            }

            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    return "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]

            return ""

        # Handle Last Name, First Name
        elif (table_name == "5f50cabcafd1482e98d9dc446d735f5e" and column_index == 0 and "," in cell_value and row_index != 0):
            values = cell_value.split(",")
            new_cell_value = values[1].strip() + " " + values[0].strip()
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": new_cell_value
            }

            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    return "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]

        # Handle Complex Name Extraction: Sr_Strontium_Gr_GEMAS_AquaRegia ==> Stronium
        elif (table_name == "b02af14b8cf34c43bac84325d6f1e912" and column_index == 1 and "_" in cell_value and row_index != 0):
            values = cell_value.split("_")
            new_cell_value = values[1]
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": new_cell_value
            }

            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    return "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]

        # Handle More Complex Nested Entities: Dove, Black-naped Fruit,Ptilinopus melanospilus » ==> « Black-naped Fruit Dove
        elif (table_name == "5a71350927ed44ca979498a5b7719a68" and column_index == 0 and "," in cell_value and row_index != 0):
            values = cell_value.split(",")
            new_cell_value = values[-1]
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": new_cell_value
            }

            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    return "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]

        # Handle useless words and special characters: « Australian Cattle Dog Mix » ==> « Australian Cattle Dog » « Brown Tabby » ==> « Brown » Massilia cf. aurea* ==> « Massilia aurea »
        elif (table_name == "0bc67e05a4d14011a2cf3fca2f869495" and column_index == 8 and "*" in cell_value and "cf." in cell_value and row_index != 0):
            print(cell_value)
            cell_value = fix_string(cell_value, "cf. ", "")
            new_cell_value = cell_value.replace("*", "")
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": new_cell_value
            }

            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    return "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]

        # Handle Abbreviations
        elif cell_value in abbreviation_annotation_mapping.keys():
            return abbreviation_annotation_mapping[cell_value]

        # Table: 8249f8533f764f6dbd195a872c18fd6d - species fish
        elif (table_name == "8249f8533f764f6dbd195a872c18fd6d" and column_index == 0 and row_index != 0):
            results = []
            number_attempts = 2
            # results = google_search(cell_value + " wikidata")

            while (len(results) == 0 and number_attempts > 0):
                results = google_search(cell_value + "fish species wikidata")
                number_attempts = number_attempts - 1
                time.sleep(5)

            print(results)
            if (len(results) > 0):
                first_link = results[0]["link"]
                if ("wikidata" in first_link):
                    if ("Q" in first_link.split("/")[-1]):
                        return first_link

        # Table: 74fc7b22dac0461a8a522480483bae4a - species fish
        elif (table_name == "74fc7b22dac0461a8a522480483bae4a" and column_index == 2 and row_index != 0):
            results = []
            number_attempts = 2
            # results = google_search(cell_value + " wikidata")

            while (len(results) == 0 and number_attempts > 0):
                results = google_search(
                    cell_value + " species of plant wikidata")
                number_attempts = number_attempts - 1
                time.sleep(5)

            print(results)
            if (len(results) > 0):
                first_link = results[0]["link"]
                if ("wikidata" in first_link):
                    if ("Q" in first_link.split("/")[-1]):
                        return first_link

        # Table: 34169c088ee848e4866f42e87b4ccbc2 - species fish
        elif (table_name == "34169c088ee848e4866f42e87b4ccbc2" and column_index == 5 and row_index != 0):
            results = []
            number_attempts = 2
            # results = google_search(cell_value + " wikidata")

            while (len(results) == 0 and number_attempts > 0):
                results = google_search(
                    cell_value + " species of plant wikidata")
                number_attempts = number_attempts - 1
                time.sleep(5)

            print(results)
            if (len(results) > 0):
                first_link = results[0]["link"]
                if ("wikidata" in first_link):
                    if ("Q" in first_link.split("/")[-1]):
                        return first_link

        else:
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": cell_value
            }
            response = requests.get(WIKIDATA_API_ENDPOINT, params=params)
            data = response.json()

            if "search" in data:
                # If the API find an associated entity for the input
                if len(data["search"]) != 0:
                    return "https://www.wikidata.org/wiki/" + data["search"][0]["concepturi"].split("/")[-1]

        # In case of no annotation / Handle incorrect names using google search
        # Sometimes the scrapping doesn't work for some reason, we can force a rescrapping
        results = []
        number_attempts = 2
        # results = google_search(cell_value + " wikidata")

        while (len(results) == 0 and number_attempts > 0):
            results = google_search(cell_value + " wikidata")
            number_attempts = number_attempts - 1
            time.sleep(5)

        print(results)
        if (len(results) > 0):
            first_link = results[0]["link"]
            if ("wikidata" in first_link):
                if ("Q" in first_link.split("/")[-1]):
                    return first_link

    except requests.exceptions.RequestException as e:
        print("An error occurred while connecting to the Wikidata API:", str(e))

    return None

# Add annotation to the csv files


def annotate_cells():
    df_cea_targets = pd.read_csv(
        "Dataset/val/gt/CEA_biodivtab_selected_tables_gt.csv", header=None)
    df_annotated = df_cea_targets.copy()

    # Create Annotation column
    df_annotated[3] = df_annotated.apply(
        lambda row: get_wikidata_entity(row[0], row[2], row[1]), axis=1)

    # Save the annotated df
    df_annotated.to_csv(
        'Dataset/output/cea annotation/cea_biodiv_third_experiment.csv', index=False, header=False)


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
