import logging
import sys

import config
import cf
import errors
import parser
import string
import os

MAX_SEEDS = 25

logger = logging.getLogger(__name__)


def main():

    """ Main entry point. """

    configuration = config.read_local_config()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    try:
        seed_candidates = parser.read_seed_dump(
            f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/'
            + configuration['cf_seed_dump'].replace('"', ''),
            configuration['wallet_port'].replace('"', '')[:7].strip(),
        )
    except OSError as e:
        print("ERROR: " + configuration['cf_seed_dump'] + " dump file not found. Did you forget to run the actual seeder app?")
        sys.exit(-1)
    except errors.SeedsNotFound as e:
        if hasattr(e, 'message'):
            print(f"ERROR: Problem reading seeds - {e.message}")
        else:
            print(f"ERROR: {str(e)}")

        sys.exit(-1)

    cloudflare = cf.CloudflareSeeder.from_configuration(configuration)
    current_seeds = cloudflare.get_seeds()

    logger.debug(f"Detected current seeds in cloudflare: {current_seeds}")

    if stale_current_seeds := [
        seed for seed in current_seeds if seed not in seed_candidates
    ]:
        cloudflare.delete_seeds(stale_current_seeds)
        current_good_seeds = [seed for seed in current_seeds if seed not in stale_current_seeds]
    else:
        current_good_seeds = current_seeds

    # Prune
    if len(current_good_seeds) >= MAX_SEEDS:
        if deleting := [
            seed for seed in current_good_seeds if seed not in seed_candidates
        ]:
            cloudflare.delete_seeds(deleting)
            current_good_seeds = [seed for seed in current_good_seeds if seed not in deleting]

    # Grow
    shortfall = MAX_SEEDS - len(current_good_seeds)
    to_add = []
    for seed in seed_candidates:
        if len(to_add) >= shortfall:
            break
        if seed not in current_good_seeds:
            to_add.append(seed)

    if len(to_add):
        cloudflare.set_seeds(to_add)


if __name__ == "__main__":
    main()
