import pytest
from brownie import config
from brownie import Contract


@pytest.fixture(scope="module")
def gov(accounts):
    yield accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)


# use this to set the standard amount of time we sleep between harvests.
# generally 1 day, but can be less if dealing with smaller windows (oracles) or longer if we need to trigger weekly earnings.
# some strategies won't report any profits unless we wait long enough (1 day vs 2 hours)
@pytest.fixture(scope="module")
def sleep_time():
    hour = 3600

    # change this one right here
    hours_to_sleep = 24

    sleep_time = hour * hours_to_sleep
    yield sleep_time

@pytest.fixture(scope="module")
def user(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def rewards(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def guardian(accounts):
    yield accounts[2]


@pytest.fixture(scope="module")
def management(accounts):
    yield accounts[3]


@pytest.fixture(scope="module")
def strategist(accounts):
    yield accounts[4]


@pytest.fixture(scope="module")
def keeper(accounts):
    yield accounts[5]


@pytest.fixture(scope="module")
def token():
    token_address = "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2"  # SUSHI
    yield Contract(token_address)

@pytest.fixture(scope="module")
def xsushi():
    token_address = "0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272"  # xSUSHI
    yield Contract(token_address)

@pytest.fixture(scope="module")
def token_whale(accounts):
    yield accounts.at("0xf977814e90da44bfa03b6295a0616a897441acec", force=True) #Reserve = Binance8

@pytest.fixture(scope="module")
def whale(accounts, token_whale):
    whale = token_whale
    yield whale

# use this when we might lose a few wei on conversions between want and another deposit token
@pytest.fixture(scope="module")
def is_slippery():
    is_slippery = True
    yield is_slippery


# use this to test our strategy in case there are no profits
@pytest.fixture(scope="module")
def no_profit():
    no_profit = True
    yield no_profit


@pytest.fixture(scope="module")
def amount(accounts, token, user, token_whale):
    amount = 10_000 * 10 ** token.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.
    reserve = token_whale
    token.transfer(user, amount, {"from": reserve})
    yield amount


@pytest.fixture(scope="module")
def weth():
    token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    yield Contract(token_address)


@pytest.fixture(scope="module")
def weth_amout(user, weth):
    weth_amout = 10 ** weth.decimals()
    user.transfer(weth, weth_amout)
    yield weth_amout


@pytest.fixture(scope="function")
def vault(pm, gov, rewards, guardian, management, token):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian, management)
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture(scope="function")
def strategy(strategist, keeper, vault, Strategy, gov):
    strategy = strategist.deploy(Strategy, vault)
    strategy.setKeeper(keeper)
    vault.addStrategy(strategy, 10_000, 0, 2 ** 256 - 1, 1_000, {"from": gov})
    yield strategy


@pytest.fixture(scope="session")
def RELATIVE_APPROX():
    yield 1e-5
