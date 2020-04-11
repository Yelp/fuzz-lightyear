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


@fuzz_lightyear.exclude.non_vulnerable_operations
def specify_non_vulnerable_operations():
    return (
        'basic.get_public_listing',
    )
