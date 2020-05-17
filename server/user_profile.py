'''
User Profile Functions
'''
import urllib.request
from PIL import Image
import server_data
from server.helper import is_valid_name, token_to_user
from server.helper import is_email, is_valid_url, check_valid_user, validate_token

@validate_token
def users_all(token):
    '''
    (GET) Users all function
    Returns a dictionary containing the list of all users in slackr
    '''

    user_list = []
    # The following is the return type
    # Dictionary containing u_id, email, name_first, name_last, handle_str, profile_img_url

    for user in server_data.data['users']:
        user_list.append({
            'u_id' : user['u_id'],
            'email' : user['email'],
            'name_first' : user['name_first'],
            'name_last' : user['name_last'],
            'handle_str' : user['handle_str'],
            'profile_img_url' : user['profile_img_url']
        })

    return {'users': user_list}


# ============================= USER PROFILES ========================== #

#               This file contains all user profile functions

# ======================================================================== #


@validate_token
def user_profile(token, u_id):
    '''
    For a valid user, returns information about their email, first name, last name, and handle
    '''
    # Check if u_id refers to a valid user
    if server_data.data['n_users'] > u_id:
        return {
            'u_id': server_data.data['users'][u_id]['u_id'],
            'email' : server_data.data['users'][u_id]['email'],
            'name_first' : server_data.data['users'][u_id]['name_first'],
            'name_last' : server_data.data['users'][u_id]['name_last'],
            'handle_str' : server_data.data['users'][u_id]['handle_str'],
            'profile_img_url': server_data.data['users'][u_id]['handle_str']
        }
    raise ValueError("Invalid User ID")

@validate_token
def user_profile_setname(token, name_first, name_last):
    '''
    Update the authorised user's first and last name
    '''
    is_valid_name(name_first)
    is_valid_name(name_last)
    current_user_id = (token_to_user(token))
    server_data.data['users'][current_user_id]['name_first'] = name_first
    server_data.data['users'][current_user_id]['name_last'] = name_last
    return {}

@validate_token
def user_profile_setemail(token, email):
    '''
    Update the authorised user's email address
    '''
    current_user_id = token_to_user(token)

    # Check if valid email
    is_email(email)

    # Check if email is being used by another user
    for user in server_data.data['users']:
        if user['email'] == email:
            raise ValueError("Email address is already being used by another user")
    # Update email
    server_data.data['users'][current_user_id]['email'] = email
    return {}

@validate_token
def user_profile_sethandle(token, handle_str):
    '''
    Update the authorised user's handle (i.e. display name)
    '''
    current_user_id = token_to_user(token)
    # Check if handle is withint character limit
    if len(handle_str) > 20:
        raise ValueError("Handle exceeds 20 characters")
    if len(handle_str) < 3:
        raise ValueError("Handle must contain at least 3 characters")

    # Update handle
    server_data.data['users'][current_user_id]['handle_str'] = handle_str
    return {}

@validate_token
def user_profiles_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Given a URL of an image on the internet, crops the image within bounds
    (x_start, y_start) and (x_end, y_end).
    Position (0,0) is the top left.
    '''

    curr_user_id = token_to_user(token)
    check_valid_user(curr_user_id)

    # checks if img_url is valid
    is_valid_url(img_url)

    # retrieving the url
    filepath = './static/' + token + '.jpg'
    urllib.request.urlretrieve(img_url, filepath)

    # opening the file for cropping
    Image.open(filepath).convert('RGB').save(filepath)
    img = Image.open(filepath)

    # crop length must be withing dimensions of the image
    width, height = img.size

    if (x_start < 0 or y_start < 0 or x_end > width or y_end > height):
        raise ValueError(
            "x_start, y_start, x_end and y_end must be within the dimensions of the image"
        )

    if (x_start > x_end or y_start > y_end):
        raise ValueError("x_start and y_start must be smaller than x_end and y_end respectively")

    # cropping image
    cropped = img.crop((x_start, y_start, x_end, y_end))
    cropped.save(filepath)

    return {}
