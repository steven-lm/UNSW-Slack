import pytest
from server.auth import *
from server.helper import *
from server.messages import message_send
from server.channels import channel_create, channel_messages


def test_channel_messages():
	reset_data()
    # SETUP START
	token = auth_register('abcdef@email.com', 'pass123', 'john', 'apple')['token']
	channel_id_public = channel_create(token, 'newChannel', True)
	message_send(token, channel_id_public, "firstMessage")
	# SETUP END

	# Invalid token
	with pytest.raises(AccessError, match = r"*"):
		channel_messages(123, channel_id_public, 0)

	# Invalid channel id
	with pytest.raises(ValueError, match = r"*"):
		channel_messages(token, 123, 0)
        
	# Working channel messages (less than 50 messages)
	assert channel_messages(token, channel_id_public, 0) == [{"messages": "firstMessage", "start" : 0, "end" : -1}]

# There are less than 50 messages in the channel

def test_lessThanFiftyMessages():
    
    # setup begins
    reset_data()
    registerNewAccount = auth_register("late@yahoo.com", "validpassword", "Night", "s")
    u_id = registerNewAccount['u_id']
    token = registerNewAccount['token']    
    newChannel = channel_create(token, "New Channel", True)
    channel_id = newChannel
    
    message_send(token,channel_id,"Hello")
    
    # set up ends
    
    assert channel_messages(token, 123456, 0) == [{"messages": "Hello", "start" : 0, "end" : -1}]
    
# Test for when there are more than 50 messages in the channel

def test_greaterThanFiftyMessages():

    # setup begins
    reset_data()
    registerNewAccount = auth_register("late@yahoo.com", "validpassword", "Night", "s")
    u_id = registerNewAccount['u_id']
    token = registerNewAccount['token']    
    newChannel = channel_create(token, "New Channel", True)
    channel_id = newChannel
    
    
    message_send51(token,channel_id,"Hello") # I did not want to write this out 51 times, 
                                             # and was unsure how to shorten this   
    
    # set up ends

# unable to implement x50 of message send and test during the current iteration    
    assert channel_messages(token, 123456, 0) == [{"messages": ["Hello"],
                                                               "start" : 0, "end" : 0}]
    message_send(token,channel_id,"Hello")


    assert channel_messages(token, 123456, 0) == [{"messages": ["Hello","Hello"], "start" : 0, "end" : -1}] 

           
