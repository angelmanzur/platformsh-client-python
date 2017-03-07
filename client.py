import requests
import os
import json

ACCOUNTS_URL = 'https://accounts.platform.sh'
EU_PLATFORM_URL = 'https://eu.platform.sh'
US_PLATFORM_URL = 'https://us.platform.sh'
TOKEN_URL = '/oauth2/token'
SUBSCRIPTIONS_URL = '/api/platform/subscriptions'
ENVIRONMENTS_URL = '/api/projects'

class UserError(BaseException):
    pass

if not os.environ.get('PLATFORMSH_API_TOKEN'):
    raise UserError('Set the $PLATFORMSH_API_TOKEN environment variable')

def get_session_token(api_token=os.environ.get('PLATFORMSH_API_TOKEN')):
    '''
    Takes an api token and returns a session token if successful.
    Also caches the session token environment variable.
    Otherwise raises an error.
    '''
    headers = {
        # cGxhdGZvcm0tY2xpOg== is "platform-cli" in base64
        "Authorization": "Basic cGxhdGZvcm0tY2xpOg==",
        "Content-Type":"application/json"
    }
    data = {
        "grant_type": "api_token",
        "api_token": api_token,
    }
    res = requests.post(
        ACCOUNTS_URL + TOKEN_URL,
        headers=headers,
        data=json.dumps(data),
    )
    token = res.json()['access_token']
    os.environ['PLATFORMSH_SESSION_TOKEN'] = token
    return token


def subscriptions(token=os.environ.get('PLATFORMSH_SESSION_TOKEN'),
                  method='get', data=None):
    '''
    Generic subscriptions endpoint.
    Takes a session token, and optional method and data.
    '''
    return accounts_request(SUBSCRIPTIONS_URL, token, method, data)


def environments(project, environment='',
                 token=os.environ.get('PLATFORMSH_SESSION_TOKEN'), method='get',
                 data=None):
    '''
    Generic environments endpoint.
    Takes a session token, project_id, and optional method and data.
    '''
    path = '/{project}/environments/{environment}'.format(
        project=project,
        environment=environment
    )
    res = platform_request(
        ENVIRONMENTS_URL + path,
        token,
        method,
        data,
    )
    return res

def accounts_request(endpoint, token, method='get', data=None):
    '''
    Request to the accounts endpoint.
    '''
    return base_request(ACCOUNTS_URL + endpoint, token, method, data)

def platform_request(endpoint, token, method='get', data=None, region=None):
    '''
    Request to the platformsh endpoints.
    '''
    if region is None:
        try:
            # try the US endpoint
            return base_request(
                US_PLATFORM_URL + endpoint,
                token,
                method,
                data
            )
        except:
            # try the EU endpoint
            return base_request(
                EU_PLATFORM_URL + endpoint,
                token,
                method,
                data
            )
    else:
        raise NotImplementedError

def base_request(url, token, method='get', data=None):
    '''
    Attempts to revalidate the session token if it fails.
    '''
    try:
        return _base_request(url, token, method, data)
    except:
        token = get_session_token(os.environ.get('PLATFORMSH_API_TOKEN'))
        return _base_request(url, token, method, data)

def _base_request(url, token, method, data):
    '''
    Generic authorized request.
    '''
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type":"application/json"
    }
    if data:
        res = requests.request(
            method,
            url,
            headers=headers,
            data=data
        )
    else:
        res = requests.request(
            method,
            url,
            headers=headers,
        )
    return res.json()


if __name__ == "__main__":
    import sys
    print(environments('PROJECT_ID', 'ENVIRONMENT'))