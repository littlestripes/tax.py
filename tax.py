#!/usr/bin/env python3
#    __
#   / /_ ____ _ _  __    ____   __  __
#  / __// __ `/| |/_/   / __ \ / / / /
# / /_ / /_/ /_>  < _  / /_/ // /_/ /
# \__/ \__,_//_/|_|(_)/ .___/ \__, /
#                    /_/     /____/
#
# Tally up your self-employment income from a CSV provided by
# your bank!
#
# honey-dos:
#   - read header from CSV and use it to parse transactions
#       (use provided list of income providers to search for/sum up different
#        income streams)
#   - OOP-ify CSV parsing with a CSVParser class
#   - translate from French to clean, professional English

import pandas as pd
import time
import sys
import argparse
import prettytable
import re

VERSION = "{} 0.4"


def to_float(a: str) -> float:
    """Takes a float as a str and returns a Python float."""
    new = []
    for char in a:
        if char == ",":
            new.append(".")
        else:
            new.append(char)
    return float("".join(new))


# subclass ArgumentParser and add arguments and attributes that way
class ArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(
            description="Extract self-employment income from bank activity."
        )
        self.add_argument(
            "csvfile",
            metavar="c",
            type=str,
            nargs=1,
            help="bank activity in CSV format",
        )
        self.add_argument(
            "--version",
            "-v",
            action="version",
            version=VERSION.format(self.prog),
            help="print version information and exit.",
        )
        self.add_argument(
            "--table",
            "-t",
            action="store_true",
            default=False,
            help="tabulate results sorted by quantity in descending order with prettytable",
        )


class CSVParser:
    def __init__(self):
        pass


def main():
    if len(sys.argv) == 1:
        print("no csv provided!!")
        sys.exit(0)

    # argparse setup
    parser = ArgumentParser()
    args = parser.parse_args()

    header = ["date", "transaction", "a", "b", "detail"]
    converters = {"transaction": to_float}

    try:
        with open(args.csvfile[0]) as csvfile:
            print(f"reading {csvfile.name}...")
            # converters will map the transaction amounts to floats
            data = pd.read_csv(csvfile, names=header, converters=converters)
    except FileNotFoundError:
        print(f"{args.csvfile[0]} not found!!")
        sys.exit(0)

    # regex setup
    courier_pattern = re.compile(r"(GRUBHUB)|(POSTMATES)")
    # and now to plumb the depths of the data
    deposits = data[data["transaction"] > 0]
    transfers = []
    transfer_dict = {'GRUBHUB': 0, 'POSTMATES': 0}  # <-- no
    for deposit in deposits.iterrows():
        # if deposit[1]["detail"][:16] in COURIER_STR:
        # this uses regex instead, much cleaner/more efficient
        # also use the deposit_search object to organize results
        deposit_search = courier_pattern.search(deposit[1]["detail"])
        if deposit_search:
            print(f"Found matching transaction on {deposit[1]['date']}")
            transfers.append(deposit)
            # transfer_dict[deposit_search.group(1)] += deposit[1]["transaction"]

    if transfers == []:
        print("No matching transactions found!")
        sys.exit()

    total = 0
    for transfer in transfers:
        total += transfer[1]["transaction"]
    total = round(total, 2)

    print(f"\nyou made ${total} from food courieringging")
    if total > 600:
        print("You got a 1099, right?")
    else:
        print("Tabulate your results with --table and fill out those forms!")
    time.sleep(1)

    if args.table:
        results_field_names = ["Amount", "Description", "Date"]
        results = prettytable.PrettyTable()
        results.field_names = results_field_names
        for transfer in transfers:
            results.add_row([transfer[1]["transaction"],
                             transfer[1]["detail"][:16],
                             transfer[1]["date"]])
            # you're not finished here!!

        print(results)

        # and for totals, too!

    sys.exit()


if __name__ == "__main__":
    main()
