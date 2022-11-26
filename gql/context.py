import strawberry.dataloader
import gql.dataloader_functions


async def get_context() -> dict:
    return {
        "categories_loader": strawberry.dataloader.DataLoader(
            load_fn=gql.dataloader_functions.get_categories_by_ids),

        "subcategories_loader": strawberry.dataloader.DataLoader(
            load_fn=gql.dataloader_functions.get_subcategories_by_ids),

        "payees_loader": strawberry.dataloader.DataLoader(
            load_fn=gql.dataloader_functions.get_payees_by_ids),

        "accounts_loader": strawberry.dataloader.DataLoader(
            load_fn=gql.dataloader_functions.get_accounts_by_ids),

        "transactions_by_accounts_loader": strawberry.dataloader.DataLoader(
            load_fn=gql.dataloader_functions.get_transactions_by_account_ids),

        "subcategories_by_categories_loader": strawberry.dataloader.DataLoader(
            load_fn=gql.dataloader_functions.get_subcategories_by_category_ids),

        "payees_by_subcategories_loader": strawberry.dataloader.DataLoader(
            load_fn=gql.dataloader_functions.get_payees_by_subcategory_ids),

        "transactions_by_payees_loader": strawberry.dataloader.DataLoader(
            load_fn=gql.dataloader_functions.get_transactions_by_payee_ids)

    }
