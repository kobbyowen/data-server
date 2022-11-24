from typing import Final

data_sample: Final = {
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
data_sample_with_empty_posts: Final = {"posts": []}

data_sample_with_int_ids: Final = {"posts": [{"id": 1, "name": "Kobby Owen", "age": 24}]}

data_sample_with_string_ids: Final = {
    "posts": [{"id": "d10b6bd7-8040-4f84-b744-bc405d4101ac", "name": "Kobby Owen", "age": 24}]}

data_sample_with_timestamps: Final = {
    "posts": [{"id": 1, "name": "Kobby Owen", "age": 24,
               "created_at": "2022-11-24T09:51:56.726362", "updated_at": None}]}

data_sample_with_id_name_as_uuid: Final = {
    "posts": [{"uuid": 1, "name": "Kobby Owen", "age": 24,
               "created_at": "2022-11-24T09:51:56.726362", "updated_at": None}]}

data_sample_with_nested_items: Final = {
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
