""" Simple config reading. """

import os
import logging
import configparser
import io

logger = logging.getLogger(__name__)


def get_conf_file_contents():

    """ Test for and read the contents of the config file. """

    conf_file = '../settings.conf'
    if os.path.exists(conf_file):
        logger.info(f"Found conf file {conf_file}")
        file_content = ''
        with open(conf_file, 'r') as f:
            file_content = '[general]\n' + f.read()
        return file_content

    return None


def read_config_section(config, section):

    """ Read a section of a config file into a dict and return it. """

    logger.info(f"Reading section {section} from config.")

    configuration = {}
    options = config.options(section)

    for option in options:

        try:
            configuration[option] = config.get(section, option)
            logger.debug(f"Successfully read option {option}: {configuration[option]}")

        except configparser.NoOptionError:
            logger.warning(f"Could not read config option {option} from section {section}")
            configuration[option] = None

    return configuration


def read_local_config():
    config_parser = configparser.RawConfigParser()
    config_parser.readfp(io.StringIO(get_conf_file_contents()))
    return read_config_section(config_parser, "general")
