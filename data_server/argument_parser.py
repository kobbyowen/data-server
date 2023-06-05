import argparse
import sys
import typing as t


class ArgumentParser:
    def __init__(
            self, program_name: t.Text, program_description: t.Text = "",
            program_epilog: t.Text = "", arguments: t.Optional[t.List[t.Text]
                                                               ] = None) -> None:
        self.arguments = arguments
        self.program_name = program_name
        self.program_description = program_description
        self.program_epilog = program_epilog
        self.arguments = arguments if arguments else sys.argv
        self._arg_parser = argparse.ArgumentParser(
            prog=self.program_name, usage="data_server file [options]",
            description=self.program_description, epilog=self.program_epilog)
        self._add_server_arguments()
        self._add_controller_arguments()
        # used to disable stdin if server is run in a subprocess
        # this prevents werkzeug from throwing an error
        self._arg_parser.add_argument(
            "--disable-stdin", type=bool, default=False, help=argparse.SUPPRESS)
        self.parsed_args = self._arg_parser.parse_args()

    def _add_server_arguments(self) -> None:
        self._arg_parser.add_argument(
            "file", help="The path of a json or csv file to serve")
        self._arg_parser.add_argument(
            "--host", default="127.0.0.1",
            help="The host the server runs on. Defaults to %(default)s")
        self._arg_parser.add_argument(
            "--port", default=2000, type=int,
            help="The server port. Defaults to %(default)s")
        self._arg_parser.add_argument(
            "--static-folder",
            help="A path to a folder to serve static files from")
        self._arg_parser.add_argument(
            "--static-url-prefix", default="static",
            help="The url path prefix used to serve static file")
        self._arg_parser.add_argument(
            "--url-path-prefix", default="",
            help="A prefix that should be added to every request url. Example , using a"
            "prefix of /api/v3/ will mean all urls paths should be prefixed by it,"
            " http://127.0.0.1:2000/api/v3/books instead of  http://127.0.0.1:2000/books")
        self._arg_parser.add_argument(
            "--additional-headers",
            help="Additional headers to add to every response. header items are separated"
            "by semi-colon, each key and value are separated by colon.Example, X-Limit:20;X-Range:30")
        self._arg_parser.add_argument(
            "--sleep-before-request", default=0, type=int,
            help="Number of milliseconds to wait before sending response for a request."
            "Can be used to test what happens to your project when a server is slow")

    def _add_controller_arguments(self) -> None:
        self._arg_parser.add_argument(
            "--page-size", default=10, type=int,
            help="The default page size. Can be changed by using 'size'")
        self._arg_parser.add_argument(
            "--page-param-name", default="page",
            help="A url param name used to control paging. Defaults to %(default)s."
            " Example, if changed to 'leaf', urls will now use http:127.0.0.1/books?leaf=1"
            " to control pagination of resources instead of https://127.0.0.1/books?page=1."
            " Pages start from 0")
        self._arg_parser.add_argument(
            "--sort-param-name", default="sort_by",
            help="A url param name used to control sorting. Defaults to %(default)s."
            " Example, if changed to 'use', urls will now use http:127.0.0.1/books?use=name"
            " to sort resources using 'name' instead of https://127.0.0.1/books?sort_by=name."
            " Default sorting key is id")
        self._arg_parser.add_argument(
            "--order-param-name", default="order",
            help="A order param name used to control rdering. Defaults to %(default)s."
            " Example, if changed to 'arrangement', urls will now use "
            "http:127.0.0.1/books?arrangement=asc to control pagination of resources "
            "instead of https://127.0.0.1/books?order=asc. Order values are from "
            "'asc' and 'desc' for asceding and descending respectively")
        self._arg_parser.add_argument(
            "--size-param-name", default="size",
            help="A url param name used to control the size of resource returned"
            " per a request. Defaults to %(default)s. Example, if changed to 'count',"
            " urls will now use http:127.0.0.1/books?count=10 to control pagination "
            "of resources instead of https://127.0.0.1/books?size=10")
        self._arg_parser.add_argument(
            "--created-at-key-name", default="created_at",
            help="The created at key name. Use to know which field should be updated "
            "with timestamp when new resource is added. Defaults to %(default)s. "
            "Can be changed to createdAt if camel case is used in your resource.")
        self._arg_parser.add_argument(
            "--updated-at-key-name", default="updated_at",
            help="The updated at key name."
            " Used to know which field should be updated "
            "with timestamp when resources are changed. Defaults to %(default)s. "
            "Can be changed to updatedAt if camel case is used in your resource.")
        self._arg_parser.add_argument(
            "--id-name", default="id",
            help="The name of key for denoting the id of a resource. Defaults to %(default)s")
        self._arg_parser.add_argument(
            "--auto-generate-ids", type=bool, default=True,
            help="Determines whether ids"
            " should be auto generated or not during post request."
            " If not set, ids are auto generated for every post request that"
            " has no id in the request body")
        self._arg_parser.add_argument(
            "--use-timestamps", type=bool, default=True,
            help="Determines whether"
            "timestamps should be added during post request and modified after every change"
            " to the resource. The names to the timestamp keys are controlled by --created-at"
            "and --updated-at key name")

    @staticmethod
    def extract_keys(dictionary: t.Dict[t.Text, t.Any],
                     keys: t.List[t.Text]) -> t.Dict[t.Text, t.Any]:
        new_dict = {}
        for key in keys:
            new_dict[key] = dictionary[key]
        return new_dict

    def get_parsed_server_arguments(self) -> t.Dict[t.Text, t.Any]:
        return self.extract_keys(
            dict(self.parsed_args._get_kwargs()),
            ["file", "host", "port", "static_folder", "static_url_prefix",
             "additional_headers", "sleep_before_request", "url_path_prefix"])

    def get_parsed_controller_arguments(self) -> t.Dict[t.Text, t.Any]:
        return self.extract_keys(
            dict(self.parsed_args._get_kwargs()),
            ["page_size", "page_param_name", "sort_param_name",
             "order_param_name", "size_param_name", "created_at_key_name",
             "updated_at_key_name", "id_name", "auto_generate_ids",
             "use_timestamps"])

    def get_parsed_arguments(self) -> t.Dict[t.Text, t.Any]:

        args = {}
        args.update(self.get_parsed_server_arguments())
        args.update(self.get_parsed_controller_arguments())
        args.update(
            self.extract_keys(
                dict(self.parsed_args._get_kwargs()),
                ["disable_stdin"]))
        return args
