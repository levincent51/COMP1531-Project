import pytest
import requests
import src.other, src.auth
from src.dm import dm_create_v1
from src.config import url
from src.other import SECRET
import jwt

AuID    = 'auth_user_id'
uID     = 'u_id'
cID     = 'channel_id'
allMems = 'all_members'
Name    = 'name'
dmName  = 'dm_name'
fName   = 'name_first'
lName   = 'name_last'
chans   = 'channels'
token   = 'token'
dmID    = 'dm_id'
handle  = 'handle_str'

#* Fixture that clears and registers the first user
@pytest.fixture
def user1():
    requests.delete(f"{url}clear/v1")    
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "first@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "1"
    })
    return response.json()

#* Fixture that registers a second user
@pytest.fixture
def user2():
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "second@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "2"}
    )
    return response.json()

#* Fixture that registers a third user
@pytest.fixture
def user3():
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "third@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "3"}
    )
    return response.json()

#* Fixture that returns a JWT with invalid u_id and session_id
@pytest.fixture
def invalid_token():
    return jwt.encode({'session_id': -1, 'user_id': -1}, SECRET, algorithm='HS256')

#* Fixture that returns an invalid dm_id 
@pytest.fixture 
def invalid_dmID():
    return -1
    
@pytest.fixture
def invalid_u_id():
    return -1 

def test_http_dm_details_valid(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()
    expected = {
        Name: 'user1, user2',
        'members': [{
            uID: user1[AuID], 
            fName: "User",
            lName: '1',
            'email': 'first@gmail.com',
            handle: 'user1',
        }, {
            uID: user2[AuID], 
            fName: "User",
            lName: '2',
            'email': 'second@gmail.com',
            handle: 'user2',
        }
        ]
    }
    responseUser1 = requests.get(f"{url}dm/details/v1", params = {'token': user1[token], 'dm_id': dm1[dmID]})
    responseUser2 = requests.get(f"{url}dm/details/v1", params = {'token': user2[token], 'dm_id': dm1[dmID]})

    assert responseUser1.json() == expected
    assert responseUser2.json() == expected

def test_http_dm_details_invalid_dm_id(user1):
    invalid_dmID = -2
    response = requests.get(f"{url}dm/details/v1", params = {'token': user1[token], 'dm_id': invalid_dmID})
    assert response.status_code == 400

def test_http_dm_details_not_in_dm(user1, user2, user3):
    responseDM = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = responseDM.json()
    response = requests.get(f"{url}dm/details/v1", params = {'token': user3[token], 'dm_id': dm1[dmID]})
    
    assert response.status_code == 403

def test_http_dm_list_none(user1):
    response = requests.get(f"{url}dm/list/v1", params = {'token': user1[token]})
    assert response.json() == {'dms': []}

def test_http_dm_list(user1, user2, user3):
    requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user3[AuID]]
    })

    dm2 = dmResponse.json()
    response = requests.get(f"{url}dm/list/v1", params = {'token': user3[token]})
    assert response.json() == {'dms': [{
        dmID: dm2[dmID],
        Name: 'user1, user3'
    }]}

def test_http_dm_create(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })

    assert dmResponse.json() == {
        dmID: 0,
        'dm_name': 'user1, user2',
    }

def test_http_dm_create_invalid_u_ids(user1):
    invalid_u_id = -1
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [invalid_u_id]
    })

    assert dmResponse.status_code == 400


def test_http_dm_remove_invalid_DM(user1):
    invalid_dm_id = -1
    dmResponse = requests.delete(f"{url}dm/remove/v1", json={
        "token": user1[token],
        dmID: invalid_dm_id
    })
    assert dmResponse.status_code == 400

def test_http_dm_remove_fail(user1, user2, invalid_dmID):

    #Create dm with dm_id 0 
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    
    #access error when user2 tries to delete it
    dm_0 = response.json()
    access_error = requests.delete(f"{url}dm/remove/v1", json={
        "token": user2[token],
        dmID: dm_0[dmID],
    })
    
    assert access_error.status_code == 403


def test_http_dm_remove_success(user1, user2):
    #Create dm with dm_id 0 
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm_0 = response.json()
    
    #Now can test success case, i.e. that dm is removed 
    requests.delete(f"{url}dm/remove/v1", json={
        "token": user1[token],
        dmID: dm_0[dmID],
    })
    
    responseUser1 = requests.get(f"{url}dm/list/v1", params = {'token': user1[token]})
    
    expected = {'dms': []}
    assert responseUser1.json() == expected


def test_http_dm_invite_invalid_dm(user1, user2):
    invalid_dm_id = -1 
    invalid_dm = requests.post(f"{url}dm/invite/v1", json={
        "token": user1[token],
        dmID: invalid_dm_id,
        uID: [user2[AuID]],
    })
    assert invalid_dm.status_code == 400

def test_http_dm_invite_fail(user1, user2, user3, invalid_dmID, invalid_u_id):

    #Create dm with dm_id 0 containing user1 and user2 
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    
    dm_0 = response.json()

    invalid_u_id = -1
    invalid_result = requests.post(f"{url}dm/invite/v1", json={
        "token": user1[token],
        dmID: dm_0[dmID],
        uID: invalid_u_id,
    })
    
    assert invalid_result.status_code == 400

def test_http_dm_invite_access_error(user1, user2, user3):
    #Create dm with dm_id 0 containing user1 and user2 
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm_0 = response.json()
    
    access_error = requests.post(f"{url}dm/invite/v1", json={
        "token": user3[token],
        dmID: dm_0[dmID],
        uID: user2[AuID],
    })
    assert access_error.status_code == 403
    

def test_http_dm_invite_success(user1, user2, user3):
    #Create dm with dm_id 0 containing user1 and user2 
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm_0 = response.json()
    #Check success case: user3 is invited to dm_0
    requests.post(f"{url}dm/invite/v1", json={
        "token": user1[token],
        dmID: dm_0[dmID],
        uID: user3[AuID],
    })
    
    responseUser3 = requests.get(f"{url}dm/list/v1", params = {'token': user3[token]})
    expected = {'dms': [{
        dmID: dm_0[dmID],
        Name: 'user1, user2'
    }]}
  
    assert responseUser3.json() == expected
    



def test_http_dm_leave(user1, user2, user3):
    #Create dm with dm_id 0 
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    
    dm_0 = response.json()
    
    #Test for input error, when dm input is invalid
    invalid_dm_id = -1
    invalid_dm = requests.post(f"{url}dm/leave/v1", json={
        "token": user1[token],
        dmID: invalid_dm_id,
    })
    
    assert invalid_dm.status_code == 400

    #Test for access error, when user requesting leave is not in dm
    access_error = requests.post(f"{url}dm/leave/v1", json={
        "token": user3[token],
        dmID: dm_0[dmID],
    })
    assert access_error.status_code == 403
    
    #Now can test success case, where user 2 is removed from dm_0
    requests.post(f"{url}dm/leave/v1", json={
        "token": user2[token],
        dmID: dm_0[dmID],
    })
    
    responseUser2 = requests.get(f"{url}dm/list/v1", params = {'token': user2[token]})
    
    expected = {'dms': []}
    assert responseUser2.json() == expected
    
def test_http_dm_messages_invalid_dm(user1, user2):
    #Test for input error, when dm input is invalid
    invalid_dm_id = -1
    invalid_dm = requests.get(f"{url}dm/messages/v1", params = {
        "token": user1[token],
        dmID: invalid_dm_id,
        'start' : 0,
    })
    assert invalid_dm.status_code == 400
    

def test_http_dm_messages_invalid_start(user1, user2):
    #Test for input error, when 'start' is greater than # of messages in DM 
    #Create dm with dm_id 0 
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]],
    })
    
    dm_0 = response.json()
    
    invalid_start = requests.get(f"{url}dm/messages/v1", params = {
        "token": user1[token],
        dmID: dm_0[dmID],
        'start' : 1,
    })
    assert invalid_start.status_code == 400

def test_http_dm_messages_access_error(user1, user2, user3): 
    #Test for access error, when Authorised user is not a member of DM with dm_id
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]],
    })
    dm_0 = response.json()
    access_error = requests.get(f"{url}dm/messages/v1", params = {
        "token": user3[token],
        dmID: dm_0[dmID],
        'start' : 0,
    })
    assert access_error.status_code == 403 


def test_http_dm_messages(user1, user2, user3):
    #Create dm with dm_id 0 
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]],
    })
    
    dm_0 = response.json()
    requests.post(f"{url}message/senddm/v1", json={
        "token": user1[token],
        dmID: dm_0[dmID],
        "message" : "First message :)",
    })
        
    #Success case 1: Less than 50 messages returns end as -1 
    result = requests.get(f"{url}dm/messages/v1", params = {
        "token": user1[token],
        dmID: dm_0[dmID],
        'start': 0
    })
    responseUser1 = result.json()
    
    expected = {
        "len_messages": 1,
        'start': 0,
        "end": -1,
    }
    
    assert len(responseUser1['messages']) == expected['len_messages']
    assert responseUser1['start'] == expected['start']
    assert responseUser1['end'] == expected['end']
    

    #Success case 2: More than 50 messages returns end as 'start' + 50     
    #Send 50 messages into dm_0 
    message_counter = 1
    while message_counter < 51:
        requests.post(f"{url}message/senddm/v1", json = {
            "token": user1[token],
            dmID: dm_0[dmID],
            "message" : f"{message_counter}",
        })
        message_counter += 1
        
    result2 = requests.get(f"{url}dm/messages/v1", params = {
        'token': user2[token],
        dmID: dm_0[dmID],
        'start': 1
    })
    
    response_2 = result2.json()

    expected_2 = {
        'len_messages': 50,
        'start' : 1,
        'end': 51,
    }
    
    assert len(response_2['messages']) == expected_2['len_messages']
    assert response_2['start'] == expected_2['start']
    assert response_2['end'] == expected_2['end']
   
    
    

def test_http_dm_invalid_user(invalid_token):
    pass