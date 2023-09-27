from datetime import datetime
import json
import os
import pandas as pd


def init_output(type):
    """Creates output directory and initializes empty output file.

    Args:
        type (str): csv/txt/json.

    Returns:
        None
    """

    valid_types = ["csv", "txt", "json"]
    if type not in valid_types:
        raise ValueError(f"Invalid output type: {type}. Please use csv, txt, or json.")

    # Create output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Get current date and time for file name
    file_name = datetime.now().strftime("%d-%m-%Y(%H:%M:%S)")

    # Create output file

    with open(os.path.join("./output", f"{file_name}.{type}"), "w") as f:
        pass

    return "./output/" + f"{file_name}.{type}"


def write_output(output_file, output_type, results):
    """Writes results to the correct output file in json, csv or txt.

    Args:
        output_file (str): Path to output file.
        output_type (str): csv/txt/json.
        results (dict): Results from scraper.

    Returns:
        None
    """

    # Determine output type
    if output_type == "json":
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)

    if output_type == "txt":
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)

    if output_type == "csv":
        # make dataframes in pandas
        # url_df = pd.DataFrame(
        #     columns=[
        #         "url",
        #         "UA_Code",
        #         "GA_Code",
        #         "GTM_Code",
        #         "Archived_UA_Codes",
        #         "Archived_GA_Codes",
        #         "Archived_GTM_Codes",
        #     ]
        # )

        url_list = []

        for item in results:
            for url, info in item.items():
                url_list.append({
                    "url": url,
                    "UA_Code": info["current_UA_code"],
                    "GA_Code": info["current_GA_code"],
                    "GTM_Code": info["current_GTM_code"],
                    "Archived_UA_Codes": info["archived_UA_codes"],
                    "Archived_GA_Codes": info["archived_GA_codes"],
                    "Archived_GTM_Codes": info["archived_GTM_codes"],
                })

        url_df = pd.DataFrame(url_list)

        url_df.to_csv(output_file, index=False)