import os
import os.path
import sys

import yaml


def load_config() -> dict:
    with open('config.yml') as stream:
        try:
            CONFIG = yaml.safe_load(stream)
        except Exception as e:
            print('There appears to be a syntax problem with your config.yml', file=sys.stderr)
            raise e

        if 'LICHESS_BOT_TOKEN' in os.environ:
            CONFIG['token'] = os.environ['LICHESS_BOT_TOKEN']

        # [section, type, error message]
        sections = [
            ['token', str, 'Section `token` must be a string wrapped in quotes.'],
            ['engine', dict, 'Section `engine` must be a dictionary with indented keys followed by colons.'],
            ['challenge', dict, 'Section `challenge` must be a dictionary with indented keys followed by colons.'],
            ['matchmaking', dict, 'Section `matchmaking` must be a dictionary with indented keys followed by colons.'],
            ['books', dict, 'Section `books` must be a dictionary with indented keys followed by colons.']]
        for section in sections:
            if section[0] not in CONFIG:
                raise Exception(f'Your config.yml does not have required section `{section[0]}`.')
            elif not isinstance(CONFIG[section[0]], section[1]):
                raise Exception(section[2])

        engine_sections = [
            ['dir', str, '"dir" must be a string wrapped in quotes.'],
            ['name', str, '"name" must be a string wrapped in quotes.'],
            ['ponder', bool, '"ponder" must be a bool.'],
            ['syzygy', dict, '"syzygy" must be a dictionary with indented keys followed by colons.'],
            ['gaviota', dict, '"gaviota" must be a dictionary with indented keys followed by colons.'],
            ['uci_options', dict, '"uci_options" must be a dictionary with indented keys followed by colons.'],
            ['variants', dict, '"variants" must be a dictionary with indented keys followed by colons.'],
            ['opening_books', dict, '"opening_books" must be a dictionary with indented keys followed by colons.'],
            ['online_moves', dict, '"online_moves" must be a dictionary with indented keys followed by colons.'],
            ['offer_draw', dict, '"offer_draw" must be a dictionary with indented keys followed by colons.'],
            ['resign', dict, '"resign" must be a dictionary with indented keys followed by colons.']]
        for subsection in engine_sections:
            if subsection[0] not in CONFIG['engine']:
                raise Exception(f'Your config.yml does not have required `engine` subsection `{subsection[0]}`.')
            if not isinstance(CONFIG['engine'][subsection[0]], subsection[1]):
                raise Exception(f'`engine` subsection {subsection[2]}')

        syzygy_sections = [
            ['enabled', bool, '"enabled" must be a bool.'],
            ['paths', list, '"paths" must be a list.'],
            ['max_pieces', int, '"max_pieces" must be a integer.'],
            ['instant_play', bool, '"instant_play" must be a bool.']]
        for subsection in syzygy_sections:
            if subsection[0] not in CONFIG['engine']['syzygy']:
                raise Exception(
                    f'Your config.yml does not have required `engine` `syzygy` subsection `{subsection[0]}`.')
            if not isinstance(CONFIG['engine']['syzygy'][subsection[0]], subsection[1]):
                raise Exception(f'`engine` `syzygy` subsection {subsection[2]}')

        gaviota_sections = [
            ['enabled', bool, '"enabled" must be a bool.'],
            ['paths', list, '"paths" must be a list.'],
            ['max_pieces', int, '"max_pieces" must be a integer.']]
        for subsection in gaviota_sections:
            if subsection[0] not in CONFIG['engine']['gaviota']:
                raise Exception(
                    f'Your config.yml does not have required `engine` `gaviota` subsection `{subsection[0]}`.')
            if not isinstance(CONFIG['engine']['gaviota'][subsection[0]], subsection[1]):
                raise Exception(f'`engine` `gaviota` subsection {subsection[2]}')

        variants_sections = [
            ['enabled', bool, '"enabled" must be a bool.'],
            ['dir', str, '"dir" must be a string wrapped in quotes.'],
            ['name', str, '"name" must be a string wrapped in quotes.'],
            ['ponder', bool, '"ponder" must be a bool.'],
            ['uci_options', dict, '"uci_options" must be a dictionary with indented keys followed by colons.']]
        for subsection in variants_sections:
            if subsection[0] not in CONFIG['engine']['variants']:
                raise Exception(
                    f'Your config.yml does not have required `engine` `variants` subsection `{subsection[0]}`.')
            if not isinstance(CONFIG['engine']['variants'][subsection[0]], subsection[1]):
                raise Exception(f'`engine` `variants` subsection {subsection[2]}')

        online_moves_sections = [
            ['opening_explorer', dict, '"opening_explorer" must be a dictionary with indented keys followed by colons.'],
            ['chessdb', dict, '"chessdb" must be a dictionary with indented keys followed by colons.'],
            ['lichess_cloud', dict, '"lichess_cloud" must be a dictionary with indented keys followed by colons.'],
            ['online_egtb', dict, '"online_egtb" must be a dictionary with indented keys followed by colons.']]
        for subsection in online_moves_sections:
            if subsection[0] not in CONFIG['engine']['online_moves']:
                raise Exception(
                    f'Your config.yml does not have required `engine` `online_moves` subsection `{subsection[0]}`.')
            if not isinstance(CONFIG['engine']['online_moves'][subsection[0]], subsection[1]):
                raise Exception(f'`engine` `online_moves` subsection {subsection[2]}')

        if not os.path.isdir(CONFIG['engine']['dir']):
            raise Exception(f'Your engine directory "{CONFIG["engine"]["dir"]}" is not a directory.')

        CONFIG['engine']['path'] = os.path.join(CONFIG['engine']['dir'], CONFIG['engine']['name'])

        if not os.path.isfile(CONFIG['engine']['path']):
            raise Exception(f'The engine "{CONFIG["engine"]["path"]}" file does not exist.')

        if not os.access(CONFIG['engine']['path'], os.X_OK):
            raise Exception(
                f'The engine "{CONFIG["engine"]["path"]}" doesnt have execute (x) permission. Try: chmod +x {CONFIG["engine"]["path"]}')

        if CONFIG['engine']['variants']['enabled']:
            if not os.path.isdir(CONFIG['engine']['variants']['dir']):
                raise Exception(
                    f'Your variants engine directory "{CONFIG["engine"]["variants"]["dir"]}" is not a directory.')

            CONFIG['engine']['variants']['path'] = os.path.join(
                CONFIG['engine']['variants']['dir'],
                CONFIG['engine']['variants']['name'])

            if not os.path.isfile(CONFIG['engine']['variants']['path']):
                raise Exception(f'The variants engine "{CONFIG["engine"]["variants"]["path"]}" file does not exist.')

            if not os.access(CONFIG['engine']['variants']['path'], os.X_OK):
                raise Exception(
                    f'The variants engine "{CONFIG["engine"]["variants"]["path"]}" doesnt have execute (x) permission. Try: chmod +x {CONFIG["engine"]["variants"]["path"]}')

        if CONFIG['engine']['syzygy']['enabled']:
            for path in CONFIG['engine']['syzygy']['paths']:
                if not os.path.isdir(path):
                    raise Exception(f'Your syzygy directory "{path}" is not a directory.')

        if CONFIG['engine']['gaviota']['enabled']:
            for path in CONFIG['engine']['gaviota']['paths']:
                if not os.path.isdir(path):
                    raise Exception(f'Your gaviota directory "{path}" is not a directory.')

        if CONFIG['engine']['opening_books']['enabled']:
            for key, book_list in CONFIG['engine']['opening_books']['books'].items():
                if not isinstance(book_list, list):
                    raise Exception(
                        f'The `engine: opening_books: books: {key}` section must be a list of book names or commented.')

                for book in book_list:
                    if book not in CONFIG['books']:
                        raise Exception(f'The book "{book}" is not defined in the books section.')
                    if not os.path.isfile(CONFIG['books'][book]):
                        raise Exception(f'The book "{book}" at "{CONFIG["books"][book]}" does not exist.')

                CONFIG['engine']['opening_books']['books'][key] = [CONFIG['books'][book] for book in book_list]

    return CONFIG
