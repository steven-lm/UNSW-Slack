''' auth_py pytests '''
import pytest
from server.auth import auth_register, auth_login, auth_logout, auth_passwordreset_request
from server.auth import auth_passwordreset_reset, admin_userpermission_change, hash_pw
from server.helper import reset_data, token_to_user, server_data, AccessError


# ======================= TESTS - AUTHORISATION ============================= #

#               This file tests all authorisation functions

# =========================================================================== #
reset_data()

@pytest.fixture
def generate_users():
    ''' Generating a standard fixture '''
    auth_register("A@email.com", "strong_pw", "A", "AA")
    auth_register("Z@email.com", "strong_pwZ", "B", "BB")

# register should be tested before login

# ------------------------ Testing auth_register() -------------------------- #


@pytest.mark.acc
def test_register():
    ''' Tests auth_register '''
    # check output is returned with correct parameters
    output = auth_register("regi@email.com", "strong_pw", "regi", "ster")
    assert output == {'u_id': token_to_user(output['token']), 'token': output['token']}

    # the following will result in value errors
    with pytest.raises(ValueError):
        # entering an invalid email
        auth_register("BadEmail", "strong_pw", "A", "AA")
        # password is not valid
        auth_register("A@email.com", 1235, "A", "AA")
        auth_register("A@email.com", "1", "A", "AA")
        # first name > 50 characters
        auth_register("A@email.com", "strong_pw", "A" * 51, "AA")
        # last name > 50 characters
        auth_register("A@email.com", "strong_pw", "A", "AA" * 51)

    # email address already in use
    with pytest.raises(ValueError):
        auth_register("regi@email.com", "strong_pw", "regi", "ster")

    reset_data()
    # first user
    output = auth_register("regi@email.com", "strong_pw", "regi", "ster")
    assert output == {'u_id': token_to_user(output['token']), 'token': output['token']}

# ------------------------ Testing auth_login() ----------------------------- #
@pytest.mark.acc
def test_login():
    ''' Tests auth_login '''
    auth_register('A@email.com', 'strong_pw', 'vvv', 'wwww')
    # Invalid email
    with pytest.raises(ValueError):
        auth_login("invalidEmail", "strong_pw")

    # Invalid password
    with pytest.raises(ValueError):
        auth_login("A@email.com", "incorrectPW")

    # Email does not belong to user
    with pytest.raises(ValueError):
        # logging in for user B should fail
        auth_login("B@email.com", "random_pw")
        # logging in with wrong password should fail
        auth_login("A@email.com", "wrong_pw")
        # logging in with invalid password should fail
        auth_login("A@email.com", "1")

    # logging in with empty strings should fail

    # check output is returned with correct parameters
    output = auth_login("A@email.com", "strong_pw")
    assert output == {'u_id': token_to_user(output['token']), 'token': output['token']}

# ------------------------ Testing auth_logout() ---------------------------- #

@pytest.mark.acc
def test_logout():
    ''' Tests auth logout '''
    auth_register("b@email.com", "strong_pw", "A", "AA")

    # Test successful login -> logout
    assert auth_logout(auth_login("b@email.com", "strong_pw")['token'])['is_success']


    # test logging out with an incorrect token
    auth_login("b@email.com", "strong_pw")
    assert not auth_logout("wrong_token")['is_success']

# ----------------- Testing auth_passwordreset_request() -------------------- #

@pytest.mark.reset
def test_reset_req():
    ''' Tests passwordreset_request '''
    reset_data()

    # registering user
    auth_register("xxxleothelionrawrxxx@gmail.com", "testpass", "john", "smith")

    assert server_data.data['users'][0]['reset_token'] is None

    # testing an invalid data type
    with pytest.raises(TypeError):
        auth_passwordreset_request(3333345)

    with pytest.raises(ValueError):
        # testing an invalid email will do nothing
        auth_passwordreset_request("notUser@invalid")

    with pytest.raises(ValueError):
        # testing an email does not exist will do nothing
        auth_passwordreset_request("notUser@invalid.com")

    # if the email exists, the reset code will be generated
    assert (auth_passwordreset_request("xxxleothelionrawrxxx@gmail.com")) == {}

    assert server_data.data["users"][0]['reset_token'] is not None

# ------------------ Testing auth_passwordreset_reset() --------------------- #

@pytest.mark.reset
def test_reset_reset():
    ''' Tests passwordreset_reset '''
    reset_data()
    res = auth_register("xxxleothelionrawrxxx@gmail.com", "testpass", "john", "smith")
    token = res['token']

    with pytest.raises(ValueError):
        # when the user has not requested a reset
        auth_passwordreset_reset(token, "newpass")

    auth_passwordreset_request("xxxleothelionrawrxxx@gmail.com")
    reset_code = str(server_data.data["users"][0]['reset_token'])

    with pytest.raises(ValueError):
        # if the password entered is not valid
        auth_passwordreset_reset(reset_code, "s")
    with pytest.raises(ValueError):
        # if the token is invalid
        auth_passwordreset_reset("invalidtoken", "newpass")

    # Working reset
    print(server_data.data["users"][0]['reset_token'])
    print(reset_code)
    auth_passwordreset_reset(reset_code, "newpassword")
    assert server_data.data["users"][0]['password'] == hash_pw("newpassword")

@pytest.mark.admin
def test_admin_change():
    ''' Tests permission change '''
    reset_data()
    token = auth_register("xxxleothelionrawrxxx@gmail.com", "testpass", "john", "smith")['token']
    owner_id = token_to_user(token)
    second_token = auth_register("afafrawrxxx@gmail.com", "testpass", "john", "smith")['token']
    second_id = token_to_user(second_token)
    third_token = auth_register("afaafaffrawrxxx@gmail.com", "testpass", "john", "smith")['token']
    third_id = token_to_user(third_token)

    # Invalid token
    with pytest.raises(AccessError):
        admin_userpermission_change('invalidToken', second_id, 1)

    # Invalid user id
    with pytest.raises(ValueError):
        admin_userpermission_change(token, 123123, 1)

    # Invalid permission_id
    with pytest.raises(ValueError):
        admin_userpermission_change(token, second_id, 42)

    # Owner can do anything
    admin_userpermission_change(token, second_id, 2)

    # Cannot target the owner
    with pytest.raises(AccessError):
        admin_userpermission_change(second_token, owner_id, 2)

    # Not an admin or owner
    admin_userpermission_change(token, second_id, 3)
    with pytest.raises(AccessError):
        admin_userpermission_change(second_token, third_id, 2)
    print(server_data.data)

    # User already has that permission id
    admin_userpermission_change(token, second_id, 2)
    admin_userpermission_change(second_token, third_id, 2)
    with pytest.raises(ValueError):
        admin_userpermission_change(second_token, third_id, 2)
    