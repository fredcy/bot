# bot

Build a Tezos bot based on the matrix-nio client library.

## Install

On MacOS I have to install some system tools and libs first.

```
brew install automake libtool libsodium
```
The app depends on Python 3.7. I used [venv](https://github.com/pyenv/pyenv) to set a global environment for that.

Then, install the Python dependencies of the app.

```
poetry install
```

## Configure

Set up a `config` file with contents similar to this:

```
[client]

username = mybotname
password = my bots matrix password
homeserver = https://matrix.org:443

[node]

url = https://sometezosnode.io:8732
```

Set up a `secret_keys` file with the same structure as used in `~/.tezos-client`.
Note: This is a huge security risk if those keys are valuable.

Invite the bot's account to some matrix room for testing. Accept that invitation by logging in as the bot account.

## Run

```
poetry run python bot/main.py
```

# References

+ pytezos: https://github.com/murbard/pytezos

+ matrix-nio: https://github.com/poljar/matrix-nio

+ poetry: https://github.com/sdispater/poetry

