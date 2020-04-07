"""Configuration Factory Unit Test."""

import pytest
from data_resource_api.config import ConfigurationFactory, InvalidConfigurationError
from expects import be_an, expect, have_property, raise_error


"""Application Configuration Unit Tests."""


@pytest.mark.unit
def test_load_configuration():
    """Load a configuration from the configuration factory.

    Ensure that a configuration object can be pulled from the
    environment.
    """

    configuration = ConfigurationFactory.from_env()
    expect(configuration).to(be_an(object))
    expect(configuration).to(have_property("POSTGRES_PORT"))
    expect(configuration).to(have_property("POSTGRES_HOSTNAME"))


@pytest.mark.unit
def test_manually_request_configuration():
    """Manually specify a configuration.

    Ensure that bad or unknown configurations will throw an
    InvalidConfigurationError.
    """

    # bad configuration
    expect(lambda: ConfigurationFactory.get_config(config_type="UNDEFINED")).to(
        raise_error(InvalidConfigurationError)
    )

    # good configuration
    configuration = ConfigurationFactory.get_config(config_type="TEST")
    expect(configuration).to(be_an(object))
    expect(configuration).to(have_property("POSTGRES_PORT"))
    expect(configuration).to(have_property("POSTGRES_HOSTNAME"))
