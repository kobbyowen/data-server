import argparse
import sys
import typing as t


def str2bool(v: t.Any) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class ArgumentParser:
    def __init__(
        self,
        program_name: str,
        program_description: str = '',
        program_epilog: str = '',
        arguments: t.Optional[t.List[str]] = None,
    ) -> None:
        self.program_name = program_name
        self.program_description = program_description
        self.program_epilog = program_epilog
        self.arguments = arguments if arguments is not None else sys.argv[1:]

        self._arg_parser = argparse.ArgumentParser(
            prog=self.program_name,
            usage='mock-data-server file [options]',
            description=self.program_description,
            epilog=self.program_epilog,
        )
        self._add_server_arguments()
        self._add_controller_arguments()
        self._add_hidden_arguments()
        self.parsed_args = self._arg_parser.parse_args(self.arguments)

    def _add_server_arguments(self) -> None:
        self._arg_parser.add_argument('file', help='Path to the JSON or CSV file to serve.')
        self._arg_parser.add_argument(
            '--host',
            default='127.0.0.1',
            help='Host interface to bind to. Default: %(default)s.',
        )
        self._arg_parser.add_argument('--port', default=2000, type=int, help='Port to listen on. Default: %(default)s.')
        self._arg_parser.add_argument('--static-folder', help='Folder path to serve static files from.')
        self._arg_parser.add_argument(
            '--static-url-prefix',
            default='static',
            help='URL prefix used when serving static files. Default: %(default)s.',
        )
        self._arg_parser.add_argument(
            '--url-path-prefix',
            default='',
            help=(
                'URL path prefix to prepend to every endpoint. '
                'Example: with /api/v3, use http://127.0.0.1:2000/api/v3/books '
                'instead of http://127.0.0.1:2000/books.'
            ),
        )
        self._arg_parser.add_argument(
            '--additional-headers',
            help=(
                'Additional headers to add to every response. '
                'Use semicolons between headers and colons between keys and values. '
                'Example: X-Limit:20;X-Range:30.'
            ),
        )
        self._arg_parser.add_argument(
            '--sleep-before-request',
            default=0,
            type=int,
            help=(
                'Delay each response by this many milliseconds. Useful for testing client behavior against slow APIs.'
            ),
        )

    def _add_controller_arguments(self) -> None:
        self._arg_parser.add_argument(
            '--page-size',
            default=10,
            type=int,
            help='Default number of items returned per page.',
        )
        self._arg_parser.add_argument(
            '--page-param-name',
            default='page',
            help=(
                'URL query parameter name for selecting page number. Default: %(default)s. '
                "Example: if set to 'leaf', use http://127.0.0.1/books?leaf=1. "
                'Pages start at 0.'
            ),
        )
        self._arg_parser.add_argument(
            '--sort-param-name',
            default='sort_by',
            help=(
                'URL query parameter name for selecting sort field. Default: %(default)s. '
                "Example: if set to 'use', use http://127.0.0.1/books?use=name. "
                'Default sort field is id.'
            ),
        )
        self._arg_parser.add_argument(
            '--order-param-name',
            default='order',
            help=(
                'URL query parameter name for sort order. Default: %(default)s. '
                "Example: if set to 'arrangement', use http://127.0.0.1/books?arrangement=asc. "
                "Allowed values are 'asc' and 'desc'."
            ),
        )
        self._arg_parser.add_argument(
            '--size-param-name',
            default='size',
            help=(
                'URL query parameter name for page size. Default: %(default)s. '
                "Example: if set to 'count', use http://127.0.0.1/books?count=10."
            ),
        )
        self._arg_parser.add_argument(
            '--created-at-key-name',
            default='created_at',
            help=(
                'Field name used for creation timestamps on new resources. '
                'Default: %(default)s. Use createdAt for camelCase payloads.'
            ),
        )
        self._arg_parser.add_argument(
            '--updated-at-key-name',
            default='updated_at',
            help=(
                'Field name used for update timestamps when resources change. '
                'Default: %(default)s. Use updatedAt for camelCase payloads.'
            ),
        )
        self._arg_parser.add_argument(
            '--id-name',
            default='id',
            help='Field name used as the resource identifier. Default: %(default)s.',
        )
        # auto_generate_ids
        self._arg_parser.add_argument(
            '--auto-generate-ids',
            type=str2bool,
            nargs='?',
            const=True,
            default=True,
            help=(
                'Whether to auto-generate IDs for POST requests missing an ID. '
                'Default behavior is enabled. Accepts true/false.'
            ),
        )
        self._arg_parser.add_argument(
            '--no-auto-generate-ids',
            dest='auto_generate_ids',
            action='store_false',
            help='Disable auto generation of ids.',
        )
        # use_timestamps
        self._arg_parser.add_argument(
            '--use-timestamps',
            type=str2bool,
            nargs='?',
            const=True,
            default=True,
            help=(
                'Whether to set timestamps on create and update operations. '
                'Timestamp field names are controlled by --created-at-key-name '
                'and --updated-at-key-name. Accepts true/false.'
            ),
        )
        self._arg_parser.add_argument(
            '--no-use-timestamps',
            dest='use_timestamps',
            action='store_false',
            help='Disable use of timestamps.',
        )

    def _add_hidden_arguments(self) -> None:
        self._arg_parser.add_argument(
            '--disable-stdin',
            type=str2bool,
            nargs='?',
            const=True,
            default=False,
            help=argparse.SUPPRESS,
        )
        self._arg_parser.add_argument(
            '--no-disable-stdin', dest='disable_stdin', action='store_false', help=argparse.SUPPRESS
        )
        self._arg_parser.add_argument(
            '--disable-logs',
            type=str2bool,
            nargs='?',
            const=True,
            default=False,
            help=argparse.SUPPRESS,
        )
        self._arg_parser.add_argument(
            '--no-disable-logs', dest='disable_logs', action='store_false', help=argparse.SUPPRESS
        )

    @staticmethod
    def extract_keys(dictionary: t.Dict[str, t.Any], keys: t.List[str]) -> t.Dict[str, t.Any]:
        return {key: dictionary[key] for key in keys if key in dictionary}

    def get_parsed_server_arguments(self) -> t.Dict[str, t.Any]:
        return self.extract_keys(
            vars(self.parsed_args),
            [
                'file',
                'host',
                'port',
                'static_folder',
                'static_url_prefix',
                'additional_headers',
                'sleep_before_request',
                'url_path_prefix',
            ],
        )

    def get_parsed_controller_arguments(self) -> t.Dict[str, t.Any]:
        return self.extract_keys(
            vars(self.parsed_args),
            [
                'page_size',
                'page_param_name',
                'sort_param_name',
                'order_param_name',
                'size_param_name',
                'created_at_key_name',
                'updated_at_key_name',
                'id_name',
                'auto_generate_ids',
                'use_timestamps',
            ],
        )

    def get_parsed_arguments(self) -> t.Dict[str, t.Any]:
        args = {}
        args.update(self.get_parsed_server_arguments())
        args.update(self.get_parsed_controller_arguments())
        args.update(self.extract_keys(vars(self.parsed_args), ['disable_stdin', 'disable_logs']))
        return args
