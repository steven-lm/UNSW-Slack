'''
    Test user_profile functions
'''
import pytest
import server_data
from server.user_profile import user_profile, user_profile_setemail, user_profile_sethandle
from server.user_profile import user_profile_setname, user_profiles_uploadphoto, users_all
from server.helper import reset_data, AccessError
from server.auth import auth_register


def test_users_all():
    ''' Tests users_all function'''
    reset_data()
    # SETUP START
    output = auth_register("test@email.com", "validPW", "tom", "cruise")
    u_id = output['u_id']
    # SETUP END

    # Working case
    assert users_all(server_data.data['users'][u_id]['token']) == {
        'users': [{
            'email': 'test@email.com',
            'handle_str': 'tomcruise',
            'name_first': 'tom',
            'name_last': 'cruise',
            'profile_img_url': '',
            'u_id': 0
        }]
    }

    # Invalid token
    with pytest.raises(AccessError):
        users_all("abcd")

def test_user_profile():
    ''' Tests user_profile function'''
    reset_data()
    # SETUP START
    output = auth_register("test@email.com", "validPW", "tom", "cruise")
    u_id = output['u_id']
    # SETUP END

    # Valid user
    assert user_profile(server_data.data['users'][u_id]['token'], u_id) == {
        'u_id': server_data.data['users'][u_id]['u_id'],
        'email' : server_data.data['users'][u_id]['email'],
        'name_first' : server_data.data['users'][u_id]['name_first'],
        'name_last' : server_data.data['users'][u_id]['name_last'],
        'handle_str' : server_data.data['users'][u_id]['handle_str'],
        'profile_img_url': server_data.data['users'][u_id]['handle_str']
    }

    # Invalid user
    with pytest.raises(ValueError):
        user_profile(server_data.data['users'][u_id]['token'], 999)

    # Invalid token:
    with pytest.raises(AccessError):
        user_profile("Invalid token", 0)


def test_user_profile_setname():
    ''' Tests user_profile_setname function '''
    reset_data()
    # SETUP START
    output = auth_register("test@email.com", "validPW", "tom", "cruise")
    u_id = output['u_id']
    # SETUP END

    # Authorised user
    user_profile_setname(server_data.data['users'][u_id]['token'], "new", "name")
    assert server_data.data['users'][u_id]['name_first'] == "new"
    assert server_data.data['users'][u_id]['name_last'] == "name"

    # First name too long
    with pytest.raises(ValueError):
        user_profile_setname(server_data.data['users'][u_id]['token'], "a" * 51, "a")

    # Last name too long
    with pytest.raises(ValueError):
        user_profile_setname(server_data.data['users'][u_id]['token'], "Tom", "a" * 51)

def test_user_profile_setemail():
    ''' Tests user_profile_setemail '''
    reset_data()
    # SETUP START
    output = auth_register("test@email.com", "validPW", "tom", "cruise")
    u_id = output['u_id']
    # SETUP END

    # Authorised User
    user_profile_setemail(server_data.data['users'][u_id]['token'], "new@email.com")

    # Invalid email provided
    with pytest.raises(ValueError):
        user_profile_setemail(server_data.data['users'][u_id]['token'], "notavalidemail")

    # Email already being used
    with pytest.raises(ValueError):
        user_profile_setemail(
            server_data.data['users'][u_id]['token'], server_data.data['users'][u_id]['email']
        )

def test_user_profile_sethandle():
    ''' Tests user_profile_sethandle function '''
    reset_data()
    # SETUP START
    output = auth_register("test@email.com", "validPW", "tom", "cruise")
    u_id = output['u_id']
    # SETUP END

    # Authorised User
    user_profile_sethandle(server_data.data['users'][u_id]['token'], "newHandle")

    # Invalid handle
    with pytest.raises(ValueError):
        user_profile_sethandle(server_data.data['users'][u_id]['token'], "a" * 21)
    with pytest.raises(ValueError):
        user_profile_sethandle(server_data.data['users'][u_id]['token'], "a" * 2)

def test_user_profiles_uploadphoto():
    ''' Tests upload photo function '''
    reset_data()
    # SETUP START
    output = auth_register("test@email.com", "validPW", "tom", "cruise")['token']
    # SETUP END
    img = 'https://i.ytimg.com/vi/MPV2METPeJU/maxresdefault.jpg'

    # Invalid token
    with pytest.raises(AccessError):
        user_profiles_uploadphoto("invalidToken", img, 0, 0, 100, 100)
    # Invalid dimensions too big
    with pytest.raises(ValueError):
        user_profiles_uploadphoto(OUTPUT, img, 0, 0, 9999999, 99999999)

    # Invalid dimensions  - x position must be 0 0
    with pytest.raises(ValueError):
        user_profiles_uploadphoto(output, img, 0, 5, 100, 100)

    # Fresh look
    user_profiles_uploadphoto(output, img, 0, 0, 100, 100)
