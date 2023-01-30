import json, os
import pandas as pd
import requests
from generateJWT import generate_jwt
import time

#AEP_URL = 'https://platform.adobe.io:443/data/foundation/export/batches/01FZG4E4RGFX8DZHDQBFHYF214/meta?path=row_errors%2Fconversion_errors_0.json'

FAILED_RECORDS_FOLDER = "/Users/bitun.sen/Downloads/"

TARGET_SANDBOX_NAME = "poc"

def current_milli_time():
    return round(time.time() * 1000)


def download_failed_records(failed_record_file, error_file_URL, jwt_token, current_time, sandbox_name):

    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-gw-ims-org-id": "9C24574E61A9EB140A495C7D@AdobeOrg",
        "x-api-key" : "3f1ab1550eb04656964e8d4895d2c241",
        "x-sandbox-name": sandbox_name
    }
    auth_header = "Bearer " + jwt_token
    req_headers["Authorization"] = auth_header

    response = requests.get(error_file_URL, headers=req_headers)
    responseText = response.text
    print("Failed Record HTTP Response : " + response.text)
    with open(failed_record_file, 'w') as f:
        f.write(responseText)


## Using BATCHID of AEP, it will retrieve the error files
def retireve_error_file_URL(failedRecordURL, jwt_token, sandbox_name):

    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + jwt_token,
        "x-gw-ims-org-id": "9C24574E61A9EB140A495C7D@AdobeOrg",
        "x-api-key": "3f1ab1550eb04656964e8d4895d2c241",
        "x-sandbox-name": sandbox_name
    }
    #auth_header = "Bearer " + jwt_token
    #req_headers["Authorization"] = auth_header

    response = requests.get(failedRecordURL, headers=req_headers)
    responseText = response.text
    jsonDict = json.loads(responseText)
    error_file_URL = "MISSING URL"
    if jsonDict:
        if jsonDict["data"] and len(jsonDict["data"]) > 0:
            item = jsonDict["data"][0]
            error_file_URL = item["_links"]["self"]["href"]

    if error_file_URL == "MISSING URL":
        raise ValueError('No Error file was returned!!!!')

    return error_file_URL

def extract_run_details(runID, jwt_token, sandbox_name):
    run_details_url = "https://platform.adobe.io/data/foundation/flowservice/runs/" + str(runID)
    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + jwt_token,
        "x-gw-ims-org-id": "9C24574E61A9EB140A495C7D@AdobeOrg",
        "x-api-key": "3f1ab1550eb04656964e8d4895d2c241",
        "x-sandbox-name": sandbox_name
    }

    response = requests.get(run_details_url, headers=req_headers)
    responseText = response.text
    jsonDict = json.loads(responseText)

    print("Response Run Details :: {}".format(responseText))

    runSummary = {}
    if jsonDict:
        if jsonDict["items"] and len(jsonDict["items"]) > 0:
            item = jsonDict["items"][0]
            activities = item["activities"]
            if activities:
                for activity in activities:
                    if activity["name"] == "Promotion Activity":
                        if "inputRecordCount" in activity["recordSummary"]:
                            runSummary["inputRecordCount"] = activity["recordSummary"]["inputRecordCount"]
                        if "outputRecordCount" in activity["recordSummary"]:
                            runSummary["successRecordCount"] = activity["recordSummary"]["outputRecordCount"]
                        if "failedRecordCount" in activity["recordSummary"]:
                            runSummary["failedRecordCount"] = activity["recordSummary"]["failedRecordCount"]

                        runSummary["failedRecordsURL"] = activity["statusSummary"]["extensions"]["manifest"]["failedRecords"]
                        break

    return runSummary


def parse_json(jsonStr):
    jsonDict = json.loads(jsonStr)
    #print("GLOBALCUSTOMERID : {} :: GLOBALPETID : {} : Error :: {}".format(jsonDict["GLOBALCUSTOMERID"], jsonDict["GLOBALPETID"], jsonDict["_errors"][0]["message"]))
    dict = {
        "GLOBALCUSTOMERID" : jsonDict["GLOBALCUSTOMERID"],
        "GLOBALPETID" : jsonDict["GLOBALPETID"],
        "EMAIL" : jsonDict["EMAIL"],
        "ERROR" : jsonDict["_errors"][0]["message"]
    }

    return dict

def extract_Error_Details(error_json_file, current_time, output_excel_file) :
    # Using for loop
    count = 0
    print("\nUsing for loop")

    record_array = []
    with open(error_json_file) as fp:
        for line in fp:
            count += 1
            record_dict = parse_json(line)
            record_array.append(record_dict)

    failed_records_df = pd.DataFrame(record_array)
    failed_records_df.to_excel(output_excel_file)




if __name__ == "__main__":

    current_time = current_milli_time()
    try:
        jwt_token = generate_jwt()
        RUN_ID = "93670d8a-9002-4474-872b-93e5fa60f36b"

        ERROR_JSON_FILENAME = "FailedRecords_" + str(current_time) + ".json"
        COMPLETE_FILE_PATH_ERROR_JSON = os.path.join(FAILED_RECORDS_FOLDER, ERROR_JSON_FILENAME)

        runSummary_dict = extract_run_details(RUN_ID, jwt_token, TARGET_SANDBOX_NAME)
        print(runSummary_dict)
        error_file_URL = retireve_error_file_URL(runSummary_dict["failedRecordsURL"], jwt_token, TARGET_SANDBOX_NAME)

        download_failed_records(COMPLETE_FILE_PATH_ERROR_JSON, error_file_URL, jwt_token, current_time,
                                TARGET_SANDBOX_NAME)

        """
        OUTPUT_EXCEL_FILE = os.path.join(FAILED_RECORDS_FOLDER, "FailedRecord_{}.xlsx".format(current_time))
        extract_Error_Details(COMPLETE_FILE_PATH_ERROR_JSON, current_time, OUTPUT_EXCEL_FILE)

        FILENAME = "Error_Diagnostics_Summary_" + str(current_time) + ".txt"
        COMPLETE_FILE_PATH = os.path.join(FAILED_RECORDS_FOLDER, FILENAME)

        with open(COMPLETE_FILE_PATH, 'w') as f:
            f.write("Total number of records                        : {}".format(runSummary_dict["inputRecordCount"]))
            f.write("\n")
            f.write("Total number of records successfully loaded    : {}".format(runSummary_dict["successRecordCount"]))
            f.write("\n")
            f.write("Total number of records failed to load         : {}".format(runSummary_dict["failedRecordCount"]))
            f.write("\n")

        """

    except ValueError as error:
        print('Caught this error: ' + repr(error))