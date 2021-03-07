import src.data
from src.error import AccessError, InputError

AuID    = 'auth_user_id'
uID     = 'user_id'
cID     = 'channel_id'
allMems = 'all_members'
cName   = 'channel_name'
fName   = 'name_first'
lName   = 'name_last'
chans   = 'channels'

def channels_list_v1(auth_user_id):
    """
    Provides a list of all channels (and their associated details) that the authorised user is part of

    Arguments:
        auth_user_id (int): The user_id of the user calling the function

    Exceptions:
        AccessError - Occurs when the auth_user_id passed in is not a valid id

    Return Value:
        Returns dictionary of a list of channels mapped to the key string 'channels'
        Each channel is represented by a dictionary containing types { channel_id, name }
    """
    # First, check if auth_user-id is a valid user_id
    check_auth_user_id(auth_user_id)

    output = []
    # Find channels that user is part of and add them to the output list
    for chanD in src.data.channels:
        for memberD in chanD['all_members']:
            if auth_user_id is memberD['user_id']:
                channel = {}
                channel[cID] = chanD[cID]
                channel[cName] = chanD[cName]
                if channel[cID] != None and channel[cName] != None:
                    output.append(channel)

    return {
        'channels': output
    }

def channels_listall_v1(auth_user_id):
    """
    Provides a list of all channels (and their associated details)
    Channels are provided irrespective of whether the member is part of the channel
    Both public and private channels are provided

    Arguments:
        auth_user_id (int): The user_id of the user calling the function

    Exceptions:
        AccessError - Occurs when the auth_user_id passed in is not a valid id

    Return Value:
        Returns dictionary of a list of channels mapped to the key string 'channels'
        Each channel is represented by a dictionary containing types { channel_id, name }
    """
    
    check_auth_user_id(auth_user_id)

    output = []
    for d in src.data.channels:
        channel = {}
        channel[cID] = d[cID]
        channel[cName] = d[cName]
        if channel[cID] != None and channel[cName] != None:
            output.append(channel)
    return {
        'channels': output
    }

def channels_create_v1(auth_user_id, name, is_public):
    return {
        'channel_id': 1,
    }

# Function that checks if auth_user_id is valid
def check_auth_user_id(auth_user_id):
    """
    Function that checks if auth_user_id is valid
    An auth_user_id is valid if there exists a user with that user_id

    Arguments:
        auth_user_id (int): The user_id of the user calling the function


    Return Value:
        AccessError is raised when the function cannot find a user with a matching user_id
    """
    for d in src.data.users:
        try:
        if auth_user_id == d[uID]:
            return
        except Exception:
            pass
    raise AccessError
