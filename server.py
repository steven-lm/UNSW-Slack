"""Flask server"""
import sys
from flask_cors import CORS
from json import dumps
import json
from flask import Flask, request, send_from_directory
import time as t
from timeloop import Timeloop
from datetime import date, time, datetime
import threading
import server_data
import os
import pickle
import sys
sys.path.append('server/')
from server.helper import *
from server.channels import *
from server.auth import auth_register, auth_login, auth_logout, auth_passwordreset_request, auth_passwordreset_reset, admin_userpermission_change
from server.user_profile import user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle, user_profiles_uploadphoto, users_all
from server.messages import message_send, message_pin, message_unpin, message_react, message_unreact, message_remove, message_edit, search, message_sendlater, standup_start, standup_send, standup_active
APP = Flask(__name__, static_url_path='/static/')

CORS(APP)

# ========================== ECHO FUNCTIONS ======================== #

# Echo functions (in the spec so I'm leaving them in)

@APP.route('/echo/get', methods=['GET'])
def echo():
    """ Echos Function """
    return dumps({
        'echo' : request.args.get('echo'),
    })

@APP.route('/echo/post', methods=['POST'])
def echo2():
    """ Echos Function """
    return dumps({
        'echo' : request.args.get('echo'),
    })

# The following function is for typecasting a token so that it can be used inside form
def type_cast(token):
        for user in server_data.data['users']:
            if str(user["token"]) == token:
                return user["token"]
        return None

# ========================== PERSISTENCE ========================== #

if os.path.exists('dataStore.json'):
    server_data.data = json.load(open('dataStore.json','r'))
    
if os.path.exists('standups.json'):
    server_data.standups = json.load(open('standups.json','r'))

if os.path.exists('messagesLater.json'):
    server_data.messages_later = json.load(open('messagesLater.json','r'))

def save():
    check_latermessages()
    check_standups()
    print('Saving!', t.strftime('%Y-%m-%d %H:%M:%S', t.localtime(int(t.time()))))
    with open('dataStore.json','w') as FILE:
        json.dump(server_data.data, FILE, indent = 4, sort_keys=False)
    with open('standups.json','w') as FILE:
        json.dump(server_data.standups, FILE, indent = 4, sort_keys=False)
    with open('messagesLater.json','w') as FILE:
        json.dump(server_data.messages_later, FILE, indent = 4, sort_keys=False)

def timerAction():
    timer = threading.Timer(1.0,timerAction)
    timer.start()
    save()
timerAction()

# ========================== DEV FUNCTIONS ======================== #
@APP.route('/data/reset', methods=['POST'])
def data_resett():
    """ Dev showing all data """
    server_data.data = {
        "n_users"       : 0,
        "users"         : [],
        "n_channels"    : 0,
        "channels"      : [],
        "n_messages"    : 0    
    }
    server_data.messages_later = []
    server_data.standups = []
    return dumps({
        'data': server_data.data
    })
    
@APP.route('/data/getall', methods=['GET'])
def get_all():
    """ Dev showing all data """
    return dumps({
        'data': server_data.data
    })
    
@APP.route('/data/later', methods=['GET'])
def get_later():
    """ Dev showing messages to be sent later"""
    return dumps({
        'later': server_data.messages_later
    })
    
@APP.route('/data/standups', methods=['GET'])
def get_standups():
    """ Dev showing all standups"""
    return dumps({
        'standups': server_data.standups
    })
    
@APP.route('/data/getlater', methods=['GET'])
def get_messages_later():
    """ Dev showing all data """
    return dumps(
        server_data.messages_later
    )
    
@APP.route('/data/add', methods=['POST'])
def add():
    """ Dev adding a user """
    name = request.args.get('name')
    last = request.args.get('last')
    server_data.data['users'].append(name)
    server_data.data['users'].append(last)
    server_data.data['n_users'] += 1
    return dumps({
    })

@APP.route('/data/delete', methods=['DELETE'])
def create():
    """ Dev removing a user """
    name = request.args.get('name')
    print(name)
    for x in server_data.data['users']:
        if x == name:
            server_data.data['users'].remove(name)
            server_data.data['n_users'] -= 1
    return dumps({
    })

# ========================== AUTH FUNCTIONS ======================== #

@APP.route('/auth/register', methods=['POST'])
def post_auth_register():
    """ Register a new user adding a user """
    email = request.form.get('email')
    password = request.form.get('password')
    name_first = request.form.get('name_first')
    name_last = request.form.get('name_last')
    
    try:
        output = auth_register(str(email), str(password), str(name_first), str(name_last))     
    except ValueError as e:
        return str(e)
    save()
    return dumps({
        'u_id': output['u_id'], 
        'token': str(output['token'])
    })

@APP.route('/auth/login', methods=['POST'])
def post_auth_login():
    """ Login an existing user """
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        output = auth_login(email, password)
        save()
    except ValueError as e:
        return str(e)
    return dumps({
        'u_id': output['u_id'], 
        'token': str(output['token'])
    })

@APP.route('/auth/logout', methods=['POST'])
def post_auth_logout():
    """ Logout an existing user and invalidate their token """
    token = request.form.get('token')
    try:
        output = auth_logout(token)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps(
        output
    )
    
@APP.route('/auth/passwordreset/request', methods=['POST'])
def post_auth_request():
    """ Send an email to reset the password of a user """
    email = request.form.get('email')
    try:
        auth_passwordreset_request(email)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({})

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def post_auth_reset():
    """ Reset the password of a user """
    reset_code = request.form.get('reset_code')
    new_password = request.form.get('new_password')
    try:
        auth_passwordreset_reset(reset_code,new_password)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({})


@APP.route('/admin/userpermission/change', methods=['POST'])
def post_admin_change():
    """ Change the slackr permission of others """
    token = request.form.get('token')
    u_id = request.form.get('u_id')
    permission_id = request.form.get('permission_id')
    
    try:
        admin_userpermission_change(token,int(u_id), int(permission_id))     
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({
    })

# ========================== CHANNEL FUNCTIONS ======================== #

@APP.route('/channel/invite', methods=['POST'])
def post_channel_invite():
    """ Invites a target user to a channel """
    token = request.form.get('token')
    real_token = type_cast(token)
    channel_id = request.form.get('channel_id')
    u_id = request.form.get('u_id')
    save()
    try:
        output = channel_invite(real_token, int(channel_id), int(u_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps(
        output
    )

@APP.route('/channel/details', methods=['GET'])
def get_channel_details():
    """ Returns the details of a specified channel """
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    token = type_cast(token)
    save()
    try:
        output = channel_details(token, int(channel_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400
    return dumps(
        output
    )

@APP.route('/channels/create', methods = ['POST'])
def post_channel_create():
    '''creates a channel'''
    token = request.form.get('token')
    channel_name = request.form.get('name')
    is_public = request.form.get('is_public')
    save()
    try:
        output = channel_create(token,channel_name,is_public)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps({        
        "channel_id" : output
    }) 

@APP.route('/channels/list', methods=['GET'])
def get_channels_list():
    """ Lists a certain user's channels """
    token = request.args.get('token')
    real_token = type_cast(token)
    try:
        output = channels_list(real_token)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps({
        'channels' : output
    })

# This function lists all the channels
@APP.route('/channels/listall', methods=['GET'])
def channels_list_all():
    """ Lists all channels """
    token = request.args.get('token')
    try:
        output = channels_listall(token)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps({
        'channels' : output
    })


# Channel add owner    
@APP.route('/channel/addowner', methods=['POST'])
def add_owner():
    token = request.form.get('token')
    channel_id = request.form.get('channel_id')
    u_id = request.form.get('u_id')
    save()
    try:
        channel_addowner(type_cast(token), int(channel_id), int(u_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps({
    })
    
  
# Channel remove owner
@APP.route('/channel/removeowner', methods=['POST'])
def remove_owner():
    token = request.form.get('token')
    channel_id = request.form.get('channel_id')
    u_id = request.form.get('u_id')
    try:
        channel_removeowner(type_cast(token), int(channel_id), int(u_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({
    })
    

# Channel join    
@APP.route('/channel/join', methods=['POST'])
def join():
    token = request.form.get('token')
    channel_id = request.form.get('channel_id')    
    try:
        channel_join(type_cast(token), int(channel_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({
    })

# Channel leave    
@APP.route('/channel/leave', methods=['POST'])
def leave():
    token = request.form.get('token')
    channel_id = request.form.get('channel_id') 
    try:
        channel_leave(type_cast(token), int(channel_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({
    })

# Channel messages
@APP.route('/channel/messages', methods=['GET'])
def messages():
    '''returns messages'''
    token = request.args.get('token')
    channel_id = request.args.get('channel_id') 
    start = request.args.get('start')
    try:
        output = channel_messages(str(token),int(channel_id),int(start))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps(
        output
    )
# ========================= USERS ALL FUNCTION ========================#

@APP.route('/users/all', methods=['GET'])
def get_users_all():
    """Lists all users across slackr"""
    token = request.args.get('token')
    try:
        output = users_all(type_cast(token))
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps(
        output
    )


# ========================= USER PROFILE FUNCTIONS ==================== #

# This function lists all the user's profile details

@APP.route('/user/profile', methods=['GET'])
def user_profile_details():
    """List details"""
    token = request.args.get('token')
    u_id = request.args.get('u_id')    
    try:
        output = user_profile(str(token), int(u_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps(
        output
    )
    

# This function updates the authorised user's first and last name

@APP.route('/user/profile/setname', methods=['PUT'])
def put_user_profile_setname():
    """Updates first and last name"""
    token = request.form.get('token')
    name_first = request.form.get('name_first')
    name_last = request.form.get('name_last')   
    try:
        output = user_profile_setname(type_cast(token), str(name_first), str(name_last))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps(        
        output
    )

# This function updates the authorised user's email

@APP.route('/user/profile/setemail', methods=['PUT'])
def put_user_profile_setemail():
    """Updates email"""
    token = request.form.get('token')
    email = request.form.get('email')
    try:
        output = user_profile_setemail(type_cast(token), str(email))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps(        
        output
    )

# This function updates the authorised user's handle 
@APP.route('/user/profile/sethandle', methods=['PUT'])
def put_user_profile_sethandle():
    """Updates handle"""
    token = request.form.get('token')
    handle_str = request.form.get('handle_str')
    try:
        output = user_profile_sethandle(type_cast(token), str(handle_str))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps(        
        output
    )
    
    
# ========================== MESSAGE FUNCTIONS ======================== #
# Message send 
@APP.route('/message/send', methods=['POST'])
def send_message():
    token = request.form.get('token')
    channel_id = request.form.get('channel_id')
    message = request.form.get('message')
    try:
        output = message_send(type_cast(token), int(channel_id), message)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({
        'message_id': output
    })


# Message send later   
@APP.route('/message/sendlater', methods=['POST'])
def sendlater_message():
    token = request.form.get('token')
    channel_id = request.form.get('channel_id')
    message = request.form.get('message')
    time = request.form.get('time_sent')   
    try:
        output = message_sendlater(token, channel_id, message, time)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({
        'message_id' : output
    })

'''
    This deletes a message
'''
@APP.route('/message/remove', methods=['DELETE'])
def delete_message():
    """ Removes a specific message """
    token = request.form.get('token')
    message_id = request.form.get('message_id')
    try:
        output = message_remove(token, int(message_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400
    save()
    return dumps(
        output
    )


'''
    This edits a message
'''
@APP.route('/message/edit', methods=['PUT'])
def put_edit_message():
    """ Edits a specific message """
    token = request.form.get('token')
    message_id = request.form.get('message_id')
    message = request.form.get('message')
    try:
        output = message_edit(token, int(message_id), message)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps(
        output
    )

'''
    These requests pins a message 
''' 
@APP.route('/message/pin', methods=['POST'])
def post_message_pin():
    """ Pins a specific message """
    token = request.form.get('token')
    message_id = request.form.get('message_id')    
    try:
        message_pin(token, int(message_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({
    })

'''
    These requests unpin a messages
''' 
@APP.route('/message/unpin', methods=['POST'])
def post_message_unpin():
    """ Unpins a specific message """
    token = request.form.get('token')
    message_id = request.form.get('message_id')    
    try:
        message_unpin(token, int(message_id))
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    save()
    return dumps({
    })


'''
    These requests react to a message 
''' 
@APP.route('/message/react', methods=['POST'])
def post_message_react():
    """ Reacts to a specific message """
    token = request.form.get('token')
    message_id = request.form.get('message_id')
    react_id = request.form.get('react_id')
    message_react(token, int(message_id), int(react_id))
    save()
    return dumps({
    })

'''
    These requests unreacts to a message 
''' 
@APP.route('/message/unreact', methods=['POST'])
def post_message_unreact():
    """ Unreacts to a specific message """
    token = request.form.get('token')
    message_id = request.form.get('message_id')
    message_unreact(token, int(message_id), 1)
    save()
    return dumps({
    })
'''
    Search message
'''
@APP.route('/search', methods=['GET'])
def get_search():
    """ Searches for a particular message given a query string """
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    try:
        output = search(token, query_str)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps(
        output
    )
# ========================== STANDUP FUNCTIONS ======================== #
# Standup start
@APP.route('/standup/start', methods=['POST'])
def start_sendup():
    token = request.form.get('token')
    channel_id = request.form.get('channel_id')
    length = request.form.get('length')
    try:
        time_end = standup_start(token, channel_id, length)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps({
        'time_end' : time_end
    })

# Standup send
@APP.route('/standup/send', methods=['POST'])
def send_standup():
    token = request.form.get('token')
    channel_id = request.form.get('channel_id')
    message = request.form.get('message')
    try:
        standup_send(token, channel_id, message)
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps({
    })

# Standup active
@APP.route('/standup/active', methods=['GET'])
def active_standup():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    exists = False
    try:
        time_finish = standup_active(token, channel_id)
        if(time_finish is not None):
            exists = True       
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps({
        'is_active' : exists,
        'time_finish' : time_finish
    })
    
    
# user profiles uploading a picture
@APP.route('/user/profiles/uploadphoto', methods=['POST'])
def user_uploadphoto():
    token = request.form.get('token')
    img_url = request.form.get('img_url')
    x_start = request.form.get('x_start')
    y_start = request.form.get('y_start')
    x_end = request.form.get('x_end')
    y_end = request.form.get('y_end')
    try:
        output = user_profiles_uploadphoto(token ,str(img_url), int(x_start), int(y_start), int(x_end), int(y_end))
        curr_user_id = token_to_user(token)
        server_data.data['users'][curr_user_id]['profile_img_url'] = request.url_root + './static/' + token + '.jpg'
    except ValueError as e:
        return str(e)
    except AccessError as e:
        return dumps ({
            'code' : 400,
            'name' : 'AccessError',
            'message' : str(e)
        }), 400 
    return dumps (
        output
    )

@APP.route('/static/<path>:path')
def send_js(path):
    return send_from_directory('',path)

if __name__ == '__main__':
    save()  
    APP.run(port=(sys.argv[1] if len(sys.argv) > 1 else 5000))
