import datetime
import json
import jwt
import os
import requests

def generate_jwt_token(JWT_PARAM_DICT):
    url = 'https://ims-na1.adobelogin.com/ims/exchange/jwt'
    jwtPayloadRaw = """{ "iss": "##IMS_ORG_ID##",
                         "sub": "##TECHNICAL_ACCOUNT_ID##",
                         "https://ims-na1.adobelogin.com/s/ent_dataservices_sdk": true,
                         "aud": "https://ims-na1.adobelogin.com/c/##API_KEY##" }"""

    for key in JWT_PARAM_DICT.keys():
        print("Key :: {} ::::::: Value :: {}".format(key, JWT_PARAM_DICT[key]))
        jwtPayloadRaw = jwtPayloadRaw.replace("##" + key + "##", JWT_PARAM_DICT[key])

    print(jwtPayloadRaw)
    jwtPayloadJson = json.loads(jwtPayloadRaw)
    jwtPayloadJson["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    accessTokenRequestPayload = {
        'client_id': JWT_PARAM_DICT["API_KEY"],
        'client_secret': JWT_PARAM_DICT["CLIENT_SECRET"]
    }

    # Request Access Key
    # This Needs to point at where your private key is on the file system
    keyfile = open(JWT_PARAM_DICT["PRIVATE_KEY_FILE"], 'r')
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


def generate_jwt():
    # Config Data
    url = 'https://ims-na1.adobelogin.com/ims/exchange/jwt'
    jwtPayloadRaw = """{ "iss": "C2C7C77B56E2C5147F000101@AdobeOrg",
                     "sub": "E56B510A6147F1DD0A495ED1@techacct.adobe.com",
                     "https://ims-na1.adobelogin.com/s/ent_dataservices_sdk": true,
                     "aud": "https://ims-na1.adobelogin.com/c/88af8f01811e4282b14c6873f363dedc" }"""
    jwtPayloadJson = json.loads(jwtPayloadRaw)
    jwtPayloadJson["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    accessTokenRequestPayload = {'client_id': '88af8f01811e4282b14c6873f363dedc'
                            ,'client_secret': 'p8e-VZKtNqTTBzsvqCwIHrUkgiN31vgm7BJZ'}

    # Request Access Key
    #This Needs to point at where your private key is on the file system
    keyfile = open('/Users/bitun.sen/Documents/AbbVie/Postman_Configuration/config/private.key','r')
    private_key = keyfile.read()
    # Encode the jwt Token
    jwttoken = jwt.encode(jwtPayloadJson, private_key, algorithm='RS256')
    #print("Encoded JWT Token")
    #print(jwttoken.decode('utf-8'))


    # We are making a http request simmilar to this curl request
    accessTokenRequestPayload['jwt_token'] = jwttoken
    result = requests.post(url, data = accessTokenRequestPayload)
    print(result)
    resultjson = json.loads(result.text);
    #print("Full output from the access token request")
    #print(json.dumps(resultjson, indent=4, sort_keys=True))

    # Echo out the access token
    print(resultjson["access_token"]);

    return resultjson["access_token"]

