from datetime import datetime
import json
import os
import pandas as pd


def init_output(type, output_dir="./output"):
    """Creates output directory and initializes empty output file.

    Args:
        type (str): csv/txt/json.
        output_dir (str): Path to output directory. Defaults to ./output.

    Returns:
        None
    """

    valid_types = ["csv", "txt", "json", "xlsx"]
    if type not in valid_types:
        raise ValueError(
            f"Invalid output type: {type}. Please use csv, txt, xlsx or json."
        )

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get current date and time for file name
    file_name = datetime.now().strftime("%d-%m-%Y(%H:%M:%S)")

    # Create empty output file if type is not csv and return filename
    if type not in ["csv"]:
        with open(os.path.join(f"{output_dir}", f"{file_name}.{type}"), "w") as f:
            pass

        return f"{output_dir}/" + f"{file_name}.{type}"

    # If csv, create separate files for urls and codes and return filename
    with open(os.path.join(f"{output_dir}", f"{file_name}_urls.{type}"), "w") as f:
        pass

    with open(os.path.join(f"{output_dir}", f"{file_name}_codes.{type}"), "w") as f:
        pass

    return f"{output_dir}/" + f"{file_name}.{type}"


def write_output(output_file, output_type, results):
    """Writes results to the correct output file in json, csv or txt.

    Args:
        output_file (str): Path to output file.
        output_type (str): csv/txt/json.
        results (dict): Results from scraper.

    Returns:
        None
    """

    # If json or txt, write contents directly to file.
    if output_type == "json" or output_type == "txt":
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
        return
    # If csv or xlsx, convert results to pandas dataframes.
    urls_df = get_urls_df(results)
    codes_df = get_codes_df(results)

    # If csv, write dataframes to separate csv files for urls, codes.
    if output_type == "csv":
        urls_output_file = output_file.replace(".csv", "_urls.csv")
        codes_output_file = output_file.replace(".csv", "_codes.csv")
        urls_df.to_csv(urls_output_file, index=False)
        codes_df.to_csv(codes_output_file, index=False)

    # If xlsx, write dataframes to separate sheets for urls, codes.
    if output_type == "xlsx":
        writer = pd.ExcelWriter(output_file, engine="xlsxwriter")
        urls_df.to_excel(writer, sheet_name="URLs", index=False)
        codes_df.to_excel(writer, sheet_name="Codes", index=False)
        writer.close()


def get_urls_df(results):
    """Flattens the results json (list of dictionaries) and converts it into simple Pandas dataframe and returns it.

    Args:
        list: Results from scraper.

    Returns:
        urls_df (pd.DataFrame): Pandas dataframe of results.
    """

    url_list = []

    for item in results:
        for url, info in item.items():
            url_list.append(
                {
                    "url": url,
                    "UA_Code": info.get("current_UA_code", ""),
                    "GA_Code": info.get("current_GA_code", ""),
                    "GTM_Code": info.get("current_GTM_code", ""),
                    "Archived_UA_Codes": format_archived_codes(
                        info.get("archived_UA_codes", {})
                    ),
                    "Archived_GA_Codes": format_archived_codes(
                        info.get("archived_GA_codes", {})
                    ),
                    "Archived_GTM_Codes": format_archived_codes(
                        info.get("archived_GTM_codes", {})
                    ),
                }
            )

    return pd.DataFrame(url_list)


def format_archived_codes(archived_codes):
    """Helper function to flatten archived codes and format them into a single string where
    each item is numbered and separated by a newline.

    Args:
        archived_codes (dict): Dictionary of archived codes.

    Returns:
        str: Formatted string.
    """

    results = []
    idx = 1

    for code, timeframe in archived_codes.items():
        results.append(
            f"{idx}. {code} ({timeframe['first_seen']} - {timeframe['last_seen']})"
        )
        idx += 1

    return "\n\n".join(results)


def get_codes_df(results):
    """Flattens the result json (list of dictionries) into a Pandas dataframe and returns it.

    Args:
        results (list): Results from scraper.

    Returns:
        codes_df (pd.DataFrame): Pandas dataframe of results.

    """

    code_list = []

    # Flattens results into list of dicts for each code, including duplicates
    for item in results:
        for url, info in item.items():
            for key, code in info.items():
                if type(code) is list:
                    for c in code:
                        code_list.append(
                            {
                                "code": c,
                                "websites": url,
                                "active": f"Current (at {url})",
                            }
                        )
                if type(code) is dict:
                    for c in code:
                        code_list.append(
                            {
                                "code": c,
                                "websites": url,
                                "active": f"{code[c]['first_seen']} - {code[c]['last_seen']}(at {url})",
                            }
                        )

    # Return a df w/ string message if no codes found
    if not code_list:
        return pd.DataFrame([{"Message": "No codes found."}])

    # Convert list of dicts to pandas dataframe
    codes_df = pd.DataFrame(code_list)

    # Combine all duplicates and format combined columns
    codes_df = (
        codes_df.groupby("code")
        .agg({"websites": lambda x: ", ".join(x), "active": format_active})
        .reset_index()
    )

    return codes_df


def format_active(list):
    """Takes a list of strings and formats them into a single, numbered string where
    each item is separated by a newline.

    Args:
        list (list): List of strings.

    Returns:
        str: Formatted string.

    Example:
        ["Current (at https://www.example.com)", "2019-01-01 - 2020-01-01 (at https://www.example.com)"]
            ->
        "1. Current (at https://www.example.com)\n\n
         2. 2019-01-01 - 2020-01-01 (at https://www.example.com)"

    """

    return "\n\n".join(f"{i + 1}. {item}" for i, item in enumerate(list))
