import csv

from django.contrib.auth import get_user_model

from pat.models import Portfolio

User = get_user_model()


def write(file_path, data):
    with open(file_path, "w") as csvfile:
        items = list(data)
        fieldnames = None
        for item in items:
            fieldnames = item.keys()
            break
        if fieldnames:
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            for item in items:
                writer.writerow(item)


def run():
    for p in Portfolio.objects.iterator():
        print("")
        print("")

        print(str(p))
        print("")
        for item in p.assets_position_ordered_by_purpose_and_percent:
            data = [
                item["percent"],
                item["asset"],
                item["purpose"],
            ]
            print("\t".join(data))
        print("...............")

        print(str(p))
        print("name\t\tpercent\tposition\t+1%")
        for item in p.subdivision_position_ordered_by_percent:

            data = [
                item["division__purpose__name"][:7],
                item["division__asset__asset_class__name"][:7],
                f"{round(item['purpose_percent'] * 100, 2)}%",
                str(round(item["purpose_position"], 2)),
                str(item["purpose_total"] * 0.01),
            ]
            print("\t".join(data))

        print("...............")

        print(str(p))
        print("name\tpercent\tposition\t+1%")
        for item in p.division_position_ordered_by_percent:

            data = [
                item["division__purpose__name"][:7],
                f"{round(item['purpose_percent'] * 100, 2)}%",
                str(round(item["purpose_position"], 2)),
                str(item["purpose_total"] * 0.01),
            ]
            print("\t".join(data))

        print("...............")
        print(str(p))
        print("name\tpercent\tposition\t+1%")
        for item in p.fidel_division_position_ordered_by_percent:
            data = [
                item["division__purpose__name"][:7],
                f"{round(item['purpose_percent'] * 100, 2)}%",
                str(round(item["purpose_position"], 2)),
                str(item["purpose_total"] * 0.01),
            ]
            print("\t".join(data))

        print("...............")
        print(str(p))
        print(p.total)

        # write("portfolio_ativos.csv", list(p.division_diffs_by_purpose))
        # write("portfolio_fatias.csv", list(p.purpose_diffs))
        # write("portfolio_global.csv", list(p.international_numbers))
