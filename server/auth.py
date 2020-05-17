''' Auth Functions '''
import hashlib
import subprocess
import server_data
from server.helper import is_email, is_password, is_valid_name, generate_token
from server.helper import is_slackr_admin, generate_reset_token, AccessError, token_to_user
from server.helper import check_valid_user, validate_token

# ============================ AUTHORISATION ================================ #

#               This file contains all authorisation functions

# =========================================================================== #

def auth_register(email, password, name_first, name_last):
    '''
    Allows users to log in
    Generates a token when supplied with an email and password
    '''
    is_email(email)
    is_password(password)
    is_valid_name(name_first)
    is_valid_name(name_last)

    for user in server_data.data['users']:
        if user['email'] == email:
            raise ValueError('Email Taken')

    # Set user_id depending on the number of users in the server
    u_id = server_data.data['n_users']

    # Generate token
    token = generate_token(u_id, password)

    # Hash encrypt password
    password = hash_pw(password)

    # Generate handle
    handle_str = name_first.lower() + name_last.lower()
    handle_str = handle_str[:20]

    og_handle_str = handle_str[:19]

    # Check if handle is taken
    handle_count = 0
    flag = 1
    while flag:
        flag = 0
        for user in server_data.data['users']:
            if handle_str == user['handle_str']:
                flag = 1
                break
        if flag == 1:
            # Increment number next to handle_str
            handle_count += 1
            handle_str = og_handle_str + str(handle_count)

    # determine admin permission
    # The first joined user is the owner of the slackr
    if server_data.data['n_users'] == 0:
        permission = 1
    else:
        permission = 3

    server_data.data["users"].append({
        'token' : token,
        'email' : email,
        'password': password,
        'name_first' : name_first,
        'name_last': name_last,
        'handle_str': handle_str,
        'u_id' : u_id,
        'channels' : [],
        'permission' : permission,
        'reset_token' : None,
        'profile_img_url' : ""
    })

    server_data.data['n_users'] += 1
    return ({'u_id': u_id, 'token': token})


def auth_login(email, password):
    '''
    Given a valid email and password, the user is returned an authorised token
    '''
    is_email(email) # Checks if the email is a valid email

    # only return token if it exists and password matches
    for user in server_data.data['users']:
        if user['email'] == email:
            if hashlib.sha256(password.encode()).hexdigest() == user['password']:
                u_id = user['u_id']
                token = generate_token(u_id, password)
                # Set the user's token
                server_data.data['users'][int(u_id)]['token'] = token
                return ({'u_id': u_id, 'token': token})
            raise ValueError('Password incorrect')

    # Otherwise, raise a ValueError
    raise ValueError('Email does not exist')

def auth_logout(token):
    '''
    Logs users out by setting their token to None
    '''
    for user in server_data.data['users']:
        if str(user['token']) == str(token):
            user['token'] = None
            return {'is_success': True}

    # Otherwise return false
    return {'is_success': False}

def auth_passwordreset_request(email):
    '''
    This functions is for requesting a password reset
    '''
    is_email(email)

    for user in server_data.data["users"]:
        if user['email'] == str(email):
            # setting reset code
            #print("Email found")
            reset = generate_reset_token(user['u_id'], user['password'])
            user['reset_token'] = reset
            msg = '"Your reset code is ' + str(reset)  + '"'
            cmd = 'echo ' + msg + ' | mailx ' + str(email) + ' -s ' + '"Password Reset"'
            subprocess.call(cmd, shell=True)
            return {}

    raise ValueError('Email does not exist')


def auth_passwordreset_reset(reset_code, new_password):
    '''
    This function is for actually resetting a password
    '''
    is_password(new_password)

    new_password = hash_pw(new_password)

    for user in server_data.data["users"]:
        if str(user['reset_token']) == str(reset_code):
            user['password'] = new_password
            user['reset_token'] = None
            return {}
    raise ValueError("Reset code is not valid")



# Given a User by their user ID, set their permissions to new permissions
# described by permission_id
# Owner permission = 1
# Admin permission = 2
# Member permission_id = 3

@validate_token
def admin_userpermission_change(token, u_id, permission_id):
    '''
    This is the function file for admin_userpermission_change
    '''
    # Checks
    curr_user_id = token_to_user(token)
    check_valid_user(curr_user_id)
    check_valid_user(u_id)

    # Ensure that the permission_id is valid
    if permission_id not in [1, 2, 3]:
        raise ValueError('The permission_id is invalid')

    # This block details permissions

    # The owner can do anything:
    if server_data.data['users'][curr_user_id]['permission'] == 1:
        pass
    # cannot target the owner
    elif server_data.data['users'][u_id]['permission'] == 1:
        raise AccessError('Cannot change the owners permission')
    # must be an admin or owner
    elif not is_slackr_admin(curr_user_id):
        raise AccessError('User does not have the correct permissions')
    # target user alreay has the permission_id
    elif server_data.data['users'][u_id]['permission'] == permission_id:
        raise ValueError('The target user already has that permission')
    else:
        pass

    # set the permission
    server_data.data['users'][u_id]['permission'] = permission_id

    return {}

def hash_pw(password):
    '''
    Simple hashing function for the password
    '''
    password = hashlib.sha256(password.encode()).hexdigest()
    return password
