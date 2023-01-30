import json
from generateJWT import generate_jwt_token
import requests
import time
import os

URL_MAP = {
    "RETRIEVE_DATAFLOW" : "https://platform.adobe.io/data/foundation/flowservice/flows/:FLOW_ID",
    "RETRIEVE_MAPPINGSET" : "https://platform.adobe.io/data/foundation/conversion/mappingSets/:MAPPING_SET_ID?expandSchema=false&version=0",
    "" : ""
}

ENVIRONMENT = "PHASE2_STAGE"
OUTPUT_FOLDER = "/Users/bitun.sen/Documents/AbbVie/Data_Ingestion/"

UTIL_HEADER_MAP = {
    "API_KEY" : "88af8f01811e4282b14c6873f363dedc",
    "CLIENT_SECRET" : "p8e-VZKtNqTTBzsvqCwIHrUkgiN31vgm7BJZ",
    "TECHNICAL_ACCOUNT_ID" : "E56B510A6147F1DD0A495ED1@techacct.adobe.com",
    "IMS_ORG_ID" : "C2C7C77B56E2C5147F000101@AdobeOrg",
    "PRIVATE_KEY_FILE" : "/Users/bitun.sen/Documents/AbbVie/Postman_Configuration/config/private.key"
}

access_token = generate_jwt_token(UTIL_HEADER_MAP)

def current_milli_time():
    return round(time.time() * 1000)


def retrieveMappingSet(mappingSetID, sandbox_name):
    URL = "https://platform.adobe.io/data/foundation/conversion/mappingSets/" + str(mappingSetID) + "?expandSchema=false&version=0"

    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key" : UTIL_HEADER_MAP["API_KEY"],
        "x-gw-ims-org-id" : UTIL_HEADER_MAP["IMS_ORG_ID"],
        "x-sandbox-name" : sandbox_name
    }

    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header

    print(URL)
    response = requests.get(URL, headers=req_headers)
    print("HTTP Response : " + response.text)
    mapping_set_json = json.loads(response.text)

    filtered_mapping_set = {}
    invalid_key_set = {"id", "createdDate", "modifiedDate", "createdBy", "modifiedBy", "supportVersion", "status", "version", "inputSchema"}
    for key in mapping_set_json.keys():
        print("Key :: {} ::::::: Value :: {}".format(key, mapping_set_json[key]))
        if key in invalid_key_set:
            continue
        else:
            if key == "mappings":
                mapping_list = mapping_set_json[key]
                filter_mapping_list = []
                for mapping in mapping_list:
                    print(mapping)
                    filtered_mapping = {}
                    for mapping_key in mapping.keys():
                        if mapping_key in invalid_key_set:
                            continue
                        else:
                            filtered_mapping[mapping_key] = mapping[mapping_key]

                    filter_mapping_list.append(filtered_mapping)
                filtered_mapping_set["mappings"] = filter_mapping_list

            elif key == "outputSchema":
                outputSchema_json = mapping_set_json[key]
                filtered_outputSchema = {}
                for outputSchema_key in outputSchema_json.keys():
                    if outputSchema_key in invalid_key_set:
                        continue
                    else:
                        filtered_outputSchema[outputSchema_key] = outputSchema_json[outputSchema_key]

                filtered_mapping_set["outputSchema"] = filtered_outputSchema

            else:
                filtered_mapping_set[key] = mapping_set_json[key]

    return filtered_mapping_set


def writeMappingSetToFile(mapping_name, filtered_mapping_set):
    OUTPUT_FILE = ENVIRONMENT + "_" + mapping_name + "_Mapping_Set_" + str(current_milli_time()) + ".json";
    COMPLETE_FILE_PATH = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
    output_file = open(COMPLETE_FILE_PATH, 'w')
    output_file.write(json.dumps(filtered_mapping_set, default=str, indent=4))
    output_file.close()

def writeSourceConnectionToFile(filtered_source_connection_dict, index):
    OUTPUT_FILE = ENVIRONMENT + "_" + str(index) + "_SourceConnection_" + str(current_milli_time()) + ".json";
    COMPLETE_FILE_PATH = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
    output_file = open(COMPLETE_FILE_PATH, 'w')
    output_file.write(json.dumps(filtered_source_connection_dict, default=str, indent=4))
    output_file.close()

def writeTargetConnectionToFile(filtered_target_connection_dict, index):
    OUTPUT_FILE = ENVIRONMENT + "_" + str(index) + "_TargetConnection_" + str(current_milli_time()) + ".json";
    COMPLETE_FILE_PATH = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
    output_file = open(COMPLETE_FILE_PATH, 'w')
    output_file.write(json.dumps(filtered_target_connection_dict, default=str, indent=4))
    output_file.close()

def retrieveSourceConnection(source_connection_id, sandbox_name):
    URL = "https://platform.adobe.io/data/foundation/flowservice/sourceConnections/" + str(source_connection_id)

    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": UTIL_HEADER_MAP["API_KEY"],
        "x-gw-ims-org-id": UTIL_HEADER_MAP["IMS_ORG_ID"],
        "x-sandbox-name": sandbox_name
    }

    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header

    response = requests.get(URL, headers=req_headers)
    print("Source Connection HTTP Response : " + response.text)

    invalid_key_set = {"id", "createdAt", "updatedAt", "createdBy", "updatedBy", "createdClient", "updatedClient",
                       "sandboxId", "sandboxName", "imsOrgId", "state", "version", "etag", "inheritedAttributes"}
    response_json = json.loads(response.text)
    source_connection_json = response_json["items"]

    count_src = 0
    for source_connection in source_connection_json:
        filtered_source_connection_dict = {}
        count_src = count_src + 1
        for key in source_connection:
            if key in invalid_key_set:
                continue
            else:
                filtered_source_connection_dict[key] = source_connection[key]

        writeSourceConnectionToFile(filtered_source_connection_dict, count_src)


def retrieveTargetConnection(target_connection_id, sandbox_name):
    URL = "https://platform.adobe.io/data/foundation/flowservice/targetConnections/" + str(target_connection_id)

    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": UTIL_HEADER_MAP["API_KEY"],
        "x-gw-ims-org-id": UTIL_HEADER_MAP["IMS_ORG_ID"],
        "x-sandbox-name": sandbox_name
    }

    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header

    response = requests.get(URL, headers=req_headers)
    print("Target Connection HTTP Response : " + response.text)

    invalid_key_set = {"id", "createdAt", "updatedAt", "createdBy", "updatedBy", "createdClient", "updatedClient",
                       "sandboxId", "sandboxName", "imsOrgId", "state", "version", "etag", "inheritedAttributes"}
    response_json = json.loads(response.text)
    target_connection_json = response_json["items"]

    count_src = 0
    for target_connection in target_connection_json:
        filtered_target_connection_dict = {}
        count_src = count_src + 1
        for key in target_connection:
            if key in invalid_key_set:
                continue
            else:
                filtered_target_connection_dict[key] = target_connection[key]

        writeTargetConnectionToFile(filtered_target_connection_dict, count_src)



def retrieveDataflow(dataflowId, sandbox_name):
    URL = "https://platform.adobe.io/data/foundation/flowservice/flows/" + str(dataflowId)

    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": UTIL_HEADER_MAP["API_KEY"],
        "x-gw-ims-org-id": UTIL_HEADER_MAP["IMS_ORG_ID"],
        "x-sandbox-name": sandbox_name
    }

    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header

    response = requests.get(URL, headers=req_headers)
    print("Dataflow HTTP Response : " + response.text)
    dataflow_json = json.loads(response.text)
    dataflow_json = dataflow_json["items"]

    for dataflow_item in dataflow_json:
        source_connections_list = dataflow_item["sourceConnectionIds"]
        for source_connection_id in source_connections_list:
            retrieveSourceConnection(source_connection_id, sandbox_name)

        target_connections_list = dataflow_item["targetConnectionIds"]
        for target_connection_id in target_connections_list:
            retrieveTargetConnection(target_connection_id, sandbox_name)


SOURCE_MAPPING_DETAILS = {
    "PATIENT_DEMOGRAPHY" : "724c85a3a59c459fb2e624b244711bdc",
    "REGISTRATION" : "3d24ab0225ef4c06a78d9ef14c842fd4",
    "REGSURVEY" : "865bfd1c4c0d4cf2bd3c089de7386460",
    "ENGAGEMENTSURVEY" : "19e1fa6c2376414698b642831ef51f74",
    "OPT" : "da1ba059769d449c987b2c8dc3a272db"
}
#retrieveDataflow("ebee28e6-9ef5-41e9-b415-ca002cdcc825", "abbvie-staging")
filtered_mapping_set = retrieveMappingSet("c5f3957cc6524f05b9fe16b5933c73d2", "abbvie-development")
writeMappingSetToFile("ENGAGEMENTSURVEY", filtered_mapping_set)


