import fuzzer_core


@fuzzer_core.attacker_account
def attacker_account():
    return {
        '_request_options': {
            'headers': {
                'Cookie': 'session=attacker_session',
            },
        },
    }
