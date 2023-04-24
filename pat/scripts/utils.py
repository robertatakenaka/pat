def convert_to_float(data):
    try:
        return float(data.replace(",", "."))
    except (AttributeError, TypeError, ValueError) as exc:
        return 0


def is_code(value):
    if len(value) > 2 and " " not in value:
        if value[-1].isdigit() or value[-2].isdigit() and value[-1] == "F":
            return True
    return False


def get_asset_name_and_code(data):
    asset_code = None
    asset_name = None

    if is_code(data):
        asset_code = data
        asset_name = None
    else:
        asset_name = data
        if " - " in data:
            value = data[: data.find(" - ")]
            if is_code(value):
                asset_code = value
    return {"asset_code": asset_code, "asset_name": asset_name}
