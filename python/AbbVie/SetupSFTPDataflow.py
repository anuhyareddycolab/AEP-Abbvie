from Utils import CommonUtils as tautils
import json
import requests
import time
import os


access_token = ""

DATAFLOW_DETAILS_DICT = {
    "SOURCE_CONN_ID": "",
    "TARGET_CONN_ID": "",
    "MAPPING_SET_ID": ""
}



def validateInput(dataGroup, target_environment, config_json):
    env_keys = config_json["abbVie"]["dataload"].keys()
    if target_environment in env_keys:
        print("")
        if "datasetDetails" in config_json["abbVie"]["dataload"][target_environment]:
            if dataGroup in config_json["abbVie"]["dataload"][target_environment]["datasetDetails"]:
                print("")
            else:
                raise RuntimeError("Configuration for datagroup {} is not present in Configuration file.".format(dataGroup))
        else:
            raise RuntimeError("Configuration for datasetDetails is not present in Configuration file.")
    else:
        raise RuntimeError("Configuration for Sandbox {} is not present in Configuration file.".format(target_environment))



def createSourceConnection(dataflow_name, base_connection_id, connection_spec_id, source_file_path, sandbox_name, security_credentials):
    SOURCE_CONN_URL = "https://platform.adobe.io/data/foundation/flowservice/sourceConnections"
    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": security_credentials["api_key"],
        "x-gw-ims-org-id": security_credentials["ims_org"],
        "x-sandbox-name": sandbox_name
    }
    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header

    source_conn_json = {
        "name": dataflow_name + " Source Connection - " + str(tautils.currentTimeInMilliseconds()),
        "description": dataflow_name + " Source Connection - " + str(tautils.currentTimeInMilliseconds()),
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


def deleteSourceConnection(source_connection_id, sandbox_name, security_credentials):
    DELETE_URL = "https://platform.adobe.io/data/foundation/flowservice/sourceConnections/" + str(source_connection_id)
    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": security_credentials["api_key"],
        "x-gw-ims-org-id": security_credentials["ims_org"],
        "x-sandbox-name": sandbox_name
    }
    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header
    print("Deleting Source Connection : Source Connection ID : {}".format(source_connection_id))
    response = requests.delete(DELETE_URL, headers=req_headers)
    print("Delete Source Connection HTTP Response : " + response.text)


def createTargetConnection(dataflow_name, target_schema_id, connection_spec_id, target_dataset_id, sandbox_name, security_credentials):
    TARGET_CONN_URL = "https://platform.adobe.io/data/foundation/flowservice/targetConnections"
    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": security_credentials["api_key"],
        "x-gw-ims-org-id": security_credentials["ims_org"],
        "x-sandbox-name": sandbox_name
    }
    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header

    target_conn_json = {
        "name": dataflow_name + " Target Connection - " + str(tautils.currentTimeInMilliseconds()),
        "description": dataflow_name + " Target Connection - " + str(tautils.currentTimeInMilliseconds()),
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


def deleteTargetConnection(target_connection_id, sandbox_name, security_credentials):
    DELETE_URL = "https://platform.adobe.io/data/foundation/flowservice/targetConnections/" + str(target_connection_id)
    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": security_credentials["api_key"],
        "x-gw-ims-org-id": security_credentials["ims_org"],
        "x-sandbox-name": sandbox_name
    }
    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header
    print("Deleting Target Connection : Target Connection ID : {}".format(target_connection_id))
    response = requests.delete(DELETE_URL, headers=req_headers)
    print("Delete Target Connection HTTP Response : " + response.text)


def createMappingSet(mapping_set_file_path, sandbox_name, security_credentials):
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
            "x-api-key": security_credentials["api_key"],
            "x-gw-ims-org-id": security_credentials["ims_org"],
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


def createDataflow(dataflow_name, source_connection_id, target_connection_id, mapping_set_id, sandbox_name, security_credentials, file_index):
    CREATE_DATAFLOW_URL = "https://platform.adobe.io/data/foundation/flowservice/flows"
    dataflow_json = {
        "name": dataflow_name + " Dataflow - " + str(tautils.currentTimeInMilliseconds()),
        "description": dataflow_name + " Dataflow - " + str(tautils.currentTimeInMilliseconds()),
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
            "startTime": tautils.addMinutesToCurrentEpochTime(file_index*300)
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
        "x-api-key": security_credentials["api_key"],
        "x-gw-ims-org-id": security_credentials["ims_org"],
        "x-sandbox-name": sandbox_name
    }
    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header
    request_body = json.dumps(dataflow_json, default=str)
    print("Create Dataflow Request : {}".format(request_body))
    response = requests.post(CREATE_DATAFLOW_URL, data=request_body, headers=req_headers)
    print("Create Dataflow :: HTTP Response : " + response.text)
    dataflow_response_json = json.loads(response.text)
    dataflow_id = dataflow_response_json["id"]
    print("Created Dataflow ID : {}".format(dataflow_response_json["id"]))
    return dataflow_id


def configureDataFlow(fileset_name, sandbox_name, security_credentials, config_json):
    try:
        # Create Source Connection
        target_connection_spec_id = tautils.getProperty("abbVie.commonDetails.SFTP.targetConnectionSpecId", config_json)
        source_connection_spec_id = tautils.getProperty("abbVie.commonDetails.SFTP.sourceConnectionSpecId", config_json)
        sftp_source_connection_id = tautils.getProperty("abbVie.dataload." + sandbox_name + ".sftpSourceConnectionId", config_json)
        source_file_path_array = tautils.getProperty("abbVie.dataload." + sandbox_name + ".inputFiles." + fileset_name, config_json)
        target_dataset_id = tautils.getProperty("abbVie.dataload." + sandbox_name + ".datasetDetails." + fileset_name + ".datasetId", config_json)
        target_schema_id = tautils.getProperty(
            "abbVie.dataload." + sandbox_name + ".datasetDetails." + fileset_name + ".schemaId", config_json)
        mapping_set_file_path = tautils.getProperty(
            "abbVie.dataload." + sandbox_name + ".datasetDetails." + fileset_name + ".mappingFilePath", config_json)

        file_index = 1
        for input_file in source_file_path_array:
            DATAFLOW_DETAILS_DICT["SOURCE_CONN_ID"] = createSourceConnection(fileset_name,
                                                                         sftp_source_connection_id,
                                                                         source_connection_spec_id,
                                                                         input_file,
                                                                         sandbox_name, security_credentials)

            DATAFLOW_DETAILS_DICT["TARGET_CONN_ID"] = createTargetConnection(fileset_name,
                                                                         target_schema_id,
                                                                         target_connection_spec_id,
                                                                         target_dataset_id,
                                                                         sandbox_name, security_credentials)

            DATAFLOW_DETAILS_DICT["MAPPING_SET_ID"] = createMappingSet(
                                                            mapping_set_file_path,
                                                            sandbox_name, security_credentials)
            print("Created Mapping Set :: {}".format(DATAFLOW_DETAILS_DICT["MAPPING_SET_ID"]))

            dataflow_id = createDataflow(fileset_name,
                                         DATAFLOW_DETAILS_DICT["SOURCE_CONN_ID"],
                                         DATAFLOW_DETAILS_DICT["TARGET_CONN_ID"],
                                         DATAFLOW_DETAILS_DICT["MAPPING_SET_ID"], sandbox_name, security_credentials, file_index)
            print("Created Dataflow ID :: {}".format(dataflow_id))
            file_index = file_index + 1

    except ValueError as err:
        print("Exception occurred ::: ", err)
        if len(DATAFLOW_DETAILS_DICT["SOURCE_CONN_ID"]) > 0:
            deleteSourceConnection(DATAFLOW_DETAILS_DICT["SOURCE_CONN_ID"], sandbox_name)

        if len(DATAFLOW_DETAILS_DICT["TARGET_CONN_ID"]) > 0:
            deleteTargetConnection(DATAFLOW_DETAILS_DICT["TARGET_CONN_ID"], sandbox_name)


if __name__ == "__main__":
    config_json = tautils.load_configuration("D:\\Official\\AEP\\Abbvie\\python\\pproject\\abbVieConfig.json")

    TARGET_ENVIRONMENT = "abbvie-development"
    API_PROJECT_TYPE = "dev"

    security_credentials = tautils.getAPIConnectionDetails(config_json, API_PROJECT_TYPE)
    access_token = tautils.generate_jwt_token(security_credentials)
    print("Access Token :: {}".format(access_token))


    configureDataFlow("PATIENT_DEMOGRAPHY", TARGET_ENVIRONMENT, security_credentials, config_json)
