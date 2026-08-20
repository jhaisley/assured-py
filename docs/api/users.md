# Users

Operations on user accounts, including the documented slim user listing
(`user-list-slim`), current-user details (`logged-in-user-details`), and
programmatic login (`login` / `login_full`). The full user listing still uses the
undocumented `external-users-list` endpoint (the previously documented
`users-list` endpoint has been removed from the API).

## Resource

::: assured.resources.users.UsersResource

## Models

::: assured.models.users.User

::: assured.models.users.UserListParams

::: assured.models.users.UserSlim

::: assured.models.users.UserSlimListParams

::: assured.models.users.LoggedInUserDetails
