# Test helper file for testing whether data types are valid or not
import pytest
import sys
from datetime import date, time, datetime, timezone
import requests
import sys
import time as t
sys.path.append('../')
import server_data
import jwt
# ========================= HELPER FUNCTIONS =============================#

# This is a helper function file which will be included in our test files

# This will define an AccessError for testing
class AccessError(Exception):
    pass

def reset_data():
    server_data.data = {
        "n_users"       : 0,
        "users"         : [],
        "n_channels"    : 0,
        "channels"      : [],
        "n_messages"    : 0    
    }
    server_data.messages_later = []
    server_data.standups = []

# this prints out the data for debugging purposes
def show():
    print(server_data.data)
    print(server_data.messages_later)
    print(server_data.standups)
    print('--------------')

'''
                            * * * TOKENS * * *
'''
# Function for encoding tokens

SECRET = "tempSecret"
RESET_SECRET = "getAnewPWboii"
     
def generate_token(u_id, password):
    global SECRET
    token = jwt.encode(
        {'u_id': u_id, 'password': password}, 
        SECRET,
        algorithm='HS256'
    )
    return token.decode('utf-8')

def generate_reset_token(u_id, password):
    global RESET_SECRET
    token = jwt.encode(
        {'u_id': u_id, 'password': password}, 
        RESET_SECRET,
        algorithm='HS256'
    )
    return token.decode('utf-8')

def validate_reset_token(token):
    global RESET_SECRET
    info = jwt.decode(token, RESET_SECRET, algorithms=['HS256'])
    check_valid_user(info['u_id'])
    return info['u_id']

# Function for decoding tokens

def decode_token(token):
    global SECRET
    info = jwt.decode(token, SECRET, algorithms=['HS256'])
    return info

# Function for obtaining user_id from token

def token_to_user(token):
    global SECRET
    u_id = decode_token(token)['u_id']
    return int(u_id)

# Function for obtaining first_name from token

def token_to_firstname(token):
    global SECRET
    u_id = decode_token(token)['u_id']
    data = server_data.data
    for x in data['users']:
        if x['u_id'] is u_id:
            return str(x['name_first'])
    

# Function for checking whether token is valid

def is_valid_token(token):
    for user in server_data.data['users']:
        if token == user['token']:
            if token != None:
                return 
    # Raise access error 
    raise AccessError("Invalid token")

# following is a decorator for validating a token
def validate_token(function):
    def wrapper(*args, **kwargs):
        is_valid_token(args[0])
        return function(*args, **kwargs)
    return wrapper

'''
                        * * * AUTHORISATION * * *
'''
# Test for valid password
def is_password(password):
    if isinstance(password, str) == False:
        raise TypeError (f"Password: {password} is not a string")
    elif len(password) < 5:
        raise ValueError(f"Password: {password} is less than 5 characters.")
    else:
        return 
        
# The following helper function tests if an email is valid

import re

def is_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email)):  
        return  
    else:  
        raise ValueError("Invalid Email")
                    

'''
                        * * * MESSAGES * * *
'''
                    
# Test for valid "messages" output (not the message data type)
def is_messages(dict_list):
    for dict in dict_list:
        if isinstance(dict['message_id'], int) == False:
            raise ValueError(f"Message_id: {dict['message_id']} is invalid")
            
        if isinstance(dict['u_id'], int) == False:
            raise ValueError(f"User_id: {dict['u_id']} is invalid") 
            
        if isinstance(dict['message'], str) == False:
            raise ValueError(f"Message: {dict['message']} is invalid")
        
        # Not sure how to validate datetime types
        # If someone can figure it out feel free to add     
        if isinstance(dict['time_created'], datetime) == False:
            raise TypeError(f"Time_created: {dict['time_created']} is invalid")
            
        if isinstance(dict['is_unread'], bool) == False:
            raise ValueError(f"Is_unread: {dict['is_unread']} is invalid")

# The following tests if a message is valid
def is_valid_message(message):
    if isinstance(message, str) == False:
        raise ValueError("Message is not a string")
    if len(message) > 1000:
        raise ValueError("Message is too long (> 1000)")

# Find a specific message in a list of dictionaries 
def find_message(dic, msg_str):
    for x in dic:
        if x['message'] is msg_str:
            return msg_str
    return None

# Search for a message and return its id          
def get_message_id(dic, msg_str):
    for x in dic:
        if x['message'] is msg_str:
            return x['message_id']
    return None            

# Search for a message ID and return its string         
# @@@ Changing this function to match changed utility 
# returns the message dictionary given a message ID
def get_msg_dict(message_id):
    # loop through the channels
    for channel in server_data.data["channels"]:
        for message in channel["messages"]:
            if int(message['message_id']) == int(message_id):
                return (message)
    return None

# Return the react id of a specific message     
def get_react_id(dic, message_id):
    for x in dic:
        if x['message_id'] is message_id:
            return x['react_id']
    return 0  

# Return the time a message was sent
def time_sent(dic, message_id):
    for x in dic:
        if x['message_id'] is message_id:
            return x['time_sent']
    return None

# checks if start is an integer and also equal to 0
def valid_start(start):
    if start != 0:
        return False
    if isinstance(start, int) == False:
        raise ValueError("Start is not an integer")
        
# given the message_id, return what channel it is in
def msg_to_channel(message_id):
    for channel in server_data.data["channels"]:
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                return channel
    return None

def is_msg_removed(message_id):
    message_dict = get_msg_dict(message_id)
    if (str(message_dict['message']) == "*** Message Deleted ***"):
        raise ValueError('Message does not exist')
    return False
            
'''
                        * * * CHANNELS * * *
'''
            
# Test for valid "channels" output
def is_channels(dict_list):
    for dict in dict_list:
        if isinstance(dict['id'], int) == False:
            raise ValueError(f":Id: {dict['id']} is invalid")
            
        if isinstance(dict['name'], str) == False:
            raise ValueError(f":Name: {dict['name']} is invalid")

def check_valid_channel(channel_id):
    if (channel_id > server_data.data['n_channels']) or (channel_id < 0):
        raise ValueError('Channel does not exist')

# Generate sample channels for test_channels.py

def generate_channels():
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    channel_id_public = channel_create(token, 'newChannel', True)
    channel_id_private = channel_create(token, 'privateChannel', False)
    pass
'''
                        * * * USERS * * *
'''

# Test for valid "members" output
def is_members(dict_list):
    for dict in dict_list:
        if isinstance(dict['u_id'], int) == False:
            raise ValueError(f":User_id: {dict['u_id']} is invalid")
            
        if isinstance(dict['name_first'], str) == False:
            raise ValueError(f":Name_first: {dict['name_first']} is invalid")
            
        if isinstance(dict['name_last'], str) == False:
            raise ValueError(f":Name_last: {dict['name_last']} is invalid")

# The following tests if a user is valid
def is_valid_name(name):
    if len(name) > 20:
        raise ValueError("Name is too long (> 20 characters)")    
        
        
'''
    The following function checks if a user is part of a channel
'''
def check_channel_member(curr_user_id, channel_id):
    # Check if the user is part of the channel
    for channels in server_data.data['users'][curr_user_id]['channels']:
        if (int(channels) == int(channel_id)):
            return True
    return False
     
'''
    The following function checks if a user valid
'''
def check_valid_user(curr_user_id):
    if (curr_user_id > server_data.data['n_users']) or (curr_user_id < 0):
        raise ValueError("User does not exist")


# checks if start is an integer and also equal to 0
def valid_start(start):
    if start != 0:
        return False
    if isinstance(start, int) == False:
        raise ValueError("Start is not an integer")


# checks if a image url is valid
# input url must be a string, i.e 'www.google.com' will work whereas www.google.com will fail, must be string
def is_valid_url(url):
    request = requests.get(url)
    if request.status_code == 200:
        pass
    else:
        raise ValueError("Invalid Url")        

# checks if channel_id is valid
def channel_id_exists(ch_id):
    if ch_id > server_data.data["n_channels"] or ch_id < 0:
        return False
    else:
        return True
'''
Checks if a specific channel exists using a channel_id
Returns 'True' if it exists, 'False' if it doesn't
'''       
def channel_exists(channel_id):
    for x in server_data.data["channels"]:
        if int(x["channel_id"]) is int(channel_id):
            return True
    return False
    
'''
Return a list of members in a specified channel
''' 
def members_list(channel_id):
    for x in server_data.data["channels"]:
        if int(x["channel_id"]) is int(channel_id):
            index = server_data.data["channels"].index(x)
            members = (server_data.data["channels"][index]['members'])
            return members
            
'''
Using a given channel_id
Returns the dictionary with all the channel info
''' 
def channel_info(channel_id):
    for x in server_data.data["channels"]:
        if int(x["channel_id"]) is int(channel_id):
            index = server_data.data["channels"].index(x)
            info = (server_data.data["channels"][index])
            return info
        
'''
Check if a user is an owner of a specified channel
Returns 'True' if they are, 'False' if they aren't
'''
def is_owner(u_id, channel_id):
    members = members_list(channel_id)
    for y in members:
        if y['u_id'] == u_id and y['channel_permission'] == 1:
            return True                
    return False
    
'''
Get user information using a u_id
Returns their dictionary in data['users']
'''
def get_userinfo(u_id):
    for x in server_data.data["users"]:
        if x['u_id'] == u_id:
            index = server_data.data["users"].index(x)
            return (server_data.data["users"][index])

'''
Check if a user has admin privileges 
Returns 'True' if they are, 'False' if not
'''
def is_slackr_admin(u_id):
    info = get_userinfo(u_id)
    admins = [1, 2]
    if info['permission'] in admins:
        return True
    else:
        return False


'''
Check if a standup is running in a specified channel
'''
def standup_exists(channel_id):
    standups = server_data.standups
    for x in standups:
        if int(x["channel_id"]) is int(channel_id):
            return True
    return False


'''
Return an active standup of a specified channel
'''
def get_standup(standups, channel_id):      
    for x in standups:
        if int(x["channel_id"]) is int(channel_id):
            index = standups.index(x)
            return (standups[index])
    return None     
    
'''
Check if there are any messages to be sent which have been stored for later
'''
def check_latermessages():
    messages_later = server_data.messages_later
    time = int(t.time())
    for x in messages_later:
        if x['time_created'] == time:
            channel_id = x['channel_id']
            index = messages_later.index(x)
            info = channel_info(channel_id) 
            messages = info['messages']
            info['channel_n_messages'] += 1
            messages.append(dict(messages_later[index]))            
    
    
'''
Check if any standups are finished
'''
def check_standups():
    standups = server_data.standups
    if len(standups) == 0:
        return
    time = int(t.time())
    for x in standups:
        if x['time_end'] == time:
            print('finished standup for channel_id', x['channel_id'])
            standup_messages = x['messages']
            channel_id = x['channel_id']
            creator_id = x['u_id']
            info = channel_info(channel_id) 
            messages = info['messages']
            info['channel_n_messages'] += 1
            all_messages = ''
            for y in standup_messages:
                all_messages += y['first_name'] + ': ' + y['message'] + '\n'
            
            message_id = server_data.data['n_messages'] 
            server_data.data['n_messages'] += 1
            
            newMessage = dict()
            newMessage['message_id'] = message_id
            newMessage['u_id'] = creator_id
            newMessage['message'] = all_messages
            newMessage['time_created'] = time
            newMessage['reacts'] = []
            newMessage['is_pinned'] = False  
            messages.append(dict(newMessage))               
            standups.remove(x)         



def time_to_epoch(given_time):
    timestamp = given_time.replace(tzinfo=timezone.utc).timestamp()
    timestamp = str(timestamp)
    return timestamp
    
'''
Get channel messages
'''
def get_messages(channel_id):
    info = channel_info(channel_id)
    messages = info['messages']
    return messages
    
'''
Check if a message is stored to be sent later
'''
def check_later(message_id):
    messages = server_data.messages_later
    for x in messages:
        if x['message_id'] is message_id:
            return message_id
    return None
    
'''
Get the messages from an active standup
'''
def standup_messages(channel_id):
    standups = server_data.standups
    for x in standups:
        if x['channel_id'] is channel_id:
            index = standups.index(x)
            return (standups[index]['messages'])   

'''
Search for a specific message in an active standup
'''
def find_standup_msg(messages, target):
    for x in messages:
        if x['message'] is target:
            return x['message']
    return None
             
