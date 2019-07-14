import fuzzer_core


@fuzzer_core.victim_account
def victim_account():
    return {
        '_request_options': {
            'headers': {
                'Cookie': 'session=victim_session',
            },
        },
    }
