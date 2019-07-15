import fuzz_lightyear


@fuzz_lightyear.attacker_account
def attacker_account():
    return {
        '_request_options': {
            'headers': {
                'Cookie': 'session=attacker_session',
            },
        },
    }
