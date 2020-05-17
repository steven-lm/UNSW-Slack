''' message funcions'''
import time as t
import server_data
from server.helper import is_valid_message, is_valid_token, token_to_user
from server.helper import check_valid_user, channel_exists, check_channel_member
from server.helper import channel_info, AccessError, standup_exists, get_standup
from server.helper import get_msg_dict, msg_to_channel, is_msg_removed, is_owner
from server.helper import token_to_firstname, check_valid_channel
from server.helper import is_slackr_admin, validate_token

# ============================ MESSAGE ====================================== #

#               This file contains all message functions

# =========================================================================== #

@validate_token
def search(token, query_str):
    '''
    Searches for a message
    Generates a list of messages that match the query_str
    '''

    is_valid_message(query_str)
    current_user_id = token_to_user(token)
    # List of matching messages
    matching = []

    #  Add Only list messages from channels user is part of

    # List of channel ids that the user is part of
    list_of_channels = server_data.data['users'][current_user_id]['channels']

    for channel_id in list_of_channels:
        for message in server_data.data['channels'][channel_id]['messages']:
            if query_str in message['message']:
                matching.append(message)

    return {'messages': matching}


@validate_token
def message_send(token, channel_id, message):
    '''
    Using a valid token, the user sends a message to a channel that they are part of
    '''
    curr_user_id = token_to_user(token)

    check_valid_user(curr_user_id)

    if not channel_exists(channel_id):
        raise ValueError(f"channel does not exist")

    if message is None:
        raise ValueError(f"No message")

    if len(message) > 1000:
        raise ValueError(f"Message cannot be over 1000 characters")

    if not check_channel_member(curr_user_id, channel_id):
        raise AccessError(f"User is not part of specified channel. Please join the channel.")

    info = channel_info(channel_id)

    messages = info['messages']
    message_id = server_data.data['n_messages']
    server_data.data['n_messages'] += 1

    new_message = dict()
    new_message['message_id'] = message_id
    new_message['u_id'] = curr_user_id
    new_message['message'] = message
    new_message['time_created'] = int(t.time())
    new_message['reacts'] = []
    new_message['is_pinned'] = False

    server_data.data["channels"][channel_id]["channel_n_messages"] += 1
    messages.append(dict(new_message))

    return message_id


@validate_token
def message_sendlater(token, channel_id, message, time_sent):
    '''
    Using a valid token, the user sends a message to a channel that they are part of
    at a specific time in the future
    '''
    if not channel_exists(channel_id):
        raise ValueError(f"channel does not exist")

    if message is None:
        raise ValueError(f"No message")

    if int(time_sent) < t.time():
        raise ValueError(f"Time is in the past")

    is_valid_token(token)

    is_valid_message(message)
    curr_user_id = token_to_user(token)
    check_valid_user(curr_user_id)

    if not check_channel_member(curr_user_id, channel_id):
        raise AccessError(f"User is not part of specified channel. Please join the channel.")

    message_id = server_data.data['n_messages']
    server_data.data['n_messages'] += 1

    messages_later = server_data.messages_later

    new_message = dict()
    new_message['message_id'] = message_id
    new_message['u_id'] = curr_user_id
    new_message['message'] = message
    new_message['time_created'] = int(time_sent)
    new_message['channel_id'] = channel_id
    new_message['reacts'] = []
    new_message['is_pinned'] = False

    messages_later.append(dict(new_message))

    return message_id

@validate_token
def standup_start(token, channel_id, length):
    '''
    Using a valid token, the user starts a standup period in a channel that they are
    part of
    '''
    if not channel_exists(channel_id):
        raise ValueError(f"channel does not exist")

    if standup_exists(channel_id):
        raise ValueError(f"A standup is already running in this channel")

    curr_user_id = token_to_user(token)

    if not check_channel_member(curr_user_id, int(channel_id)):
        raise AccessError(f"User is not part of specified channel. Please join the channel.")

    standups = server_data.standups

    new = dict()
    new['messages'] = []
    new['u_id'] = curr_user_id
    new['channel_id'] = channel_id
    new['time_end'] = int(t.time() + int(length))

    standups.append(new)
    return new['time_end']

@validate_token
def standup_send(token, channel_id, message):
    '''
    Using a valid token, the user sends a message in an active standup in the channel
    '''
    if not channel_exists(channel_id):
        raise ValueError(f"channel does not exist")

    if not standup_exists(channel_id):
        raise ValueError(f"Channel does not have an active standup")

    user_id = token_to_user(token)

    if not check_channel_member(user_id, channel_id):
        raise AccessError(f"User is not part of specified channel. Please join the channel.")

    if len(message) > 1000:
        raise ValueError(f"Message cannot be over 1000 characters")

    standups = server_data.standups
    target = get_standup(standups, channel_id)
    messages = target['messages']

    new_message = dict()
    new_message['first_name'] = token_to_firstname(token)
    new_message['message'] = message

    messages.append(dict(new_message))

@validate_token
def standup_active(token, channel_id):
    '''
    Using a valid token, check if a standup is active in a channel
    '''
    if not channel_exists(int(channel_id)):
        raise ValueError(f"channel does not exist")


    standups = server_data.standups
    exists = get_standup(standups, channel_id)

    if exists is None:
        return None # @@@@ NEED TO CHECK IF THIS DOES NOT TRIGGER

    return exists['time_end']

@validate_token
def message_remove(token, message_id):
    '''
    The following function removes a message @@ can change to remove completely
    '''

    curr_user_id = token_to_user(token)
    check_valid_user(curr_user_id)

    message = get_msg_dict(message_id)

    # check if the message exists
    is_msg_removed(message_id)

    channel = msg_to_channel(message_id)
    check_channel_member(curr_user_id, channel['channel_id'])

    # if the message was sent by the user
    if message['u_id'] == curr_user_id:
        pass
    # if the current user is a owner of the channel
    elif is_slackr_admin(curr_user_id):
        pass
    elif is_owner(curr_user_id, channel['channel_id']):
        pass
    else:
        raise AccessError('User does not have the right permission')

    # decrease the channel_n_messages and n_messages
    channel["channel_n_messages"] -= 1

    # deleting message
    for i in range(len(channel['messages'])):
        if channel['messages'][i]['message_id'] == int(message_id):
            del channel['messages'][i]
            break

    return {}

@validate_token
def message_edit(token, message_id, message):
    '''
    The following function edits a message
    '''

    curr_user_id = token_to_user(token)
    check_valid_user(curr_user_id)

    # if message too long / not a string
    is_valid_message(message)
    message_dict = get_msg_dict(message_id)

    # check if the message exists
    is_msg_removed(message_id)

    # Check if message is the same
    msg_str = (get_msg_dict(message_id))['message']
    if msg_str == message:
        raise ValueError(f"Message is the same")

    channel = msg_to_channel(message_id)
    check_channel_member(curr_user_id, channel['channel_id'])

    if message_dict['u_id'] == curr_user_id:
        pass
    elif is_slackr_admin(curr_user_id):
        pass
    elif is_owner(curr_user_id, channel['channel_id']):
        pass
    else:
        raise AccessError('User does not have the right permission')

    if message == "":
        message_remove(token, message_id)
    else:
        message_dict['message'] = message

    return {}

@validate_token
def message_pin(token, message_id):
    '''
    The following function pins a message
    '''

    curr_user_id = token_to_user(token)

    message = get_msg_dict(message_id)
    channel = msg_to_channel(message_id)

    # check if the message_id is valid
    if message_id >= server_data.data["n_messages"]:
        raise ValueError("message_id is invalid")

    is_msg_removed(int(message_id))

    # check if the user is valid
    check_valid_user(curr_user_id)

    # check if the channel is valid
    check_valid_channel(channel["channel_id"])

    # check if the user is in the channel
    if not check_channel_member(curr_user_id, channel["channel_id"]):
        raise AccessError("User is not a member of the channel")

    # User must be a admin of either the channel or slackr
    check_permission = server_data.data["users"][curr_user_id]["permission"]
    check_isowner = is_owner(curr_user_id, channel["channel_id"])
    if (not check_isowner) and check_permission == 3:
        raise ValueError("User is not authorised for this action")

    # check if the message is already pinned
    if message["is_pinned"]:
        raise ValueError("Message is already pinned")

    message["is_pinned"] = True
    return {}

@validate_token
def message_unpin(token, message_id):
    '''
    The following function unpins a message
    '''
    curr_user_id = token_to_user(token)

    message = get_msg_dict(message_id)
    channel = msg_to_channel(message_id)

    # check if the message_id is valid
    if message_id >= server_data.data["n_messages"]:
        raise ValueError("message_id is invalid")

    is_msg_removed(message_id)

    # check if the user is valid
    check_valid_user(curr_user_id)

    # check if the channel is valid
    check_valid_channel(channel["channel_id"])

    # check if the user is in the channel
    if not check_channel_member(curr_user_id, channel["channel_id"]):
        raise AccessError("User is not a member of the channel")

    # User must be a admin of either the channel or slackr
    check_permission = server_data.data["users"][curr_user_id]["permission"]
    check_isowner = is_owner(curr_user_id, channel["channel_id"])
    if not check_isowner and check_permission == 3:
        raise ValueError("User is not authorised for this action")

    # check if the message is already unpinned
    if not message["is_pinned"]:
        raise ValueError("Message is not currently pinned")

    message["is_pinned"] = False
    return {}

@validate_token
def message_react(token, message_id, react_id):
    '''
    This function reacts to a message
    '''
    curr_user_id = token_to_user(token)

    message = get_msg_dict(message_id)
    channel = msg_to_channel(message_id)

    # check if the message_id is valid
    if message_id >= server_data.data["n_messages"]:
        raise ValueError("message_id is invalid")

    is_msg_removed(message_id)

    # check if the user is valid
    check_valid_user(curr_user_id)

    # check if the channel is valid
    check_valid_channel(channel["channel_id"])

    # check if the user is in the channel
    if not check_channel_member(curr_user_id, channel["channel_id"]):
        raise AccessError("User is not a member of the channel")

    # check if the react_id is valid, only 1 in iteration 2
    react_id_list = [1]
    if react_id not in react_id_list:
        raise ValueError("React ID is not valid")

    # if the message already has the react id
    for react in message["reacts"]:
        if react['react_id'] == react_id:
            # check if the current user has already reacted
            if curr_user_id in react['u_ids']:
                raise ValueError("Message already reacted by current user")
            # react to the message!
            react['u_ids'].append(curr_user_id)
            return {}

    # otherwise, the message has not been reacted too
    message['reacts'].append({
        'react_id' : react_id,
        'u_ids' : [curr_user_id]
    })

    return {}

@validate_token
def message_unreact(token, message_id, react_id):
    '''
    This function unreacts to a message
    '''

    curr_user_id = token_to_user(token)

    message = get_msg_dict(message_id)
    channel = msg_to_channel(message_id)

    # check if the message_id is valid
    if message_id >= server_data.data["n_messages"]:
        raise ValueError("message_id is invalid")

    is_msg_removed(message_id)

    # check if the user is valid
    check_valid_user(curr_user_id)

    # check if the channel is valid
    check_valid_channel(channel["channel_id"])

    # check if the user is in the channel
    if not check_channel_member(curr_user_id, channel["channel_id"]):
        raise AccessError("User is not a member of the channel")

    # check if the react_id is valid, only 1 in iteration 2
    react_id_list = [1]
    if react_id not in react_id_list:
        raise ValueError("React ID is not valid")

    # check if the message already has the react_id
    # check if the user has reacted to that message

    present_flag = 0
    for react_dict in message['reacts']:
        if react_dict['react_id'] == react_id:
            present_flag = 1
            if curr_user_id in react_dict['u_ids']:
                # the current user has reacted
                react_dict['u_ids'].remove(curr_user_id)
            if len(react_dict['u_ids']) == 0:
                # remove react entirely if no more members
                del react_dict

    if present_flag == 0:
        raise ValueError("Message does not have that react")

    return {}
