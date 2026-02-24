import os
from dotenv import load_dotenv

from . import (
    BTCWallet_b2b,
    BTCWallet_kaa,

    LTCWallet_b2b,
    LTCWallet_kaa,

    XMRWallet_b2b,
    XMRWallet_ww,

    USDTWallet_b2b,
    USDTWallet_ww
)


load_dotenv()



BTC_PROVIDER = os.environ.get('BTC_PROVIDER', 'b2bwallet')
LTC_PROVIDER = os.environ.get('LTC_PROVIDER', 'b2bwallet')
XMR_PROVIDER = os.environ.get('XMR_PROVIDER', 'b2bwallet')
USDT_PROVIDER = os.environ.get('USDT_PROVIDER', 'b2bwallet')


match BTC_PROVIDER:
    case 'b2bwallet':
        BTCWallet = BTCWallet_b2b

    case 'kaawallet':
        BTCWallet = BTCWallet_kaa


match LTC_PROVIDER:
    case 'b2bwallet':
        LTCWallet = LTCWallet_b2b

    case 'kaawallet':
        LTCWallet = LTCWallet_kaa


match XMR_PROVIDER:
    case 'b2bwallet':
        XMRWallet = XMRWallet_b2b

    case 'westwallet':
        XMRWallet = XMRWallet_ww


match USDT_PROVIDER:
    case 'b2bwallet':
        USDTWallet = USDTWallet_b2b

    case 'westwallet':
        USDTWallet = USDTWallet_ww

def display_decimal(amount):
    return '{:.8f}'.format(amount).rstrip('0').rstrip('.')