# bot

Build a Tezos bot based on the matrix-nio client library.

## Install

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
