import src.data
from src.error import InputError, AccessError

def channels_list_v1(auth_user_id):
    # First, check if auth_user-id is a valid user_id
    try:
        check_auth_user_id(auth_user_id)
    except AccessError:
        print("Access error, please try again")
    
    output = []
    # Find channels that user is part of and add them to the output list
    for dictionary in src.data.channels:
        if auth_user_id in dictionary['all_members']:
            output.append(dictionary)

    return {'channels': output}
def channels_listall_v1(auth_user_id):
    # First, check if auth_user_id is a valid user_id
    try:
        check_auth_user_id(auth_user_id)
    except AccessError:
        print("Access error, please try again")

    # If auth_user_id is valid, then it should print all channels in data
    return {src.data.channels}

def channels_create_v1(auth_user_id, name, is_public):
    return {
        'channel_id': 1,
    }

# Function that checks if auth_user_id is valid
def check_auth_user_id(auth_user_id):
    
    uID = 'user_id'
    for dictionary in src.data.users:
        if auth_user_id == dictionary[uID]:
            return
    raise AccessError

