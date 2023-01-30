import json
from generateJWT import generate_jwt_token
import requests
import time
import os

SOURCE_ENVIRONMENT = "abbvie-staging"
TARGET_ENVIRONMENT = "prod"
OUTPUT_FOLDER = "/Users/bitun.sen/Documents/AbbVie/Export_Schema/ACSDEV"
CUSTOM_DATATYPE_ID_SET = set()


SCHEMA_URLS = {
    "Patient" : "https%3A%2F%2Fns.adobe.com%2Fabbviecommercial%2Fschemas%2F1ee6fc0711482e90d31572b717b385386e7a9de4d3b300e7",
    "Registration" : "https%3A%2F%2Fns.adobe.com%2Fabbviecommercial%2Fschemas%2F609603e52dd66bd6cc825fdde2e145d3033e4d46de6c84a1",
    "OPT" : "https%3A%2F%2Fns.adobe.com%2Fabbviecommercial%2Fschemas%2F7b13553e7e2572d3807ef2372a90add2dccee699a8c1312b",
    "Survey" : "https%3A%2F%2Fns.adobe.com%2Fabbviecommercial%2Fschemas%2F9a44614e906f80ff029a570b9bb5cbb1845143539dfacd5",
    "WebSDKEvent" : "https%3A%2F%2Fns.adobe.com%2Fabbviecommercial%2Fschemas%2F19d39d77cc22a88ef60b80cb9a939ebfc6c1f2b1966f4560",
    "WebSDKProfile" : "https%3A%2F%2Fns.adobe.com%2Fabbviecommercial%2Fschemas%2Fe2cc0794d2e6168973f14524ccb37471999c3c55b3b64289",
    "PatientIDLinkProfile" : "https%3A%2F%2Fns.adobe.com%2Fabbviecommercial%2Fschemas%2F538923f2d499a7573ed4a49a2436c4590f9a34bedb2c7ff9"
}

SCHEMA_URLS = {
    "WebSDKEvent" : "https%3A%2F%2Fns.adobe.com%2Fabbviecommercial%2Fschemas%2F19d39d77cc22a88ef60b80cb9a939ebfc6c1f2b1966f4560"
}

SOURCE_UTIL_HEADER_MAP = {
    "API_KEY" : "88af8f01811e4282b14c6873f363dedc",
    "CLIENT_SECRET" : "p8e-VZKtNqTTBzsvqCwIHrUkgiN31vgm7BJZ",
    "TECHNICAL_ACCOUNT_ID" : "E56B510A6147F1DD0A495ED1@techacct.adobe.com",
    "IMS_ORG_ID" : "C2C7C77B56E2C5147F000101@AdobeOrg",
    "PRIVATE_KEY_FILE" : "/Users/bitun.sen/Documents/AbbVie/Postman_Configuration/config/private.key"
}

TARGET_UTIL_HEADER_MAP = {
    "API_KEY" : "9d5c3730c7584d7e8112a67a88986ebc",
    "CLIENT_SECRET" : "p8e-2E1fId8dZUv3z3dGufmWmKMmgiy28KzD",
    "TECHNICAL_ACCOUNT_ID" : "0AB01D15627D65B90A495FCF@techacct.adobe.com",
    "IMS_ORG_ID" : "C2C7C77B56E2C5147F000101@AdobeOrg",
    "PRIVATE_KEY_FILE" : "/Users/bitun.sen/Documents/AbbVie/Postman_Configuration/CDP_Production_Migration/private.key"
}


source_access_token = generate_jwt_token(SOURCE_UTIL_HEADER_MAP)
target_access_token = generate_jwt_token(TARGET_UTIL_HEADER_MAP)


COMMON_IDS_SET = set()
REQUIRED_IDENTITIES_SET = set()
CUSTOM_FIELDGROUP_ID_SET = set()


def current_milli_time():
    return round(time.time() * 1000)


def getTenantID(sandbox_name, UTIL_HEADER_MAP, access_token):
    GET_URL = "https://platform.adobe.io/data/foundation/schemaregistry/stats"
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

    response = requests.get(GET_URL, headers=req_headers)
    print("HTTP Response : " + response.text)
    tenant_info_json = json.loads(response.text)
    tenant_id = tenant_info_json["tenantId"]
    return tenant_id

def getAllExistingIdentities(sandbox_name, UTIL_HEADER_MAP, access_token):
    GET_URL = "https://platform.adobe.io/data/core/idnamespace/identities"
    req_headers = {
        "Accept": "application/vnd.adobe.xdm-link+json; version=1",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": UTIL_HEADER_MAP["API_KEY"],
        "x-gw-ims-org-id": UTIL_HEADER_MAP["IMS_ORG_ID"],
        "x-sandbox-name": sandbox_name
    }
    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header

    response = requests.get(GET_URL, headers=req_headers)
    print("Get Tenant Details HTTP Response : " + response.text)
    identities_json = json.loads(response.text)

    return identities_json



def exportSchemaFromSourceSandbox(schema_id, sandbox_name, UTIL_HEADER_MAP, access_token):
    EXPORT_URL = "https://platform.adobe.io/data/foundation/schemaregistry/rpc/export/" + str(schema_id)

    req_headers = {
        "Accept": "application/vnd.adobe.xdm-link+json; version=1",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": UTIL_HEADER_MAP["API_KEY"],
        "x-gw-ims-org-id": UTIL_HEADER_MAP["IMS_ORG_ID"],
        "x-sandbox-name": sandbox_name
    }

    auth_header = "Bearer " + access_token
    req_headers["Authorization"] = auth_header

    response = requests.get(EXPORT_URL, headers=req_headers)
    print("Export Schema HTTP Response : " + response.text)
    schema_json = json.loads(response.text)
    return schema_json


def writeMappingSetToFile(schema_payload, schema_name):
    OUTPUT_FILE = TARGET_ENVIRONMENT.upper() + "_" + schema_name + "_" + str(current_milli_time()) + ".json";
    COMPLETE_FILE_PATH = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
    output_file = open(COMPLETE_FILE_PATH, 'w')
    output_file.write(json.dumps(schema_payload, default=str, indent=4))
    output_file.close()

def getAllCustomDataTypesFromTarget(sandbox_name):
    GET_DATATYPE_URL = "https://platform.adobe.io/data/foundation/schemaregistry/tenant/datatypes"
    req_headers = {
        "Accept": "application/vnd.adobe.xed-id+json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": TARGET_UTIL_HEADER_MAP["API_KEY"],
        "x-gw-ims-org-id": TARGET_UTIL_HEADER_MAP["IMS_ORG_ID"],
        "x-sandbox-name": sandbox_name
    }

    auth_header = "Bearer " + target_access_token
    req_headers["Authorization"] = auth_header

    response = requests.get(GET_DATATYPE_URL, headers=req_headers)
    print("Get All Data Types HTTP Response : " + response.text)
    custom_data_type_json = json.loads(response.text)
    custom_data_type_list = custom_data_type_json["results"]
    data_type_id_set = set()
    for data_type in custom_data_type_list:
        data_type_id = data_type["meta:altId"]
        #data_type_id = "datatypes." + data_type_id.split(".datatypes.")[1]
        data_type_id_set.add(data_type_id)

    return data_type_id_set


def getAllCustomFieldGroupsFromTarget(sandbox_name):
    GET_FG_URL = "https://platform.adobe.io/data/foundation/schemaregistry/tenant/fieldgroups"
    req_headers = {
        "Accept": "application/vnd.adobe.xed-id+json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {{ACCESS_TOKEN}}",
        "x-api-key": TARGET_UTIL_HEADER_MAP["API_KEY"],
        "x-gw-ims-org-id": TARGET_UTIL_HEADER_MAP["IMS_ORG_ID"],
        "x-sandbox-name": sandbox_name
    }

    auth_header = "Bearer " + target_access_token
    req_headers["Authorization"] = auth_header

    response = requests.get(GET_FG_URL, headers=req_headers)
    print("Get All Field Groups HTTP Response : " + response.text)
    custom_field_group_json = json.loads(response.text)
    custom_field_group_list = custom_field_group_json["results"]
    field_group_id_set = set()
    for field_group in custom_field_group_list:
        field_group_id = field_group["meta:altId"]
        #field_group_id = "mixins." + field_group_id.split(".mixins.")[1]
        field_group_id_set.add(field_group_id)

    return field_group_id_set



def parseAndCleanSchema(schema_json, tenant_id):
    schema_json_items = []
    for item in schema_json:
        if item["meta:resourceType"] == "schemas":
            schema_id = item["meta:altId"]
            if schema_id not in COMMON_IDS_SET:
                schema_json_items.append(item)
                COMMON_IDS_SET.add(schema_id)

        elif item["meta:resourceType"] == "descriptors":
            schema_json_items.append(item)
            if item["@type"] == "xdm:descriptorIdentity":
                identity_namespace = item["xdm:namespace"]
                REQUIRED_IDENTITIES_SET.add(identity_namespace)

        elif item["meta:resourceType"] == "datatypes":
            datatype_id = item["meta:altId"]

            if datatype_id not in COMMON_IDS_SET:
                data_type_id = "_" + str(tenant_id) + ".datatypes." + datatype_id.split(".datatypes.")[1]
                if data_type_id not in CUSTOM_DATATYPE_ID_SET:
                    schema_json_items.append(item)
                #schema_json_items.append(item)
                COMMON_IDS_SET.add(datatype_id)
        elif item["meta:resourceType"] == "mixins":
            mixins_id = item["meta:altId"]
            if mixins_id not in COMMON_IDS_SET:
                field_group_id = "_" + str(tenant_id) + ".mixins." + mixins_id.split(".mixins.")[1]
                if field_group_id not in CUSTOM_FIELDGROUP_ID_SET:
                    schema_json_items.append(item)
                #schema_json_items.append(item)
                COMMON_IDS_SET.add(mixins_id)
        else:
            schema_json_items.append(item)

    return schema_json_items


def importSchemaIntoTargetSandbox(cleaned_schema_json, sandbox_name, UTIL_HEADER_MAP, access_token):
    IMPORT_URL = "https://platform.adobe.io/data/foundation/schemaregistry/rpc/import"

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

    request_body = json.dumps(cleaned_schema_json, default=str)
    response = requests.post(IMPORT_URL, data=request_body, headers=req_headers)
    print("HTTP Response : " + response.text)


def cleanIdentityAndCreate(identity, sandbox_name, UTIL_HEADER_MAP, access_token):
    invalid_key_set = {"id", "createTime", "updateTime", "status"}
    cleaned_identity = {}
    for key in identity.keys():
        if key not in invalid_key_set:
            cleaned_identity[key] = identity[key]

    if len(cleaned_identity) > 0:
        CREATE_IDENTITY_URL = "https://platform.adobe.io/data/core/idnamespace/identities"
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

        request_body = json.dumps(cleaned_identity, default=str)
        response = requests.post(CREATE_IDENTITY_URL, data=request_body, headers=req_headers)
        print("Create Identity HTTP Response : " + response.text)

    return cleaned_identity


if __name__ == "__main__":
    CUSTOM_DATATYPE_ID_SET = getAllCustomDataTypesFromTarget(TARGET_ENVIRONMENT)
    print("Custom Dataset Ids :: {}".format(CUSTOM_DATATYPE_ID_SET))
    CUSTOM_FIELDGROUP_ID_SET = getAllCustomFieldGroupsFromTarget(TARGET_ENVIRONMENT)

    tenant_id = getTenantID(SOURCE_ENVIRONMENT, SOURCE_UTIL_HEADER_MAP, source_access_token)
    SCHEMA_PAYLOAD_LIST = []

    for key in SCHEMA_URLS.keys():
        schema_json = exportSchemaFromSourceSandbox(SCHEMA_URLS[key], SOURCE_ENVIRONMENT, SOURCE_UTIL_HEADER_MAP, source_access_token)
        cleaned_schema_json = parseAndCleanSchema(schema_json, tenant_id)
        writeMappingSetToFile(cleaned_schema_json, key)
        SCHEMA_PAYLOAD_LIST.append(cleaned_schema_json)

    source_identities_json = getAllExistingIdentities(SOURCE_ENVIRONMENT, SOURCE_UTIL_HEADER_MAP, source_access_token)
    target_identities_json = getAllExistingIdentities(TARGET_ENVIRONMENT, TARGET_UTIL_HEADER_MAP, target_access_token)
    source_identities_dict = {}
    target_identities_set = set()

    for identity in source_identities_json:
        identity_code = identity["code"]
        #print("Identity :: {}".format(identity_code))
        if identity_code in REQUIRED_IDENTITIES_SET:
            source_identities_dict[identity_code] = identity

    #print(json.dumps(source_identities_dict))

    for identity in target_identities_json:
        identity_code = identity["code"]
        target_identities_set.add(identity_code)

    for identity_code in source_identities_dict.keys():
        if identity_code not in target_identities_set:
            identity = source_identities_dict[identity_code]
            cleaned_identity = cleanIdentityAndCreate(identity, TARGET_ENVIRONMENT, TARGET_UTIL_HEADER_MAP, target_access_token)
            print("Need to create :: {}".format(json.dumps(cleaned_identity)))

    for payload in SCHEMA_PAYLOAD_LIST:
        importSchemaIntoTargetSandbox(payload, TARGET_ENVIRONMENT, TARGET_UTIL_HEADER_MAP, target_access_token)


