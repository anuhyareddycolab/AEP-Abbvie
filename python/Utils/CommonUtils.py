import time
import os
import os.path
import json
import jwt
import requests
import datetime

def currentTimeInMilliseconds():
    return round(time.time() * 1000)

def getCurrentEpochTime():
    return int(time.time())

def addMinutesToCurrentEpochTime(seconds):
    epoch = int(time.time()) + seconds
    return epoch

def load_configuration(config_file_path):
    config_json = ""
    if os.path.isfile(config_file_path):
        text_file = open(config_file_path, "r")
        # read whole file to a string
        config_data = text_file.read()
        # close file
        text_file.close()
        config_json = json.loads(config_data)
    else:
        raise RuntimeError("Configuration file is missing.")

    return config_json


def getAPIConnectionDetails(config_json, api_project_type):

    if api_project_type in config_json["abbVie"]["instanceDetails"]:
        connection_json = config_json["abbVie"]["instanceDetails"][api_project_type]

        if "private_key_path" in connection_json:
            if os.path.exists(connection_json["private_key_path"]):
                return connection_json
            else:
                raise RuntimeError(
                    "Private Key file specified in Configuration file does not exists.")
        else:
            raise RuntimeError(
                "No entry found for Private Key file in Configuration file.")
    else:
        raise RuntimeError(
            "Configuration for security credentials is not present in Configuration file.")


def generate_jwt_token(JWT_PARAM_DICT):
    url = 'https://ims-na1.adobelogin.com/ims/exchange/jwt'
    jwtPayloadRaw = """{ "iss": "##ims_org##",
                         "sub": "##technical_account_id##",
                         "https://ims-na1.adobelogin.com/s/ent_dataservices_sdk": true,
                         "aud": "https://ims-na1.adobelogin.com/c/##api_key##" }"""

    for key in JWT_PARAM_DICT.keys():
        print("Key :: {} ::::::: Value :: {}".format(key, JWT_PARAM_DICT[key]))
        jwtPayloadRaw = jwtPayloadRaw.replace("##" + key + "##", JWT_PARAM_DICT[key])

    print(jwtPayloadRaw)
    jwtPayloadJson = json.loads(jwtPayloadRaw)
    jwtPayloadJson["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    accessTokenRequestPayload = {
        'client_id': JWT_PARAM_DICT["api_key"],
        'client_secret': JWT_PARAM_DICT["secret"]
    }

    # Request Access Key
    # This Needs to point at where your private key is on the file system
    keyfile = open(JWT_PARAM_DICT["private_key_path"], 'r')
    private_key = keyfile.read()

    # Encode the jwt Token
    jwttoken = jwt.encode(jwtPayloadJson, private_key, algorithm='RS256')
    # print("Encoded JWT Token")
    # print(jwttoken.decode('utf-8'))

    # We are making a http request simmilar to this curl request
    accessTokenRequestPayload['jwt_token'] = jwttoken
    result = requests.post(url, data=accessTokenRequestPayload)
    print(result)
    resultjson = json.loads(result.text);
    # print("Full output from the access token request")
    # print(json.dumps(resultjson, indent=4, sort_keys=True))

    # Echo out the access token
    print(resultjson["access_token"]);

    return resultjson["access_token"]


def getProperty(path, config_json):
    value = ""
    print("[getProperty] Path :: {}".format(path))
    pathArray = path.split(".")
    config_json_temp = config_json

    for item in pathArray:
        if item in config_json_temp:
            config_json_temp = config_json_temp[item]
        else:
            raise RuntimeError("Invalid Path provided :: {}".format(item))

    return config_json_temp




