import argparse
import sys
import typing as t

def str2bool(v):
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
        program_description: str = "",
        program_epilog: str = "",
        arguments: t.Optional[t.List[str]] = None
    ) -> None:
        self.program_name = program_name
        self.program_description = program_description
        self.program_epilog = program_epilog
        self.arguments = arguments if arguments is not None else sys.argv[1:]

        self._arg_parser = argparse.ArgumentParser(
            prog=self.program_name,
            usage="data_server file [options]",
            description=self.program_description,
            epilog=self.program_epilog
        )
        self._add_server_arguments()
        self._add_controller_arguments()
        self._add_hidden_arguments()
        self.parsed_args = self._arg_parser.parse_args(self.arguments)

    def _add_server_arguments(self) -> None:
        self._arg_parser.add_argument(
            "file", help="The path of a json or csv file to serve"
        )
        self._arg_parser.add_argument(
            "--host", default="127.0.0.1",
            help="The host the server runs on. Defaults to %(default)s"
        )
        self._arg_parser.add_argument(
            "--port", default=2000, type=int,
            help="The server port. Defaults to %(default)s"
        )
        self._arg_parser.add_argument(
            "--static-folder",
            help="A path to a folder to serve static files from"
        )
        self._arg_parser.add_argument(
            "--static-url-prefix", default="static",
            help="The url path prefix used to serve static file"
        )
        self._arg_parser.add_argument(
            "--url-path-prefix", default="",
            help=(
                "A prefix that should be added to every request url. Example: using a "
                "prefix of /api/v3/ will mean all urls paths should be prefixed by it, "
                "http://127.0.0.1:2000/api/v3/books instead of http://127.0.0.1:2000/books"
            )
        )
        self._arg_parser.add_argument(
            "--additional-headers",
            help=(
                "Additional headers to add to every response. Header items are separated "
                "by semi-colon, each key and value are separated by colon. Example: X-Limit:20;X-Range:30"
            )
        )
        self._arg_parser.add_argument(
            "--sleep-before-request", default=0, type=int,
            help=(
                "Number of milliseconds to wait before sending response for a request. "
                "Can be used to test what happens to your project when a server is slow"
            )
        )

    def _add_controller_arguments(self) -> None:
        self._arg_parser.add_argument(
            "--page-size", default=10, type=int,
            help="The default page size. Can be changed by using 'size'"
        )
        self._arg_parser.add_argument(
            "--page-param-name", default="page",
            help=(
                "A url param name used to control paging. Defaults to %(default)s. "
                "Example: if changed to 'leaf', urls will now use http:127.0.0.1/books?leaf=1 "
                "to control pagination of resources instead of https://127.0.0.1/books?page=1. "
                "Pages start from 0"
            )
        )
        self._arg_parser.add_argument(
            "--sort-param-name", default="sort_by",
            help=(
                "A url param name used to control sorting. Defaults to %(default)s. "
                "Example: if changed to 'use', urls will now use http:127.0.0.1/books?use=name "
                "to sort resources using 'name' instead of https://127.0.0.1/books?sort_by=name. "
                "Default sorting key is id"
            )
        )
        self._arg_parser.add_argument(
            "--order-param-name", default="order",
            help=(
                "A order param name used to control ordering. Defaults to %(default)s. "
                "Example: if changed to 'arrangement', urls will now use "
                "http:127.0.0.1/books?arrangement=asc to control pagination of resources "
                "instead of https://127.0.0.1/books?order=asc. Order values are 'asc' and 'desc'."
            )
        )
        self._arg_parser.add_argument(
            "--size-param-name", default="size",
            help=(
                "A url param name used to control the size of resource returned per request. "
                "Defaults to %(default)s. Example: if changed to 'count', urls will now use "
                "http:127.0.0.1/books?count=10 to control pagination of resources instead of "
                "https://127.0.0.1/books?size=10"
            )
        )
        self._arg_parser.add_argument(
            "--created-at-key-name", default="created_at",
            help=(
                "The created at key name. Used to know which field should be updated "
                "with timestamp when new resource is added. Defaults to %(default)s. "
                "Can be changed to createdAt if camel case is used in your resource."
            )
        )
        self._arg_parser.add_argument(
            "--updated-at-key-name", default="updated_at",
            help=(
                "The updated at key name. Used to know which field should be updated "
                "with timestamp when resources are changed. Defaults to %(default)s. "
                "Can be changed to updatedAt if camel case is used in your resource."
            )
        )
        self._arg_parser.add_argument(
            "--id-name", default="id",
            help="The name of key for denoting the id of a resource. Defaults to %(default)s"
        )
        # auto_generate_ids
        self._arg_parser.add_argument(
            "--auto-generate-ids", type=str2bool, nargs='?', const=True, default=True,
            help=(
                "Determines whether ids should be auto generated or not during post request. "
                "If not set, ids are auto generated for every post request that has no id in the request body. "
                "Accepts true/false."
            )
        )
        self._arg_parser.add_argument(
            "--no-auto-generate-ids", dest="auto_generate_ids", action="store_false",
            help="Disable auto generation of ids."
        )
        # use_timestamps
        self._arg_parser.add_argument(
            "--use-timestamps", type=str2bool, nargs='?', const=True, default=True,
            help=(
                "Determines whether timestamps should be added during post request and modified after every change "
                "to the resource. The names to the timestamp keys are controlled by --created-at and --updated-at key name. "
                "Accepts true/false."
            )
        )
        self._arg_parser.add_argument(
            "--no-use-timestamps", dest="use_timestamps", action="store_false",
            help="Disable use of timestamps."
        )

    def _add_hidden_arguments(self) -> None:
        self._arg_parser.add_argument(
            "--disable-stdin", type=str2bool, nargs='?', const=True, default=False, help=argparse.SUPPRESS
        )
        self._arg_parser.add_argument(
            "--no-disable-stdin", dest="disable_stdin", action="store_false", help=argparse.SUPPRESS
        )
        self._arg_parser.add_argument(
            "--disable-logs", type=str2bool, nargs='?', const=True, default=False, help=argparse.SUPPRESS
        )
        self._arg_parser.add_argument(
            "--no-disable-logs", dest="disable_logs", action="store_false", help=argparse.SUPPRESS
        )

    @staticmethod
    def extract_keys(dictionary: t.Dict[str, t.Any], keys: t.List[str]) -> t.Dict[str, t.Any]:
        return {key: dictionary[key] for key in keys if key in dictionary}

    def get_parsed_server_arguments(self) -> t.Dict[str, t.Any]:
        return self.extract_keys(
            vars(self.parsed_args),
            [
                "file", "host", "port", "static_folder", "static_url_prefix",
                "additional_headers", "sleep_before_request", "url_path_prefix"
            ]
        )

    def get_parsed_controller_arguments(self) -> t.Dict[str, t.Any]:
        return self.extract_keys(
            vars(self.parsed_args),
            [
                "page_size", "page_param_name", "sort_param_name",
                "order_param_name", "size_param_name", "created_at_key_name",
                "updated_at_key_name", "id_name", "auto_generate_ids",
                "use_timestamps"
            ]
        )

    def get_parsed_arguments(self) -> t.Dict[str, t.Any]:
        args = {}
        args.update(self.get_parsed_server_arguments())
        args.update(self.get_parsed_controller_arguments())
        args.update(
            self.extract_keys(
                vars(self.parsed_args),
                ["disable_stdin", "disable_logs"]
            )
        )
        return args
