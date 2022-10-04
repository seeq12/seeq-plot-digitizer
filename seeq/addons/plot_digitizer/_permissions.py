from seeq.sdk.rest import ApiException

def print_red(text): print(f"\x1b[31m{text}\x1b[0m")

def get_user_group(group_name, user_groups_api):
    try:
        group = user_groups_api.get_user_groups(name_search=group_name)
        assert len(group.items) != 0, 'No group named "%s" was found' % group_name
        assert len(group.items) == 1, 'More that one group named "%s" was found' % group_name
        return group
    except AssertionError as error:
        print_red(error)
    except ApiException as error:
        print_red(error.body)

def get_user(user_name, users_api):
    try:
        user_ = users_api.get_users(username_search=user_name)
        if len(user_.users) == 0:
            raise ValueError(f'No user named {user_name} was found')
        if len(user_.users) > 1:
            raise ValueError(f'More than one user named {user_name} was found')
        return user_
    except AssertionError as error:
        print_red(error)
    except ApiException as error:
        print_red(error.body)

def get_plotdigitizer_package(
    formulas_api:'seeq.sdk.apis.formulas_api.FormulasApi'
) -> 'seeq.sdk.models.formula_package_output_v1.FormulaPackageOutputV1':
    try:
        return formulas_api.get_package(package_name='PltDgz')
    except ApiException:
        raise ValueError(f'Unable to access PltDgz package. Ensure that external calculation scripts are installed correctly.')

def set_acl_read_permissions_true(package_id:'str', user_id:'str', 
                 items_api:'seeq.sdk.apis.items_api.ItemsApi'
                ):
    body = {
      "identityId": user_id,
      "permissions": {
        "read": True,
      }
    }
    items_api.add_access_control_entry(id=package_id, body=body)
    return 