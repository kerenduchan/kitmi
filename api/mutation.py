import strawberry
from api.category import Category
from api.subcategory import Subcategory
from api.payee import Payee
from api.transaction import Transaction
from api.account import Account
from api.count import Count
import api.mutation_resolvers


@strawberry.type
class Mutation:

    # ---------------------------------------------------------------
    # account

    create_account: Account = strawberry.mutation(
        resolver=api.mutation_resolvers.create_account,
        description="create an account")

    update_account: Account = strawberry.mutation(
        resolver=api.mutation_resolvers.update_account,
        description="update an account")

    delete_account: Count = strawberry.mutation(
        resolver=api.mutation_resolvers.delete_account,
        description="delete an account")

    # ---------------------------------------------------------------
    # category

    create_category: Category = strawberry.mutation(
        resolver=api.mutation_resolvers.create_category,
        description="create a category")

    update_category: Category = strawberry.mutation(
        resolver=api.mutation_resolvers.update_category,
        description="update a category")

    delete_category: Count = strawberry.mutation(
        resolver=api.mutation_resolvers.delete_category,
        description="delete a category")

    move_category_up: Category = strawberry.mutation(
        resolver=api.mutation_resolvers.move_category_up,
        description="move a category higher up in the list")

    move_category_down: Category = strawberry.mutation(
        resolver=api.mutation_resolvers.move_category_down,
        description="move a category lower down in the list")

    # ---------------------------------------------------------------
    # subcategory

    create_subcategory: Subcategory = strawberry.mutation(
        resolver=api.mutation_resolvers.create_subcategory,
        description="create a subcategory")

    update_subcategory: Subcategory = strawberry.mutation(
        resolver=api.mutation_resolvers.update_subcategory,
        description="update a subcategory")

    delete_subcategory: Count = strawberry.mutation(
        resolver=api.mutation_resolvers.delete_subcategory,
        description="delete a subcategory")

    # ---------------------------------------------------------------
    # payee

    create_payee: Payee = strawberry.mutation(
        resolver=api.mutation_resolvers.create_payee,
        description="create a payee")

    update_payee: Payee = strawberry.mutation(
        resolver=api.mutation_resolvers.update_payee,
        description="update a payee")

    update_payees = strawberry.mutation(
        resolver=api.mutation_resolvers.update_payees,
        description="update many payees")

    # ---------------------------------------------------------------
    # transaction

    update_transaction: Transaction = strawberry.mutation(
        resolver=api.mutation_resolvers.update_transaction,
        description="update a transaction")
