import sys
import argparse
import logging
import asyncio
import db.account
import db.schema
import do_sync
import init_logging
from db.init import init_db
import db.globals


def get_parser():
    parser = argparse.ArgumentParser(
        prog='kitmi',
        description='Fetch and store financial transactions')

    subparsers = parser.add_subparsers(dest='command')

    # add_account
    create_account = subparsers.add_parser('create_account')
    create_account.add_argument('-n', '--name', nargs=1)
    create_account.add_argument('-s', '--source', choices=['leumi', 'max'])
    create_account.add_argument('-u', '--username', nargs=1)
    create_account.add_argument('-p', '--password', nargs=1)

    # sync
    sync = subparsers.add_parser('sync')
    sync.add_argument('-s', '--scraper', nargs=1)

    return parser


async def main():

    try:
        init_logging.init_logging()

        parser = get_parser()
        args = parser.parse_args(sys.argv[1:])

        init_db()

        if args.command == 'create_account':
            async with db.globals.session_maker() as s:
                await db.account.create_account(
                    s,
                    args.name[0],
                    args.source,
                    args.username[0],
                    args.password[0])

        elif args.command == 'sync':
            async with db.globals.session_maker() as s:
                await do_sync.do_sync(s, args.scraper[0])

    except Exception as e:
        logging.exception(str(e))
        raise e


if __name__ == "__main__":
    asyncio.run(main())
