import fuzz_lightyear


@fuzz_lightyear.victim_account
def victim_account():
    return {
        '_request_options': {
            'headers': {
                'Cookie': 'session=victim_session',
            },
        },
    }
