import json
from generateJWT import generate_jwt_token
import requests
import time
import os
from Utils import CommonUtils as bsutils


SOURCE_ENVIRONMENT = "prod"
TARGET_ENVIRONMENT = "abbvie-staging"

TARGET_ENVIRONMENT_DETAILS = {
    "abbvie-staging" : {
        "TARGET_SFTP_SOURCE_CONN_ID": "0434c183-63ad-4d49-a359-58e88e67d9fa"
    },
    "acs-dev" : {
        "TARGET_SFTP_SOURCE_CONN_ID": "48460874-2dc4-483a-99ec-ff36cd3899d5"
    }
}
COMMON_BASIC_DETAILS = {
    "TARGET_SFTP_SOURCE_CONN_ID": "48460874-2dc4-483a-99ec-ff36cd3899d5",
    "SFTP_CONN_SPEC_ID": "b7bf2577-4520-42c9-bae9-cad01560f7bc",
    "TARGET_CONN_SPEC_ID": "c604ff05-7f1a-43c0-8e18-33bf874cb11c"
}

ENVIRONMENT_DATASET_ID = {
    "abbvie-staging" : {
        "PATIENT_DEMOGRAPHY" : "62790bd34000f61949bee303",
        "REGISTRATION" : "6263830358a78f1949e0b516",
        "REGSURVEY" : "626383649e5a1e19497feffd",
        "ENGAGEMENTSURVEY" : "626383649e5a1e19497feffd",
        "OPT" : "6263832d7c6cec194a51635e"
    },
    "acs-dev" : {
        "PATIENT_DEMOGRAPHY" : "627400cd5e6c79194874ee13",
        "REGISTRATION" : "6274010a365db8194a9a437d",
        "REGSURVEY" : "627401e5d6ba86194a0fa260",
        "ENGAGEMENTSURVEY" : "627401e5d6ba86194a0fa260",
        "OPT" : "627400ecdd4b37194b42e1ff"
    }
}

INPUT_FILE_SPECIFIC_DETAILS = {
    "PATIENT_DEMOGRAPHY" : {
        "SOURCE_FILE_PATH": "/ORG-PS-CDP-NP/Epsilon/Initial_Data_Load/TEST_ABOT_EPSI_DEMOGRAPHIC_CDP_20220422010203_138813.csv",
        "MAPPING_SET_FILE_PATH": "/Users/bitun.sen/Documents/AbbVie/Data_Ingestion/PROD_PatientDemography_Mapping_Set_1651784825667.json",
        "TARGET_SCHEMA_ID": "https://ns.adobe.com/abbviecommercial/schemas/1ee6fc0711482e90d31572b717b385386e7a9de4d3b300e7",
        "TARGET_DATASET_ID": ""
    },
    "REGISTRATION" : {
        "SOURCE_FILE_PATH": "/ORG-PS-CDP-NP/Epsilon/Initial_Data_Load/TEST_ABOT_EPSI_REGISTRATION_CDP_20220422010203_335938.csv",
        "MAPPING_SET_FILE_PATH": "/Users/bitun.sen/Documents/AbbVie/Data_Ingestion/PROD_Registration_Mapping_Set_1651847214772.json",
        "TARGET_SCHEMA_ID": "https://ns.adobe.com/abbviecommercial/schemas/609603e52dd66bd6cc825fdde2e145d3033e4d46de6c84a1",
        "TARGET_DATASET_ID": "6274010a365db8194a9a437d"
    },
    "REGSURVEY" : {
        "SOURCE_FILE_PATH": "/ORG-PS-CDP-NP/Epsilon/Initial_Data_Load/TEST_ABOT_EPSI_REGSURVEY_CDP_20220422010203_2081315.csv",
        "MAPPING_SET_FILE_PATH": "/Users/bitun.sen/Documents/AbbVie/Data_Ingestion/PROD_REGSURVEY_Mapping_Set_1651852178363.json",
        "TARGET_SCHEMA_ID": "https://ns.adobe.com/abbviecommercial/schemas/9a44614e906f80ff029a570b9bb5cbb1845143539dfacd5",
        "TARGET_DATASET_ID": "627401e5d6ba86194a0fa260"
    },
    "ENGAGEMENTSURVEY" : {
        "SOURCE_FILE_PATH": "/ORG-PS-CDP-NP/Epsilon/Initial_Data_Load/TEST_ABOT_EPSI_ENGAGEMENTSRVY_CDP_20220422010203_1488379.csv",
        "MAPPING_SET_FILE_PATH": "/Users/bitun.sen/Documents/AbbVie/Data_Ingestion/PROD_ENGAGEMENTSURVEY_Mapping_Set_1651852712980.json",
        "TARGET_SCHEMA_ID": "https://ns.adobe.com/abbviecommercial/schemas/9a44614e906f80ff029a570b9bb5cbb1845143539dfacd5",
        "TARGET_DATASET_ID": "627401e5d6ba86194a0fa260"
    },
    "OPT" : {
        "SOURCE_FILE_PATH": "/ORG-PS-CDP-NP/Epsilon/Initial_Data_Load/TEST_ABOT_EPSI_OPT_CDP_20220422010203_1725949.csv",
        "MAPPING_SET_FILE_PATH": "/Users/bitun.sen/Documents/AbbVie/Data_Ingestion/PROD_OPTEVENT_Mapping_Set_1651852149915.json",
        "TARGET_SCHEMA_ID": "https://ns.adobe.com/abbviecommercial/schemas/7b13553e7e2572d3807ef2372a90add2dccee699a8c1312b",
        "TARGET_DATASET_ID": "627400ecdd4b37194b42e1ff"
    }
}

UTIL_HEADER_MAP = {
    "API_KEY": "88af8f01811e4282b14c6873f363dedc",
    "CLIENT_SECRET": "p8e-VZKtNqTTBzsvqCwIHrUkgiN31vgm7BJZ",
    "TECHNICAL_ACCOUNT_ID": "E56B510A6147F1DD0A495ED1@techacct.adobe.com",
    "IMS_ORG_ID": "C2C7C77B56E2C5147F000101@AdobeOrg",
    "PRIVATE_KEY_FILE": "/Users/bitun.sen/Documents/AbbVie/Postman_Configuration/config/private.key"
}

DATAFLOW_DETAILS_DICT = {
    "SOURCE_CONN_ID": "",
    "TARGET_CONN_ID": "",
    "MAPPING_SET_ID": ""
}

access_token = generate_jwt_token(UTIL_HEADER_MAP)


def current_milli_time():
    return round(time.time() * 1000)


def createSourceConnection(dataflow_name, base_connection_id, connection_spec_id, source_file_path, sandbox_name):
    SOURCE_CONN_URL = "https://platform.adobe.io/data/foundation/flowservice/sourceConnections"
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

    source_conn_json = {
        "name": dataflow_name + " Source Connection - " + str(current_milli_time()),
        "description": dataflow_name + " Source Connection - " + str(current_milli_time()),
        "baseConnectionId": str(base_connection_id),
        "data": {
            "format": "delimited"
        },
        "connectionSpec": {
            "id": str(connection_spec_id),
            "version": "1.0"
        },
        "params": {
            "type": "file",
            "path": str(source_file_path)
        }
    }

    request_body = json.dumps(source_conn_json, default=str)
    response = requests.post(SOURCE_CONN_URL, data=request_body, headers=req_headers)
    print("Create Source Connection :: HTTP Response : " + response.text)
    source_connection_response_json = json.loads(response.text)
    source_connection_id = source_connection_response_json["id"]
    print("Created Source Connection ID : {}".format(source_connection_response_json["id"]))
    return source_connection_id


def deleteSourceConnection(source_connection_id, sandbox_name):
    DELETE_URL = "https://platform.adobe.io/data/foundation/flowservice/sourceConnections/" + str(source_connection_id)
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
    print("Deleting Source Connection : Source Connection ID : {}".format(source_connection_id))
    response = requests.delete(DELETE_URL, headers=req_headers)
    print("Delete Source Connection HTTP Response : " + response.text)


def createTargetConnection(dataflow_name, target_schema_id, connection_spec_id, target_dataset_id, sandbox_name):
    TARGET_CONN_URL = "https://platform.adobe.io/data/foundation/flowservice/targetConnections"
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

    target_conn_json = {
        "name": dataflow_name + " Target Connection - " + str(current_milli_time()),
        "description": dataflow_name + " Target Connection - " + str(current_milli_time()),
        "data": {
            "format": "delimited",
            "schema": {
                "version": "application/vnd.adobe.xed-full+json;version=1",
                "id": str(target_schema_id)
            }
        },
        "connectionSpec": {
            "id": str(connection_spec_id),
            "version": "1.0"
        },
        "params": {
            "dataSetId": str(target_dataset_id)
        }
    }

    request_body = json.dumps(target_conn_json, default=str)
    response = requests.post(TARGET_CONN_URL, data=request_body, headers=req_headers)
    print("Create Target Connection :: HTTP Response : " + response.text)
    target_connection_response_json = json.loads(response.text)
    target_connection_id = target_connection_response_json["id"]
    print("Created Target Connection ID : {}".format(target_connection_response_json["id"]))
    return target_connection_id


def deleteTargetConnection(target_connection_id, sandbox_name):
    DELETE_URL = "https://platform.adobe.io/data/foundation/flowservice/targetConnections/" + str(target_connection_id)
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
    print("Deleting Target Connection : Target Connection ID : {}".format(target_connection_id))
    response = requests.delete(DELETE_URL, headers=req_headers)
    print("Delete Target Connection HTTP Response : " + response.text)


def createMappingSet(mapping_set_file_path, sandbox_name):
    if os.path.isfile(mapping_set_file_path):
        # open text file in read mode
        text_file = open(mapping_set_file_path, "r")
        # read whole file to a string
        mapping_set_data = text_file.read()
        # close file
        text_file.close()
        mapping_set_json = json.loads(mapping_set_data)

        CREATE_MAPPING_URL = "https://platform.adobe.io/data/foundation/conversion/mappingSets"
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
        request_body = json.dumps(mapping_set_json, default=str)
        response = requests.post(CREATE_MAPPING_URL, data=request_body, headers=req_headers)
        print("Create Mapping Set :: HTTP Response : " + response.text)
        mapping_set_response_json = json.loads(response.text)
        mapping_set_id = mapping_set_response_json["id"]
        print("Created Mapping Set ID : {}".format(mapping_set_response_json["id"]))
        return mapping_set_id

    else:
        raise ValueError('Mapping file not found : {}'.format(mapping_set_file_path))


def createDataflow(dataflow_name, source_connection_id, target_connection_id, mapping_set_id, sandbox_name):
    CREATE_DATAFLOW_URL = "https://platform.adobe.io/data/foundation/flowservice/flows"
    dataflow_json = {
        "name": dataflow_name + " Dataflow - " + str(current_milli_time()),
        "description": dataflow_name + " Dataflow - " + str(current_milli_time()),
        "flowSpec": {
            "id": "9753525b-82c7-4dce-8a9b-5ccfce2b9876",
            "version": "1.0"
        },
        "sourceConnectionIds": [
            str(source_connection_id)
        ],
        "targetConnectionIds": [
            str(target_connection_id)
        ],
        "options": {
            "partialIngestionPercent": 50,
            "errorDiagnosticsEnabled": True
        },
        "scheduleParams": {
            "frequency": "once",
            "startTime": bsutils.addMinutesToCurrentEpochTime(300)
        },
        "transformations": [
            {
                "name": "Mapping",
                "params": {
                    "mappingId": str(mapping_set_id),
                    "mappingVersion": "0"
                }
            }
        ]
    }

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
    request_body = json.dumps(dataflow_json, default=str)
    response = requests.post(CREATE_DATAFLOW_URL, data=request_body, headers=req_headers)
    print("Create Dataflow :: HTTP Response : " + response.text)
    dataflow_response_json = json.loads(response.text)
    dataflow_id = dataflow_response_json["id"]
    print("Created Dataflow ID : {}".format(dataflow_response_json["id"]))
    return dataflow_id



def configureDataFlow(fileset_name, sandbox_name):
    try:
        # Create Source Connection

        target_dataset_id = ENVIRONMENT_DATASET_ID[sandbox_name][fileset_name]
        sftp_connection_id = TARGET_ENVIRONMENT_DETAILS[sandbox_name]["TARGET_SFTP_SOURCE_CONN_ID"]

        DATAFLOW_DETAILS_DICT["SOURCE_CONN_ID"] = createSourceConnection(fileset_name,
                                       sftp_connection_id,
                                       COMMON_BASIC_DETAILS["SFTP_CONN_SPEC_ID"],
                                       INPUT_FILE_SPECIFIC_DETAILS[fileset_name]['SOURCE_FILE_PATH'],
                                       sandbox_name)
    
    
        DATAFLOW_DETAILS_DICT["TARGET_CONN_ID"] = createTargetConnection(fileset_name,
                                       INPUT_FILE_SPECIFIC_DETAILS[fileset_name]["TARGET_SCHEMA_ID"],
                                       COMMON_BASIC_DETAILS["TARGET_CONN_SPEC_ID"],
                                       target_dataset_id,
                                       sandbox_name)


        DATAFLOW_DETAILS_DICT["MAPPING_SET_ID"] = createMappingSet(
                                        INPUT_FILE_SPECIFIC_DETAILS[fileset_name]["MAPPING_SET_FILE_PATH"],
                                        sandbox_name)
        print("Created Mapping Set :: {}".format(DATAFLOW_DETAILS_DICT["MAPPING_SET_ID"]))

        dataflow_id = createDataflow(fileset_name,
                                     DATAFLOW_DETAILS_DICT["SOURCE_CONN_ID"],
                                     DATAFLOW_DETAILS_DICT["TARGET_CONN_ID"],
                                     DATAFLOW_DETAILS_DICT["MAPPING_SET_ID"], sandbox_name)
        print("Created Dataflow ID :: {}".format(dataflow_id))

    except ValueError as err:
        print("Exception occurred ::: ", err)
        if len(DATAFLOW_DETAILS_DICT["SOURCE_CONN_ID"]) > 0:
            deleteSourceConnection(DATAFLOW_DETAILS_DICT["SOURCE_CONN_ID"], sandbox_name)

        if len(DATAFLOW_DETAILS_DICT["TARGET_CONN_ID"]) > 0:
            deleteTargetConnection(DATAFLOW_DETAILS_DICT["TARGET_CONN_ID"], sandbox_name)


configureDataFlow("OPT", TARGET_ENVIRONMENT)
