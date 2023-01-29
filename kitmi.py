import sys
import argparse
import logging
import asyncio
import db.account
import db.schema
from db.session import session_maker
import crypto
import do_sync
import init_logging


def get_parser():
    parser = argparse.ArgumentParser(
        prog='kitmi',
        description='Fetch and store financial transactions')

    subparsers = parser.add_subparsers(dest='command')

    # create
    subparsers.add_parser('init')

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

        if args.command == 'init':

            proceed = ask_yesno("You will lose all your data. Proceed? [y/n]")
            if proceed:
                print('Generating key')
                crypto.Crypto.generate_key()

                print('Creating database')
            async with db.session.engine.begin() as conn:
                await conn.run_sync(db.schema.Base.metadata.drop_all)
                await conn.run_sync(db.schema.Base.metadata.create_all)

            await db.session.engine.dispose()

        elif args.command == 'create_account':
            async with session_maker() as s:
                await db.account.create_account(
                    s,
                    args.name[0],
                    args.source,
                    args.username[0],
                    args.password[0])

        elif args.command == 'sync':
            async with session_maker() as s:
                await do_sync.do_sync(s, args.scraper[0])

    except Exception as e:
        logging.exception(str(e))
        raise e


def ask_yesno(question):
    """
    Helper to get yes / no answer from user.
    """
    yes = ['yes', 'y']
    no = ['no', 'n']

    done = False
    print(question)
    while not done:
        choice = input().lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond by yes or no.")


if __name__ == "__main__":
    asyncio.run(main())
