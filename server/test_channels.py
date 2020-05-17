'''tests'''
import sys
import pytest
from server.channels import channel_join, channel_leave, channel_addowner, channel_removeowner
from server.channels import channel_invite, channel_messages, channel_details, channels_list
from server.channels import channels_listall, channel_create
from server.helper import token_to_user, AccessError, reset_data, is_slackr_admin
from server.helper import  check_channel_member
from server.auth import auth_register
from server.messages import message_send, message_react
sys.path.append("../")


# ======================= TEST - CHANNELS ============================= #

#               This file tests all channel functions

# =========================================================================== #

#---------------------- channel_join ---------------------------------------- #

def test_channel_join():
    '''
    The following tests channel_join add's a user to channel
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    channel_id_private = channel_create(token, 'privateChannel', 'false')
    # END SETUP

    # Invalid channel ID
    with pytest.raises(ValueError):
        channel_join(token, 666)

    # Invalid token
    with pytest.raises(AccessError):
        channel_join('invalidToken', channel_id_public)

    # Trys to join private channel
    with pytest.raises(AccessError):
        channel_join(token, channel_id_private)

    # Working channel_join
    channel_join(token, channel_id_public)

def test_channel_leave():
    '''
    The following test's various sections of channel_leave
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    token2 = auth_register('abcde@email.com', 'pass123', 'john2', 'apple2')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    # END SETUP

    # Invalid channel ID
    with pytest.raises(ValueError):
        channel_leave(token, 666)

    # Invalid token
    with pytest.raises(AccessError):
        channel_leave('invalidToken', channel_id_public)

    # Working channel leave
    channel_join(token2, channel_id_public)
    channel_leave(token2, channel_id_public)

def test_channel_addowner():
    '''
    The following test's various cases of channel_addowner
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    creator_id = token_to_user(token)
    channel_id_public = channel_create(token, 'newChannel', 'true')
    second_token = auth_register('newUser@email.com', 'pass147', 'vicks', 'uwu')['token']
    second_user_id = token_to_user(second_token)
    third_token = auth_register('thirdUser@email.com', 'pass134124', 'lol', 'lmao')['token']
    third_user_id = token_to_user(third_token)
    # END SETUP

    # Invalid token
    with pytest.raises(AccessError):
        channel_addowner('invalidToken', channel_id_public, second_user_id)
    # Invalid channel ID
    with pytest.raises(ValueError):
        channel_addowner(token, 666, second_user_id)

    # trying to add when user is not in the channel
    with pytest.raises(ValueError):
        channel_addowner(second_token, channel_id_public, third_user_id)

    # trying to add random channel
    with pytest.raises(ValueError):
        channel_addowner(second_token, 999, third_user_id)

    # User is already an owner
    second_channel_id = channel_create(third_token, 'anotherCHannel', 'true')
    with pytest.raises(ValueError):
        channel_addowner(token, second_channel_id, third_user_id)


    # When user is not an admin or owner
    channel_join(second_token, channel_id_public)
    channel_join(third_token, channel_id_public)
    with pytest.raises(AccessError):
        channel_addowner(second_token, channel_id_public, third_user_id)

    # Attempting to change permission of Slackr creator
    with pytest.raises(AccessError):
        channel_addowner(second_token, channel_id_public, creator_id)

    # Working addowner
    channel_addowner(token, channel_id_public, third_user_id)

def test_channel_removeowner():
    '''
    Testing cases of channel_removeowner
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    creator_id = token_to_user(token)
    channel_id_public = channel_create(token, 'newChannel', 'true')
    second_token = auth_register('newUser@email.com', 'pass147', 'vicks', 'uwu')['token']
    second_user_id = token_to_user(second_token)
    third_token = auth_register('thirdUser@email.com', 'pass134124', 'lol', 'lmao')['token']
    third_user_id = token_to_user(third_token)
    fourth_token = auth_register('fourthUser@email.com', 'pass13424', 'Troye', 'Bob')['token']
    fourth_user_id = token_to_user(fourth_token)
    # END SETUP

    # Trying to remove someone not in the channel
    with pytest.raises(ValueError):
        channel_removeowner(token, channel_id_public, fourth_user_id)

    # Invalid token
    with pytest.raises(AccessError):
        channel_removeowner('invalidToken', channel_id_public, second_user_id)
    # Invalid channel ID
    with pytest.raises(ValueError):
        channel_removeowner(token, 666, third_user_id)

    # User already not an owner
    channel_join(fourth_token, channel_id_public)
    with pytest.raises(ValueError):
        channel_removeowner(token, channel_id_public, fourth_user_id)

    # User is not an admin or owner
    channel_join(second_token, channel_id_public)
    channel_join(third_token, channel_id_public)
    channel_addowner(token, channel_id_public, second_user_id)
    with pytest.raises(AccessError):
        channel_removeowner(third_token, channel_id_public, second_user_id)


    # Attempting to change permission of Slackr creator
    with pytest.raises(AccessError):
        channel_removeowner(second_token, channel_id_public, creator_id)

    # Working removeowner
    channel_join(third_token, channel_id_public)
    channel_addowner(token, channel_id_public, third_user_id)
    channel_removeowner(token, channel_id_public, third_user_id)

def test_channel_invite():
    '''
    Testing cases of channel_invite
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUser@email.com', 'pass147', 'vicks', 'uwu')['token']
    second_user_id = token_to_user(second_token)
    channel_id_private = channel_create(token, 'privateChannel', 'false')
    channel_id_public = channel_create(token, 'NotPrivate', 'true')
    third_token = auth_register('thirdUser@email.com', 'pass134124', 'lol', 'lmao')['token']
    third_user_id = token_to_user(third_token)
    # END SETUP

    # check if the current user who is inviting is actually part of the target channel
    with pytest.raises(AccessError):
        channel_invite(second_token, channel_id_private, third_user_id)

    # Invalid token
    with pytest.raises(AccessError):
        channel_invite('invalidToken', channel_id_private, second_user_id)

    # Working channel invite
    channel_invite(token, channel_id_private, third_user_id)
    assert check_channel_member(third_user_id, channel_id_private)

    # Inviting user who is already in the channel
    with pytest.raises(AccessError):
        channel_invite(second_token, channel_id_public, third_user_id)

    # Target user already in channel
    with pytest.raises(ValueError):
        channel_invite(token, channel_id_private, third_user_id)


def test_channel_messages():
    '''
    Testing cases of channel_messages
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUser@email.com', 'pass147', 'vicks', 'uwu')['token']
    third_token = auth_register('thirdUser@email.com', 'pass134124', 'lol', 'lmao')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    channel_id_private = channel_create(token, 'privateChannel', 'false')
    # END SETUP

    # Calling Channel messages when there are no messages
    with pytest.raises(ValueError):
        channel_messages(token, channel_id_public, 0)


    # Functioning channel messages base case
    message_send(token, channel_id_public, "Hello")
    channel_messages(token, channel_id_public, 0)

    # Calling Channel messages when current user is not in the target channel
    # and target channel is private
    message_send(token, channel_id_private, "Hi")
    with pytest.raises(AccessError):
        channel_messages(second_token, channel_id_private, 0)

    # Sending 123 messages and reacting
    message_react(token, 0, 1)
    channel_join(second_token, channel_id_public)
    message_react(second_token, 0, 1)
    channel_join(third_token, channel_id_public)
    message_send(third_token, channel_id_public, "Hey")

    counter = 2
    while counter < 124:
        message_send(token, channel_id_public, "Hello")
        counter = counter + 1

    # Testing case where end = -1
    channel_messages(token, channel_id_public, 0)
    channel_messages(token, channel_id_public, 50)
    channel_messages(token, channel_id_public, 100)

def test_channel_details():
    '''
    Testing cases of channel_details
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUser@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_private = channel_create(token, 'privateChannel', 'false')
    third_token = auth_register('thirdUser@email.com', 'pass134124', 'lol', 'lmao')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    channel_id_private = channel_create(token, 'privateChannel', 'false')
    # END SETUP

    # Invalid token
    with pytest.raises(AccessError):
        channel_details('invalidToken', channel_id_public)

    # User is not part of target channel
    with pytest.raises(AccessError):
        channel_details(third_token, channel_id_private)

    # Working channel details
    channel_join(second_token, channel_id_public)
    channel_details(token, channel_id_public)
    channel_details(second_token, channel_id_public)


def test_channels_list():
    '''
    Testing cases of channels_list
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUser@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_public = channel_create(token, 'New', 'true')
    channel_join(second_token, channel_id_public)
    # END SETUP

    # Invalid token
    with pytest.raises(AccessError):
        channels_list('invalidToken')

    # Working chanels_list
    channels_list(token)
    channels_list(second_token)

def test_channels_listall():
    '''
    Testing cases of channel_listall
    '''
    reset_data()
    # START SETUP
    token = auth_register('abcd@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUser@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_public = channel_create(token, 'Cool', 'true')
    channel_join(second_token, channel_id_public)
    # END SETUP

    # Invalid token
    with pytest.raises(AccessError):
        channels_listall('invalidToken')

    # Working chanels_list
    channels_listall(token)
    channels_listall(second_token)

def test_invalid_channel_create():
    '''
    Testing error cases of channel_create
    '''
    # Invalid token
    with pytest.raises(AccessError):
        channel_create('invalidToken', 'test', "true")

def test_invalid_name():
    '''
    Testing if the name given for channel_create is invalid
    '''
    # set up begins
    token = auth_register('abcde@email.com', 'pass123', 'john', 'apple')['token']
    # set up ends
    with pytest.raises(ValueError, match=r"*"):
        channel_create(token, 'WaitWaitWaitWaitWaitW', True)
    reset_data()

def test_is_public_valid_for_channel_create():
    '''
    Testing if the the input of is_public is valid
    '''
    # set up begins
    token = auth_register('abcde@email.com', 'pass123', 'john', 'apple')['token']
    # set up ends
    # invalid input for is_public
    with pytest.raises(ValueError):
        channel_create(token, 'Shawn', 'yes')
    reset_data()

def test_add_all_slackr_and_admins():
    '''
    Test adding a user who has slackr admin into the channel
    '''
    # set-up
    # create first user with slackr permission
    token = auth_register('abcde@email.com', 'pass123', 'john', 'apple')['token']
    creator_id = token_to_user(token)
    assert is_slackr_admin(creator_id)

    # make another user and make channel
    second_token = auth_register('NewUser@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_public = channel_create(second_token, 'newChannel', "true")

    # assert that slackr admin is in the channel
    assert check_channel_member(creator_id, channel_id_public)
    reset_data()

if __name__ == "__main__":
    pass
