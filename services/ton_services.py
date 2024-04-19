from environs import Env
from TonTools import *


# Getting hidden consts
def load_config(path: str | None = None):
    env = Env()
    env.read_env(path)
    return [env('JETTON_MASTER'), env('CENTRAL_WALLET'), env('API'), env('CENTRAL_WALLET_MNEMONICS')]


# Is valid wallet entered?
async def check_wallet(wallet):
    config = load_config()
    client = TonCenterClient(config[2])
    wallet = Wallet(provider=client, address=wallet)


# Is valid mnemonics entered
async def check_mnemonics(mnemonics):
    config = load_config()
    client = TonCenterClient(config[2])
    your_wallet = Wallet(provider=client, mnemonics=mnemonics, version='v4r2')


# Import processing
async def jetton_import(mnemonics, value):
    config = load_config()
    client = TonCenterClient(config[2])
    your_wallet = Wallet(provider=client, mnemonics=mnemonics, version='v4r2')
    await your_wallet.transfer_jetton(
            destination_address=config[1],
            jetton_master_address=config[0],
            jettons_amount=value
        )


# Export processing
async def jetton_export(destination_address, value):
    config = load_config()
    client = TonCenterClient(config[2])
    your_wallet = Wallet(provider=client, mnemonics=config[3].split(), version='v4r2')
    await your_wallet.transfer_jetton(
        destination_address=destination_address,
        jetton_master_address=config[0],
        jettons_amount=value
    )


# Checking balance for transaction fee
async def check_balance(wallet):
    config = load_config()
    client = TonCenterClient(config[2])
    your_wallet = Wallet(provider=client, address=wallet)
    balance = await your_wallet.get_balance()
    return balance
