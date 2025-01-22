import requests
import traceback


def get_secret(dc_kv_ref):
    try:
        token = get_token()
        token_val = token.get("token")
        url = f"https://delivery-connector-mana.internal.ericsson.com/bots_ms/api/get_secret/{dc_kv_ref}"
        payload = {}
        headers = {
            'access-token': token_val
        }
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        res_json = response.json()
        return res_json
    except Exception as ex:
        print(f"Exception at get_secret {str(ex)}")
        traceback.print_exc()


def get_token():
    try:
        url = "https://delivery-connector-mana.internal.ericsson.com/user_ms/api/auth/token"
        payload = {}
        headers = {
            'Authorization': 'Basic aXNmbG9jYWx1c2VyOmZ6dHMkaWE3MEo='
        }
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        return response.json()
    except Exception as ex:
        print(f"Exception at get_token {str(ex)}")
        traceback.print_exc()