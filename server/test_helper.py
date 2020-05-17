import re
from server.helper import *
from server.auth import auth_register
import pytest

# Testing if token check works

def test_is_valid_token():
    valid_token= auth_register("test@email.com", "validPW", "tom", "cruise")['token']

    # Valid token
    is_valid_token(valid_token)

    # Invalid token
    with pytest.raises(AccessError):
        is_valid_token("abcd")


# Testing if email works

def test_is_email():

    # Working Email
    is_email("hi@email.com") 

    # Only text
    with pytest.raises(ValueError):
        is_email("siohgoisdg")
    
    # No dot
    with pytest.raises(ValueError):
        is_email("hi@email")
        
    # Only numbers
    with pytest.raises(TypeError):
        is_email(238947)
        
    # No preceding string
    with pytest.raises(ValueError):
        is_email("@email")

def test_is_password():
    
    # Working password
    is_password("password123")
    
    # Not a string
    with pytest.raises(TypeError):
        is_password(123456789)
    
    # Less than 5 characters
    with pytest.raises(ValueError):
        is_password("pass")

def test_is_messages():
    
    # Working dict_list
    is_messages([{"message_id": 111, "u_id": 1, "message": "string1", "time_created": datetime(2019, 1, 1, 1, 1, 1), "is_unread": True}, {"message_id": 222, "u_id": 2, "message": "string2", "time_created": datetime(2019, 2, 2, 2, 2, 2), "is_unread": False}])     
    
    # Invalid message_id
    with pytest.raises(ValueError):
        is_messages([{"message_id": "string", "u_id": 1, "message": "string1", "time_created": datetime(2019, 1, 1, 1, 1, 1), "is_unread": True}, {"message_id": 222, "u_id": 2, "message": "string2", "time_created": datetime(2019, 2, 2, 2, 2, 2), "is_unread": False}])  
    
    # Invalid u_id
    with pytest.raises(ValueError):
        is_messages([{"message_id": 111, "u_id": "string", "message": "string1", "time_created": datetime(2019, 1, 1, 1, 1, 1), "is_unread": True}, {"message_id": 222, "u_id": 2, "message": "string2", "time_created": datetime(2019, 2, 2, 2, 2, 2), "is_unread": False}])  
        
    # Invalid message
    with pytest.raises(ValueError):
        is_messages([{"message_id": 111, "u_id": 1, "message": 123, "time_created": datetime(2019, 1, 1, 1, 1, 1), "is_unread": True}, {"message_id": 222, "u_id": 2, "message": "string2", "time_created": datetime(2019, 2, 2, 2, 2, 2), "is_unread": False}])     
    
    # Invalid time_created
    with pytest.raises(ValueError):
        is_messages([{"message_id": 111, "u_id": 1, "message": 123, "time_created": datetime(2019, 1, 1, 1, 1), "is_unread": True}, {"message_id": 222, "u_id": 2, "message": "string2", "time_created": datetime(2019, 2, 2, 2, 2, 2), "is_unread": False}])     
    # Add raise error for time 

    # Invalid is_unread
    with pytest.raises(ValueError):
        is_messages([{"message_id": 111, "u_id": 1, "message": "string1", "time_created": datetime(2019, 1, 1, 1, 1, 1), "is_unread": True}, {"message_id": 222, "u_id": 2, "message": "string2", "time_created": datetime(2019, 2, 2, 2, 2, 2), "is_unread": "True"}])     
   
def test_is_channels():
    
    # Working dict_list
    is_channels([{"id": 1, "name": "name1"}, {"id": 2, "name": "name2"}])
    
    # Invalid id
    with pytest.raises(ValueError):
        is_channels([{"id": "abc", "name": "name1"}, {"id": 2, "name": "name2"}])
        
    # Invalid name
    with pytest.raises(ValueError):
        is_channels([{"id": 1, "name": 123}, {"id": 2, "name": "name2"}])

def test_is_members():

    # Working dict_list
    is_members([{"u_id": 1, "name_first": "first1", "name_last": "last1"}, {"u_id": 2, "name_first": "first2", "name_last": "last2"}])
    
    # Invalid u_id
    with pytest.raises(ValueError):
        is_members([{"u_id": "abc", "name_first": "first1", "name_last": "last1"}, {"u_id": 2, "name_first": "first2", "name_last": "last2"}])
        
    # Invalid name_first
    with pytest.raises(ValueError):
        is_members([{"u_id": 1, "name_first": 123, "name_last": "last1"}, {"u_id": 2, "name_first": "first2", "name_last": "last2"}])
    
    # Invalid name_last
    with pytest.raises(ValueError):
        is_members([{"u_id": 1, "name_first": "first1", "name_last": 789}, {"u_id": 2, "name_first": "first2", "name_last": "last2"}])
