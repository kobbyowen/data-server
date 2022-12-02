import typing as t

JSONItem = t.Dict[t.Text, t.Any]

JSONItems = t.List[JSONItem]

JSONResult = t.Union[JSONItems, JSONItem]

FilterParams = t.Dict[t.Text, t.Any]

IdType = t.Union[t.Text, int]

ItemPath = t.List[t.Text]
