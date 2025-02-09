# with-env

Start a process with the nearby `.env`!

# Usage

## Simple

```bash
# load `.env`
with-env echo hello
```

## Profiles

```bash
# load `.env` and `.env.prod`
with-env :prod echo hello
```

## Watch and restart

```bash
# load `.env` and `.env.prod` and restart on updates
with-env -w :prod echo hello
```
