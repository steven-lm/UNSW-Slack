'''Channels'''
import sys
import server_data
from server.helper import is_valid_token, channel_exists, token_to_user, members_list
from server.helper import get_userinfo, check_valid_user, check_valid_channel, is_owner
from server.helper import is_slackr_admin, is_valid_name, check_channel_member, AccessError
from server.helper import valid_start, channel_id_exists
sys.path.append('../')



def channel_join(token, channel_id):
    '''
    Using a valid token, the user joins a channel specified by 'channel_id'

    Raises errors if:
    - Channel doesn't exist
    - User tries to join a private channel
    '''
    is_valid_token(token)
  # When channel Id is invalid
    if not channel_exists(int(channel_id)):
        raise ValueError('Channel does not exist')

  # When user tries to join a private channel ( AccessError)
    if not server_data.data['channels'][int(channel_id)]['is_public']:
        raise AccessError('Channel is invite only')

    user_id = token_to_user(token)

  # Add user to channel 'members' list (channel_permission 2)
    # create a new dictionary with u_id and default channel permission
    data = {
        'u_id': user_id,
        'channel_permission': 0,
    }

    # append this to the channel list
    members = members_list(channel_id)
    members.append(data)

  # Add channel to users 'channels' list
    # get user info
    user_info = get_userinfo(user_id)

    # add channel_id to 'channels' list
    user_info['channels'].append(channel_id)


def channel_leave(token, channel_id):
    '''
    Using a valid token, the user leaves a channel specified by 'channel_id'

    Raises errors if:
    - Channel doesn't exist
    '''
    is_valid_token(token)
  # When channel Id is invalid
    if not channel_exists(channel_id):
        raise ValueError('Channel does not exist')

  # Remove user from 'members' list in channel
    # get members list (from channel_id)
    members = members_list(channel_id)

    # remove user from members list
    user_id = token_to_user(token)
    for member in members:
        if member['u_id'] == user_id:
            members.remove(member)

  # Remove channel from users 'channels' list
    user_info = get_userinfo(user_id)
    user_info['channels'].remove(channel_id)


def channel_addowner(token, channel_id, u_id):
    '''
    Using a valid token, add a user specified by 'u_id' as an owner of a specific channel

    Raises errors if:
    - Channel doesn't exist
    - the user is already an owner of that channel
    - token's user doesn't have permission to assign owners
    '''
    is_valid_token(token)
    check_valid_user(u_id)

    token_id = token_to_user(token)

    check_valid_user(token_id)
    check_valid_channel(channel_id)

    if not check_channel_member(u_id, channel_id):
        raise ValueError('Target user is not in the channel')

  # When user is not an admin or owner, only owners can add other owners (AccessError)
    if not is_owner(token_id, channel_id) and not is_slackr_admin(token_id):
        raise AccessError('You do not have permission to assign an owner')

  # User is already an owner of that channel
    if is_owner(u_id, channel_id):
        raise ValueError('User is already an owner')

  # Change user permission to owner
    # get members list (from channel_id)
    members = members_list(channel_id)

    # change user permission to '1'
    for member in members:
        if member['u_id'] == u_id:
            member['channel_permission'] = 1


def channel_removeowner(token, channel_id, u_id):
    '''
    Using a valid token, remove a users permission as an owner in a specified channel

    Raises errors if:
    - Channel doesn't exist
    - the user is already an not an owner of that channel
    - token's user doesn't have permission to remove owners
    '''
    is_valid_token(token)
    check_valid_user(u_id)

    token_id = token_to_user(token)

    check_valid_user(token_id)
    check_valid_channel(channel_id)

    if not check_channel_member(u_id, channel_id):
        raise ValueError('Target user is not in the channel')

  # User is already not an owner of that channel
    if not is_owner(u_id, channel_id):
        raise ValueError('User is already not an owner')

    curr_user_id = token_to_user(token)

  # When user is not an admin or owner, only owners can remove other owners (AccessError)
    if not is_owner(curr_user_id, channel_id) and not is_slackr_admin(curr_user_id):
        raise AccessError('You do not have permission to remove this owner')

    if server_data.data['users'][u_id]['permission'] == 1:
        raise AccessError('Cannot change the permission of Slackr creator')

  # Remove user permission as owner
    # get members list (from channel_id)
    members = members_list(channel_id)

    # change user permission to '0'
    for member in members:
        if member['u_id'] == u_id:
            member['channel_permission'] = 0

# ============================ CHANNELS ====================================== #

#               This file contains all channel functions

# =========================================================================== #

# ------------------------- CHANNEL INVITE -------------------------#

#                 Implementation for channel_invite

#                 Adds a target user into a target channel.

# ----------------------------------------------------------------

def channel_invite(token, channel_id, u_id):
    '''
    The following function invites a given user into a given channel
    '''
    # may need to alter this so that only AUTHORISED members can invite others

    # Perform required checks
    check_valid_channel(channel_id)

    curr_user_id = token_to_user(token)

    check_valid_user(curr_user_id)
    check_valid_user(u_id)
    # Check the current user is actually a member of target channel
    if not check_channel_member(curr_user_id, channel_id):
        raise AccessError('User is not part of the target channel')

    # Check the target user is not already a member of target channel
    if check_channel_member(u_id, channel_id):
        raise ValueError('Target user is already a member of the target channel')

    # If it reaches here, all parameters are valid
    # target user becomes a member of the channel
    for channel in server_data.data['channels']:
        if channel['channel_id'] == channel_id:
            channel['members'].append({
                'u_id' : u_id,
                'channel_permission' : 0
            })
            break

    # channel is in the user's channel list
    for user in server_data.data['users']:
        if user['u_id'] == u_id:
            user['channels'].append(channel_id)
            break
    return {}

# -------------------------CHANNEL MESSAGES-------------------------

#                 Implementation for channel_messages

# ----------------------------------------------------------------


def channel_messages(token, channel_id, start):
    '''
    The following function shows up to 50 messages in a given channel
    '''
    # check token
    curr_user_id = token_to_user(token)

    # Check if the user exists
    check_valid_user(curr_user_id)
    check_valid_channel(channel_id)

    cha_data = server_data.data['channels'][channel_id]

    if not check_channel_member(curr_user_id, channel_id) and not cha_data['is_public']:
        raise AccessError('User is not in the target channel. Error code: 1')

    #tests for validity of token, channel_id and start

    # checks if start is valid else raise error
    valid_start(start)
    if start >= (server_data.data["channels"][channel_id]["channel_n_messages"]):
        raise ValueError("Start is greater than total number of messages")

    # checks if channel_id is valid else raise error
    channel_id_exists(channel_id)

    return_amount = 49
    messages = []
    actual_start = server_data.data["channels"][channel_id]["channel_n_messages"] - start - 1
    counter = actual_start

    if actual_start > return_amount:
        last = actual_start - return_amount
        for counter in range(actual_start, last, -1):
            messages.append(server_data.data["channels"][channel_id]["messages"][counter])
        end = start + return_amount

    else:
        end = -1
        while counter > -1:
            messages.append(server_data.data["channels"][channel_id]["messages"][counter])
            counter = counter - 1

    # return correct react types
    for msg in messages:
        for react in msg['reacts']:
            if curr_user_id in react['u_ids']:
                react['is_this_user_reacted'] = True
            else:
                react['is_this_user_reacted'] = False

    return {
        'messages' : messages,
        'start' : start,
        'end' : end
    }




# -------------------------CHANNEL DETAILS-------------------------

#                 Implementation for channel_details

# ----------------------------------------------------------------

def channel_details(token, channel_id):
    '''
    The following function gives details about a given channel
    '''
    # check token
    curr_user_id = token_to_user(token)

    # Check if the user exists
    check_valid_user(curr_user_id)
    check_valid_channel(channel_id)

    channel_data = server_data.data['channels'][channel_id]

    if not check_channel_member(curr_user_id, channel_id)  and not channel_data['is_public']:
        raise AccessError('User is not in the target private channel')

    # Return channel details

    # format: { name, owner_members, all_members }

    # add owner and all members
    owner_members = []
    all_members = []
    for member in channel_data['members']:
        user = server_data.data['users'][member['u_id']]
        all_members.append({
            'u_id' : user['u_id'],
            'name_first' : user['name_first'],
            'name_last' : user['name_last'],
            'profile_img_url' : user['profile_img_url']
        })
        if member['channel_permission'] == 1:
            owner_members.append({
                'u_id' : user['u_id'],
                'name_first' : user['name_first'],
                'name_last' : user['name_last'],
                'profile_img_url' : user['profile_img_url']
            })

    return ({
        'name' : channel_data['name'],
        'owner_members' : owner_members,
        'all_members' : all_members
        })


# -------------------------CHANNEL LIST -------------------------

#                 Implementation for listing channels

# ----------------------------------------------------------------

# The following functions are for listing channels

# Input: Token
# Output: List of channels

# Provide a list of all channels (and their associated details) that the
# authorised user is part of
@validate_token
def channels_list(token):
    '''
    The following function creates a channel
    '''
    is_valid_token(token)
    curr_user_id = token_to_user(token)
    channel_list = server_data.data['users'][curr_user_id]['channels']

    full_list = []
    for c_id in channel_list:
        curr_channel = server_data.data['channels'][c_id]
        full_list.append({
            'channel_id' : curr_channel['channel_id'],
            'name' : curr_channel['name']
        })
    return full_list

# Provide a list of all channels (and their associated details)
@validate_token
def channels_listall(token):
    '''
    The following function list all the channels
    '''
    is_valid_token(token)
    full_list = []
    for channel in server_data.data['channels']:
        if channel['is_public']:
            full_list.append({
                'channel_id' : channel['channel_id'],
                'name' : channel['name']
            })
    return full_list

# ------------------------- CHANNEL CREATE -------------------------

#                 Implementation for channel_create

# ----------------------------------------------------------------

# The following functions are for creating channels

# Input: token, name, is_public
# Output: Adds a channel to channels dictionary
@validate_token
def channel_create(token, name, is_public):

    '''
    The following function creates a channel
    '''

    # tests for name
    is_valid_name(name)

    if is_public == "true":
        public_bool = True
    elif is_public == "false":
        public_bool = False
    else:
        raise ValueError("Is_public must be true or false")

    # generates current user id from token
    curr_user_id = token_to_user(token)

    check_valid_user(curr_user_id)

    # generates a channel_id and assigns it to a variable
    channel_id = server_data.data["n_channels"]

    # appending a dictionary containing channel details into "channels"
    server_data.data["channels"].append({"channel_id": channel_id, "name": name, "members":
                                         [{"u_id" : curr_user_id, "channel_permission" : 1}],
                                         "messages" : [], "is_public": public_bool,
                                         "channel_n_messages": 0
                                        })

    # add all slackr owner / admins into the channel
    for user in server_data.data['users']:
        if is_slackr_admin(user['u_id']) and (user['u_id'] != curr_user_id):
            server_data.data['channels'][channel_id]['members'].append({"u_id" : user['u_id'],
                                                                        "channel_permission" : 1
                                                                        })
            server_data.data['users'][user['u_id']]['channels'].append(channel_id)

    # appending a dictionary containing channel details into 'channels' within "users"
    server_data.data['users'][curr_user_id]['channels'].append(channel_id)

    # increasing n_channels by one
    server_data.data["n_channels"] = ((server_data.data["n_channels"]) + 1)


    # returning channel_id
    return channel_id
