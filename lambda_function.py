import parse_api
import boto3
import parse_dataset
import os
import logging
import pandas as pd
import datetime
import utils
from config import (
    FTP_SERVER_LINK,
    API_LINK,
    S3_BUCKET_NAME,
    LOGS_PATH,
    INPUT_PATH,
    API_PATH,
)

pd.set_option("display.float_format", lambda x: "%.2f" % x)

## Part 1: AWS S3 & Sourcing Datasets
s3_resource = boto3.resource("s3")


def get_logger():
    utils.clean_temp_files()
    log_file_name = (
        f'report_log_{datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.log'
    )
    log_file_path = os.path.join(LOGS_PATH, log_file_name)
    logger = logging.getLogger("data-quest-logger")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger, log_file_name, log_file_path


def handler(event, context):
    logger, log_file_name, log_file_path = get_logger()

    parse_dataset.get_updates(FTP_SERVER_LINK, s3_resource, S3_BUCKET_NAME)
    parse_api.store_api_response(API_LINK, s3_resource, S3_BUCKET_NAME)
    utils.sync_s3(s3_resource, S3_BUCKET_NAME)

    part1_file = os.path.join(INPUT_PATH, "pr.data.0.Current")
    df_part1 = pd.read_csv(part1_file, delimiter="\t")

    # Removing excessive whitespaces from values and column names
    df_part1 = df_part1.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df_part1.columns = df_part1.columns.str.replace(" ", "")

    # Reading the json file from Part 2
    part2_file = os.path.join(API_PATH, "api_response.json")
    df_part2 = pd.read_json(part2_file)

    # Removing excessive whitespaces from values and column names
    df_part2 = df_part2.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df_part2.columns = df_part2.columns.str.replace(" ", "")

    ### 3.1 Using the dataframe from the population data API (Part 2), generate the mean and the standard deviation of the annual US population across the years [2013, 2018] inclusive.

    df2_calculation = df_part2[df_part2["IDYear"].between(2013, 2018)]

    mean_population = df2_calculation["Population"].mean()
    std_population = df2_calculation["Population"].std()

    logger.info(f"The mean is {mean_population}")
    logger.info(f"The standard deviation is {std_population}")

    ### 3.2 Using the dataframe from the time-series (Part 1), For every series_id, find the best year: the year with the max/largest sum of "value" for all quarters in that year. Generate a report with each series id, the best year for that series, and the summed value for that year. For example, if the table had the following values:

    df = df_part1.groupby(["series_id", "year"])["value"].sum()
    df = df.reset_index()

    max_value_indices = df.groupby("series_id")["value"].transform(max) == df["value"]
    df_result = df[max_value_indices].reset_index(drop=True)

    logger.info("The best year for every series id:")
    logger.info(f"\n {df_result.to_markdown(floatfmt='.1f')}")

    ### 3.3 Using both dataframes from Part 1 and Part 2, generate a report that will provide the value for series_id = PRS30006032 and period = Q01 and the population for that given year (if available in the population dataset)

    df_1 = df_part1[["series_id", "year", "period", "value"]]
    df_2 = df_part2[["Year", "Population"]]
    df_2.columns = ["year", "Population"]

    df_report = pd.merge(df_1, df_2, on="year", how="inner")
    df_report = df_report[
        (df_report["series_id"] == "PRS30006032") & (df_report["period"] == "Q01")
    ]
    df_report = df_report.reset_index(drop=True)

    logger.info(
        "The report that will provide the value for series_id = PRS30006032 and period = Q01 and the population for that given year"
    )
    logger.info(f"\n {df_report.to_markdown(floatfmt='.1f')}")

    log_s3_key = f"logs/{log_file_name}"
    utils.upload_to_s3(s3_resource, log_file_path, S3_BUCKET_NAME, log_s3_key)
