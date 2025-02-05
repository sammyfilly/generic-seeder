import logging
import errors

logger = logging.getLogger(__name__)


def _parse_ipv4(ip):

    """ Parse an ipv4 address and port number. """

    addr, port = ip.split(':')
    return addr, port


def _parse_ipv6(ip):

    """ Parse an ipv6 address and port number. """

    addr, port = ip.split(']:')
    return addr.replace("[", ""), port


def isipv6(ip):

    """ Extremely naive IPV6 check. """

    return '[' in ip and ']' in ip


def parse_ip(ip):

    """ Return an ip address and port number from the string """

    return _parse_ipv6(ip) if isipv6(ip) else _parse_ipv4(ip)


def read_hard_seeds(hard_seeds_file):

    """ Read the hard seed list from the file. Should just be new line separated list of IP Addresses. """

    logger.debug(f"Reading hard seeds file: {hard_seeds_file}")

    hard_seeds = []
    with open(hard_seeds_file) as seed_lines:
        for line in seed_lines:
            if stripped_line := line.strip():
                if ':' in stripped_line:
                    hard_seed = stripped_line.split(':')[0]
                else:
                    hard_seed = stripped_line

                hard_seeds.append(hard_seed)

    logger.info(f"Found {len(hard_seeds)} hard seeds.")

    if not hard_seeds:
        raise errors.SeedsNotFound(
            f"No seeds read from the hard seeds list: {hard_seeds_file}"
        )

    return hard_seeds


def read_seed_dump(seeds_file, valid_port):

    """ Read the good ip addresses from the seeds dump. """

    logger.debug(f"Reading seeds dump file: {seeds_file}")

    addresses = []
    with open(seeds_file) as seeds:

        for line in seeds:
            if line.startswith('#'):
                continue

            components = line.split()

            try:
                ip_addr, port = parse_ip(components[0])
                logger.debug(f"Parsed ip: {ip_addr}")
            except ValueError:
                logger.error(f"Could not parse ip from {components[0]} - skipping.")
                continue

            if port == valid_port and components[1] == "1":
                addresses.append(ip_addr)
                logger.debug(f"Read a good seed: IP {ip_addr} PORT {port}")

    logger.info(f"Found {len(addresses)} good ip addresses from dump file.")

    if not addresses:
        raise errors.SeedsNotFound(
            f"No good seeds read from seeds dump file: {seeds_file}"
        )

    return addresses
