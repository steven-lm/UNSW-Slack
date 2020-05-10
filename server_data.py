# ============================ DATA =================================== #

#            This file contains global data variables

# ===================================================================== # 


global data

data = {
    "n_users"       : 0,
    "users"         : [],
    "n_channels"    : 0,
    "channels"      : [],
    "n_messages"    : 0    
}

'''
Below is sample data used for testing and data reference

data = {
    "n_users" : 2,
    "users" : [{    
        'token': 'valid_token',
        'email': 'testsubject@email.com',
        'password': 'valid_password',
        'name_first': 'test',
        'name_last': 'subject',
        'handle_str' : 'test_handle',
        'u_id': 0,
        'channels':[ 0 ],
        'permission':'',   
    }],
    "n_channels": 2,
    "channels": [
        {   
        "channel_id": 0, 
        "name": "name", 
        "members": [     
                {
                    'u_id': '0',
                    'channel_permission': '1',
                }
            ],
        "messages" : [
    
            {   
                 "msg_id": 0,
                 "u_id": 0,
                 "message": "hello world",
                 "time_created": 1,
                 "reacts" : [],
                 "is_pinned" : False
            },
    
            {   
                 "msg_id": 1,
                 "u_id": 0,
                 "message": "Another message",
                 "time_created": 2,
                 "reacts" : [],
                 "is_pinned" : False
            }
    
        ],
        "is_public" : True
          
        },
        
       {   
       "channel_id": 1, 
       "name": "name1", 
       "members": [     
                {
                    'u_id': '1',
                    'channel_permission': '1',
                }
            ],
        "messages" : [],
        "is_public" : False  
        },
       
    ],
    
    "n_messages" : 2
    
}
'''
global user_list
global channels_list
global owner_list
user_list = data['users']
channels_list = data['channels']

global messages_later
messages_later = []

global standups
standups = []

'''
# Users (in 'users' list)
user = {
    'token': '',
    'email': '',
    'password': '',
    'first_name': '',
    'last_name': '',
    'u_id': '',
    'channels':'',
    'slackr_permission':'',
}

# Channels (in 'channels' list)
channel = {
    'channel_name': '',
    'channel_id':'',
    'members':[],
    'owners':[],
    'is_public': False,
    'messages': [],
    'n_messages': 0,
}

# Messages (in channel info)
message = {
    'msg_id':,
    'u_id':,
    'message':,
    'time_created':,
    'reacts': [],
    'is_pinned': False,
}

# Messages (in messages_later)
message = {
    'msg_id':,
    'u_id':,
    'message':,
    'time_created':,
    'reacts': [],
    'channel_id':, 
    'is_pinned': False,
}

# In 'members' list inside a channel dictionary
{
    'u_id': '',
    'channel_permission': '',
}

# messages (in data list)
message = {
    'message_id': '',
    'u_id': '',
    'message':'',
    'time_created':'',
    'reacts':[],
    'is_pinned':
}

# reacts (in "messages" list)
# u_ids is a list of all u_id who have reacted to the comment
react = {
    'react_id': '',
    'u_ids': [],
    'is_this_user_reacted':
}
'''

if __name__ == '__main__':
    pass
