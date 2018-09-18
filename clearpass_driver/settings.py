from everett.manager import ConfigManager
from everett.manager import ConfigOSEnv

"""
:mod:`clearpass-driver.settings` -- Clearpass Driver Configuration
"""


def get_config():
    return ConfigManager(
        [
            ConfigOSEnv()
        ]
    )
