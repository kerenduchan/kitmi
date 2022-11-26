import sys
import argparse
import asyncio
import db
import crypto


def get_parser():
    parser = argparse.ArgumentParser(
        prog='kitmi',
        description='Fetch and store financial transactions')

    subparsers = parser.add_subparsers(dest='command')

    # create
    subparsers.add_parser('create')

    # add_account
    add_account = subparsers.add_parser('add_account')
    add_account.add_argument('-n', '--name', nargs=1)
    add_account.add_argument('-s', '--source', choices=['leumi', 'max'])
    add_account.add_argument('-u', '--username', nargs=1)
    add_account.add_argument('-p', '--password', nargs=1)

    # sync
    sync = subparsers.add_parser('sync')
    sync.add_argument('-s', '--scraper', nargs=1)

    return parser


async def main():

    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.command == 'create':
        crypto.Crypto.generate_key()
        await db.create_db.create_db()

    elif args.command == 'add_account':
        pass
        # TODO
#            await store.accounts.insert_one(
#                db, args.name[0], args.source, args.username[0], args.password[0])

    elif args.command == 'sync':
        pass
        # TODO
#            await do_sync.do_sync(db, args.scraper[0])

if __name__ == "__main__":
    asyncio.run(main())
