from data_server.argument_parser import ArgumentParser
from data_server.core.server import Server
from data_server.core.data_router import DataRouter


parser = ArgumentParser(
    "Data Server",
    "Spin up a full fake REST API with no coding in less than 3 \
                            seconds using JSON , CSV file as the source.")

arguments = parser.get_parsed_arguments()

request_handler = DataRouter(
    arguments["file"],
    id_name=arguments["id_name"],
    sort_key_param_name=arguments["sort_param_name"],
    order_param_name=arguments["order_param_name"],
    page_param_name=arguments["page_param_name"],
    size_param_name=arguments["size_param_name"],
    autogenerate_id=arguments["auto_generate_ids"],
    use_timestamps=arguments["use_timestamps"],
    created_at_key_name=arguments["created_at_key_name"],
    updated_at_key_name=arguments["updated_at_key_name"],
    default_page_size=arguments["page_size"])

server = Server(request_handler=request_handler,
                url_path_prefix=arguments["url_path_prefix"],
                host=arguments["host"],
                port=arguments["port"],
                static_url_prefix=arguments["static_url_prefix"],
                additional_headers=arguments["additional_headers"],
                sleep_before_request=arguments["sleep_before_request"],
                extra_files=[arguments["file"]])

server.run()
