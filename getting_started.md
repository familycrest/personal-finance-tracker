# Getting started

## Prerequisites

If you're on Linux, here are the prerequisite packages:

```
python3 (plus any additional packages that provide `pip` and `venv`)
build-essential
pkg-config
lib-mysqlclient-dev
```

The package names might differ based on the distro you use.

## Local development/debugging

### 0. Clone the project

Run `git clone https://github.com/familycrest/personal-finance-tracker` then `cd personal_finance_tracker`.

### 1. Create a `.env` file

Copy `.env.example` to just `.env` and fill in the important variables. Remember to set `DJANGO_DEBUG=1`.

### 2. Run the project!

Run `chmod +x start_server` (you only need to do this once). Then, run `./start_server`.
