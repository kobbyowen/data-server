import data_server.data_server_types as dt

data_sample: dt.JSONItem = {
    "books": [
        {
            "id": 12, "author": "Mark Mason", "title": "Professional Python"
        },
        {
            "id": 1, "author": "Kobby Owen", "title": "Advanced Python"
        },
        {
            "id": 2, "author": "Pius Lins", "title": "Beginning Python"
        },
        {
            "id": 3, "author": "OReilly", "title": "Intermediate Python"
        },
        {
            "id": 6, "author": "Guido Van Rossum", "title": "Monty Python"
        },
        {
            "id": 4, "author": "Beverly Jones", "title": "Python In A Nutshell"
        },
        {
            "id": 15, "author": "Kobby Owen", "title": "Everything about Python"
        },
    ]
}
data_sample_with_empty_posts: dt.JSONItem = {"posts": []}

data_sample_with_int_ids: dt.JSONItem = {"posts": [{"id": 1, "name": "Kobby Owen", "age": 24}]}

data_sample_with_string_ids: dt.JSONItem = {
    "posts": [{"id": "d10b6bd7-8040-4f84-b744-bc405d4101ac", "name": "Kobby Owen", "age": 24}]}

data_sample_with_timestamps: dt.JSONItem = {
    "posts": [{"id": 1, "name": "Kobby Owen", "age": 24,
               "created_at": "2022-11-24T09:51:56.726362", "updated_at": None}]}

data_sample_with_id_name_as_uuid: dt.JSONItem = {
    "posts": [{"uuid": 1, "name": "Kobby Owen", "age": 24,
               "created_at": "2022-11-24T09:51:56.726362", "updated_at": None}]}

data_sample_with_nested_items: dt.JSONItem = {
    "posts": {
        "comments": {
            "all": [
                {
                    "id": 1,
                    "userId": 20
                }
            ]
        }
    }
}
