''' tests for standup'''
import time as t
import pytest
from server.auth import auth_register
from server.channels import channel_create
from server.messages import standup_active, standup_start, standup_send
from server.helper import reset_data, AccessError, standup_messages
from server.helper import find_standup_msg
# ------------------------ Testing standup_start -------------------------- #

def test_standupstart():
    '''
    Simple test for standup
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    expected_end = int(t.time()) + 60
    time_end = standup_start(token, c_id, 60)

    assert expected_end == time_end

def test_standupstart_alreadyexists():
    '''
    Test standup when another standup is already running in the channel
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    standup_start(token, c_id, 60)

    with pytest.raises(ValueError, match=r"*"):
        standup_start(token, c_id, 60)

def test_standupstart_nochannel():
    '''
    Test standup with an invalid channel id
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    # SETUP END

    with pytest.raises(ValueError, match=r"*"):
        standup_start(token, 3, 60)
        standup_start(token, '', 60)

def test_standupstart_notmember():
    '''
    Test standup while not a member of the channel
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    # Register another user (not part of server)
    registered_user = auth_register('test2@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    with pytest.raises(AccessError, match=r"*"):
        standup_start(token, c_id, 60)

# ------------------------ Testing standup_send -------------------------- #

def test_standupsend():
    '''
    Test standup_send in an active standup
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    standup_start(token, c_id, 60)
    message = "hello world"
    standup_send(token, c_id, message)

    message_list = standup_messages(c_id)
    assert find_standup_msg(message_list, message) is message

    # Send another message
    message2 = "another message"
    standup_send(token, c_id, message2)

    message_list = standup_messages(c_id)
    assert find_standup_msg(message_list, message2) is message2

def test_standupsend_nochannel():
    '''
    Test standup_send with an invalid channel_id
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    # SETUP END
    with pytest.raises(ValueError, match=r"*"):
        standup_send(token, 4, "does not exist")

def test_standupsend_nostandup():
    '''
    Test standup_send when there is no active standup
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    with pytest.raises(ValueError, match=r"*"):
        standup_send(token, c_id, 60)

def test_standupsend_notmember():
    '''
    Test standup_send when not a member of the channel
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')
    standup_start(token, c_id, 60)

    # SETUP END

    # Register another user (not part of server)
    registered_user = auth_register('test2@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    with pytest.raises(AccessError, match=r"*"):
        standup_send(token, c_id, "hello")

def test_standupsend_toolong():
    '''
    Test standup_send when the message is too long
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    standup_start(token, c_id, 60)
    message = "a" * 1001

    with pytest.raises(ValueError, match=r"*"):
        standup_send(token, c_id, message)

# ------------------------ Testing standup_active -------------------------- #
def test_standup_active():
    '''
    Test standup_active in a channel with an active standup
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    expected_end = int(t.time()) + 60
    standup_start(token, c_id, 60)

    assert expected_end == standup_active(token, c_id)

def test_standupactive_nochannel():
    '''
    Test standup_active with an invalid channel_id
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    # SETUP END

    with pytest.raises(ValueError, match=r"*"):
        standup_active(token, 3)
        standup_active(token, '')

def test_standup_active_none():
    '''
    Test standup_active when there is no active standup
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    assert standup_active(token, c_id) is None

def test_standup_active_notmember():
    '''
    Test standup_active when user is not a member of the channel
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')
    standup_start(token, c_id, 60)

    # SETUP END

    # Register another user (not part of server)
    registered_user = auth_register('test2@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    with pytest.raises(AccessError, match=r"*"):
        standup_active(token, c_id)
