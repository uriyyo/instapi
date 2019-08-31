from instapi.client import ClientProxy


def pytest_configure():
    # Turn on testing mode for ClientProxy
    ClientProxy.is_testing = True
