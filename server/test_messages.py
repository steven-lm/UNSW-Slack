''' tests for messages'''
import time as t
import pytest
import server_data
from server.auth import auth_register, auth_logout, admin_userpermission_change
from server.channels import channel_create, channel_addowner, channel_join
from server.messages import message_send, message_sendlater, message_edit
from server.messages import message_remove, message_react, message_unreact
from server.messages import message_pin, message_unpin, search
from server.helper import get_messages, find_message, reset_data, check_later
from server.helper import AccessError, get_message_id

# ------------------------ Testing message_send -------------------------- #

def test_simple():
    '''
    Test sending multiple messages in different channels
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    # Send message
    message_send(token, c_id, 'Hello world!')
    message_list = get_messages(c_id)
    assert find_message(message_list, 'Hello world!') == 'Hello world!'

    # Send message to a channel that already has a message
    message_send(token, c_id, 'another message')
    message_list = get_messages(c_id)
    assert find_message(message_list, 'Hello world!') == 'Hello world!'
    assert find_message(message_list, 'another message') == 'another message'

    # Send message to another channel
    c2_id = channel_create(token, 'Channel2', 'true')

    # Send message
    message_send(token, c2_id, 'Hello world!')
    message_list = get_messages(c2_id)
    assert find_message(message_list, 'Hello world!') == 'Hello world!'

def test_maximum():
    '''
    Test sending a message at the maxmium character limit (1000)
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    message_send(token, c_id, 'a' * 1000)
    message_list = get_messages(c_id)
    assert 'a' in message_list[0]['message']

def test_long():
    '''
    Test sending a message over maxmium character limit (1000)
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    with pytest.raises(ValueError, match=r"*Over 1000 characters*"):
        message_send(token, c_id, 'long message' * 1000)
        message_send(token, c_id, 'very' * 1001)

def test_no_message():
    '''
    Test sending a message with no input
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    with pytest.raises(ValueError, match=r"*"):
        message_send(token, c_id, None)

def test_nochannel():
    '''
    Test sending a message to an invalid/non existent channel
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    # SETUP END

    with pytest.raises(ValueError, match=r"*No message*"):
        message_send(token, 5, 'Hello')
        message_send(token, None, 'Hello')

def test_unauthorized():
    '''
    Test sending a message as an unauthorized user
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test3@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    # Login as new user not part of channel
    auth_logout(token)
    registered_user = auth_register('unauthorized@gmail.com', '123456',
                                    'Bob', 'Smith')
    token = registered_user['token']

    with pytest.raises(AccessError, match=r"*No message*"):
        message_send(token, c_id, 'Hello')
        message_send('', c_id, 'Hello')
        message_send(1234, c_id, 'Hello')


# ------------------------ Testing message_sendlater -------------------------- #

def test_simple_sendlater():
    '''
    Test sendlater with multiple messages in different channels
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    # Send message later
    time_sent = int(t.time() + 10)
    msg_id = message_sendlater(token, c_id, 'Hello world', time_sent)

    # Assert is stored for later
    assert check_later(msg_id) is msg_id

    # Sending message later in another channel
    c2_id = channel_create(token, 'Channel1', 'true')

    # Send message later
    time_sent = t.time() + 10
    msg_id3 = message_sendlater(token, c2_id, 'Hello world', time_sent)

    # Assert message is in channel
    assert check_later(msg_id3) is msg_id3

def test_sendlater_cap():
    '''
    Test sending a message later at the maximum character limit (1000)
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    # Send message later
    time_sent = t.time() + 10
    message_sendlater(token, c_id, 'a' * 1000, time_sent)

    # Check message is in the channel
    message_list = server_data.messages_later
    print('messages', message_list)
    assert 'a' in message_list[0]['message']

def test_nochannel_sendlater():
    '''
    Test sending a message later when the channel doesn't exist
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    # SETUP END

    time_sent = t.time() + 10
    with pytest.raises(ValueError, match=r"*"):
        message_sendlater(token, '', 'Hello world', time_sent)
        message_sendlater(token, '123', 'Hello world', time_sent)

def test_sendlater_toolong():
    '''
    Test sending a message later when the message is too long (>1000)
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    time_sent = t.time() + 10
    with pytest.raises(ValueError, match=r"*"):
        message_sendlater(token, c_id, 'Hello world' * 1000, time_sent)
        message_sendlater(token, c_id, 'a' * 1001, time_sent)

def test_sendlater_nomsg():
    '''
    Test sending a message later with no message
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    time_sent = t.time() + 10
    with pytest.raises(ValueError, match=r"*"):
        message_sendlater(token, c_id, None, time_sent)

def test_past():
    '''
    Test sending a message later when the time is in the past
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    time_sent = t.time() - 10
    with pytest.raises(ValueError, match=r"*"):
        message_sendlater(token, c_id, 'Hello world', time_sent)

def test_unauthorized_sendlater():
    '''
    Test sending a message later with an unauthorized token
    '''
    reset_data()

    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, 'Channel1', 'true')
    # SETUP END

    # Login as new user not part of channel
    auth_logout(token)
    registered_user = auth_register('test2@gmail.com', '123456', 'Bob',
                                    'Smith')
    token = registered_user['token']
    time_sent = t.time() + 10
    with pytest.raises(AccessError, match=r"*"):
        message_sendlater(token, c_id, 'Hello world', time_sent)
        message_sendlater('', c_id, 'Hello world', time_sent)


# ------------------------ Testing message_edit -------------------------- #

def test_message_edit():
    '''
    Test edit as the poster of the message on multiple messages
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_send(token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"

    msg1_id = get_message_id(message_list, "Hello world!")
    msg2_id = get_message_id(message_list, "another message")
    # SETUP END

    message_edit(token, msg1_id, "Updated message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Updated message") == "Updated message"
    message_edit(token, msg2_id, "Another update")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Another update") == "Another update"

def test_message_edit_empty():
    '''
    Test edit with an empty input, should delete the message
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    msg1_id = get_message_id(message_list, "Hello world!")

    message_edit(token, msg1_id, "")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Updated message") is None

def test_edit_owner():
    '''
    Test edit as the owner of the channel
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    first_token = registered_user['token']
    c_id = channel_create(first_token, "Channel1", 'true')

    # Add two messages
    message_send(first_token, c_id, "Hello world!")
    message_send(first_token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"

    # Login as a new user
    registered_user = auth_register("user2@gmail.com", "1password", "Bob", "Smith")
    token = registered_user['token']
    u_id = registered_user['u_id']

    # Set new user as a channel owner
    channel_join(token, c_id)
    channel_addowner(first_token, c_id, u_id)

    msg1_id = get_message_id(message_list, "Hello world!")
    msg2_id = get_message_id(message_list, "another message")
    # SETUP END

    message_edit(token, msg1_id, "Updated message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Updated message") == "Updated message"
    message_edit(token, msg2_id, "Another update")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Another update") == "Another update"

def test_edit_admin():
    '''
    Test edit as an admin of the slack
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    first_token = registered_user['token']
    c_id = channel_create(first_token, "Channel1", 'true')

    # Add two messages
    message_send(first_token, c_id, "Hello world!")
    message_send(first_token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"

    # Login as a new user
    registered_user = auth_register("user2@gmail.com", "1password", "Bob", "Smith")
    token = registered_user['token']
    u_id = registered_user['u_id']

    # Set new user as an admin of slack
    admin_userpermission_change(first_token, u_id, 2)

    msg1_id = get_message_id(message_list, "Hello world!")
    msg2_id = get_message_id(message_list, "another message")
    # SETUP END

    message_edit(token, msg1_id, "Updated message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Updated message") == "Updated message"
    message_edit(token, msg2_id, "Another update")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Another update") == "Another update"

def test_edit_same():
    '''
    Test edit when the editted message is the same as the original
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world") == "Hello world"

    msg1_id = get_message_id(message_list, "Hello world")
    # SETUP END

    with pytest.raises(ValueError, match=r"*"):
        message_edit(token, msg1_id, "Hello world")

def test_edit_cap():
    '''
    Test edit at the maximum character limit
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"

    msg1_id = get_message_id(message_list, "Hello world!")
    # SETUP END

    message_edit(token, msg1_id, "a"*999)
    message_list = get_messages(c_id)
    assert 'a' in message_list[0]['message']

def test_edit_no_id():
    '''
    Test edit when the message ID is invalid or doesn't exist
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_send(token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"
    # SETUP END

    with pytest.raises(ValueError, match=r"*"):
        message_edit(token, "123asfawf12", "update")
        message_edit(token, "", "there is no message")

def test_edit_notoken():
    '''
    Test edit with an invalid or no token
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_send(token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"

    msg1_id = get_message_id(message_list, "Hello world!")
    msg2_id = get_message_id(message_list, "another message")
    # SETUP END

    with pytest.raises(AccessError, match=r"*"):
        message_edit("123", msg1_id, "update")
        message_edit('', msg2_id, "there is no message")

def test_edit_diffuser():
    '''
    Test edit as a different user
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_send(token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"

    msg1_id = get_message_id(message_list, "Hello world!")

    # Logout
    auth_logout(token)

    # SETUP
    registered_user = auth_register('test2@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    # SETUP END

    with pytest.raises(AccessError, match=r"*"):
        message_edit(token, msg1_id, "update")

def test_edit_longmessage():
    '''
    Test edit when the edit is over the character limit
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_list = get_messages(c_id)

    msg1_id = get_message_id(message_list, "Hello world!")
    long_message = "a" * 1001

    with pytest.raises(ValueError):
        message_edit(token, msg1_id, long_message)



# ------------------------ Testing message_remove -------------------------- #

def test_remove_simple():
    '''
    Test remove with multiple messages
    '''
    reset_data()
    # SETUP
    registered_user = auth_register("test@gmail.com", "123456", "John", "Smith")
    token = registered_user['token']

    c_id = channel_create(token, "Channel1", 'true')

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_send(token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"

    msg1_id = get_message_id(message_list, "Hello world!")
    msg2_id = get_message_id(message_list, "another message")
    # SETUP END

    # Delete both messages one by one
    message_remove(token, msg1_id)
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") is None
    message_remove(token, msg2_id)
    message_list = get_messages(c_id)
    assert find_message(message_list, "another message") is None

def test_remove_owner():
    '''
    Test remove as an owner of the channel
    '''
    reset_data()
    # SETUP
    registered_user = auth_register("test@gmail.com", "123456", "John", "Smith")
    first_token = registered_user['token']
    c_id = channel_create(first_token, "Channel1", 'true')

    # Add two messages
    message_send(first_token, c_id, "Hello world!")
    message_list = get_messages(c_id)

    # Login as a new user
    registered_user = auth_register("user2@gmail.com", "1password", "Bob", "Smith")
    token = registered_user['token']
    u_id = registered_user['u_id']

    # Set new user as a channel owner
    channel_join(token, c_id)
    channel_addowner(first_token, c_id, u_id)

    # SETUP END
    msg1_id = get_message_id(message_list, "Hello world!")

    message_remove(token, msg1_id)
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") is None

def test_remove_admin():
    '''
    Test remove as an admin of the slack
    '''
    reset_data()
    # SETUP
    registered_user = auth_register("test@gmail.com", "123456", "John", "Smith")
    first_token = registered_user['token']

    c_id = channel_create(first_token, "Channel1", 'true')

    # Add two messages
    message_send(first_token, c_id, "Hello world!")
    message_send(first_token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"

    # Login as a new user
    registered_user = auth_register("user2@gmail.com", "1password", "Bob", "Smith")
    token = registered_user['token']
    u_id = registered_user['u_id']

    # Set new user as an admin of slack
    admin_userpermission_change(first_token, u_id, 2)
    # SETUP END

    message_list = get_messages(c_id)
    msg1_id = get_message_id(message_list, "Hello world!")
    message_remove(token, msg1_id)
    assert find_message(message_list, "Hello world!") is None

def test_remove_no_id():
    '''
    Test remove when message_id doesn't exist
    '''
    reset_data()
    # SETUP
    registered_user = auth_register("test@gmail.com", "123456", "John", "Smith")
    token = registered_user['token']
    c_id = channel_create(token, "Channel1", 'true')

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_send(token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"
    # SETUP END

    with pytest.raises(ValueError, match=r"*"):
        message_remove(token, "123asfawf12")
        message_remove(token, "")

# Invalid token
def test_remove_notoken():
    '''
    Test remove when token is invalid or doesn't exist
    '''
    reset_data()
    # SETUP
    registered_user = auth_register("test@gmail.com", "123456", "John", "Smith")
    token = registered_user['token']

    c_id = channel_create(token, "Channel1", 'true')

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_send(token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"
    # SETUP END

    msg1_id = get_message_id(message_list, "Hello world!")
    with pytest.raises(AccessError, match=r"*"):
        message_remove("123", msg1_id)
        message_remove("", msg1_id)

# When user is not the poster of the message
def test_remove_diffuser():
    '''
    Test remove as a different user in the channel
    '''
    reset_data()
    # SETUP
    registered_user = auth_register("test@gmail.com", "123456", "John", "Smith")
    token = registered_user['token']

    c_id = channel_create(token, "Channel1", 'true')

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_send(token, c_id, "another message")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"
    assert find_message(message_list, "another message") == "another message"

    msg1_id = get_message_id(message_list, "Hello world!")

    # Logout
    auth_logout(token)

    # Login as a new user
    registered_user = auth_register("user2@gmail.com", "1password", "Bob", "Smith")
    token = registered_user['token']

    # SETUP END

    with pytest.raises(AccessError, match=r"*"):
        message_remove(token, msg1_id)

# ------------------------ Testing React/Unreact -------------------------- #

def test_message_react():
    '''
    Test working message_react and its errors
    '''
    reset_data()
    # SETUP START
    token = auth_register('abcde@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUserrr@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    msg_id = message_send(token, channel_id_public, "firstMessage")
    # SETUP END

    react_id = 1
    # Invalid token
    with pytest.raises(AccessError):
        message_react('invalidToken', msg_id, react_id)

    # msg_id is invalid
    with pytest.raises(ValueError):
        message_react(token, 666, react_id)

    # User is not in the channel
    with pytest.raises(AccessError):
        message_react(second_token, msg_id, react_id)

    # React id is invalid
    with pytest.raises(ValueError):
        message_react(token, msg_id, 200)

    # Working react
    message_react(token, msg_id, react_id)

    # Message already reacted
    with pytest.raises(ValueError):
        message_react(token, msg_id, react_id)

def test_message_react_another():
    '''
    Test message_react as another member
    '''
    reset_data()
    # SETUP START
    token = auth_register('abcde@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUserrr@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    msg_id = message_send(token, channel_id_public, "firstMessage")
    # SETUP END

    react_id = 1

    # Working react
    message_react(token, msg_id, react_id)

    # React as another user
    channel_join(second_token, 0)
    message_react(second_token, msg_id, react_id)

def test_message_unreact():
    '''
    Test working message_unreact and its errors
    '''
    reset_data()
    # SETUP START
    token = auth_register('abcde@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUserrr@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    msg_id = message_send(token, channel_id_public, "firstMessage")
    react_id = 1
    message_react(token, msg_id, react_id)
    # SETUP END

    # Invalid token
    with pytest.raises(AccessError):
        message_unreact('invalidToken', msg_id, react_id)

    # msg_id is invalid
    with pytest.raises(ValueError):
        message_unreact(token, 666, react_id)

    # User is not in the channel
    with pytest.raises(AccessError):
        message_unreact(second_token, msg_id, react_id)

    # React id is invalid
    with pytest.raises(ValueError):
        message_unreact(token, msg_id, 200)

    # Working unreact
    message_unreact(token, msg_id, react_id)

# Edit messages as the original poster
def test_unreact_already():
    '''
    Test message_unreact when the message already has no react
    '''
    reset_data()
    # SETUP
    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, "Channel1", 'true')
    # SETUP END

    # Add two messages
    message_send(token, c_id, "Hello world!")
    message_list = get_messages(c_id)
    assert find_message(message_list, "Hello world!") == "Hello world!"

    msg1_id = get_message_id(message_list, "Hello world!")
    # SETUP END

    with pytest.raises(ValueError):
        message_unreact(token, msg1_id, 1)

# ------------------------ Testing Pin/Unpin -------------------------- #

def test_message_pin():
    '''
    Test working message_pin and all its errors
    '''
    reset_data()
    # SETUP START
    token = auth_register('abcde@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUserrr@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    msg_id = message_send(token, channel_id_public, "firstMessage")
    # SETUP END

    # Invalid token
    with pytest.raises(AccessError):
        message_pin('invalidToken', msg_id)

    # msg_id is invalid
    with pytest.raises(ValueError):
        message_pin(token, 666)

    # User is not in the channel
    with pytest.raises(AccessError):
        message_pin(second_token, msg_id)

    # User is not authorised
    channel_join(second_token, channel_id_public)
    with pytest.raises(ValueError):
        message_pin(second_token, msg_id)

    # Working message pin
    message_pin(token, msg_id)

    # Message is already pinned
    with pytest.raises(ValueError):
        message_pin(token, msg_id)

def test_message_unpin():
    '''
    Test working message_unpin and all its errors
    '''
    reset_data()
    # SETUP START
    token = auth_register('abcde@email.com', 'pass123', 'john', 'apple')['token']
    second_token = auth_register('newUserrr@email.com', 'pass147', 'vicks', 'uwu')['token']
    channel_id_public = channel_create(token, 'newChannel', 'true')
    msg_id = message_send(token, channel_id_public, "firstMessage")
    # SETUP END

    # Invalid token
    with pytest.raises(AccessError):
        message_unpin('invalidToken', msg_id)

    # msg_id is invalid
    with pytest.raises(ValueError):
        message_unpin(token, 666)

    # User is not in the channel
    with pytest.raises(AccessError):
        message_unpin(second_token, msg_id)

    # User is not authorised
    channel_join(second_token, channel_id_public)
    with pytest.raises(ValueError):
        message_unpin(second_token, msg_id)

    # Working unpin
    message_pin(token, msg_id)
    message_unpin(token, msg_id)

    # Message not pinned
    with pytest.raises(ValueError):
        message_unpin(token, msg_id)

# ------------------------ Testing Search -------------------------- #

def test_search_simple():
    '''
    Test search given a query string
    '''
    reset_data()

    # SETUP

    registered_user = auth_register('test@gmail.com', '123456', 'John',
                                    'Smith')
    token = registered_user['token']

    c_id = channel_create(token, 'Channel1', 'true')

    # SETUP END

    message_send(token, c_id, 'Hello')
    message_send(token, c_id, 'Dont find this')

    return_dic = search(token, "Hello")
    messages = return_dic['messages']

    for message in messages:
        assert "Hello" in message['message']
