import warnings
import pandas as pd
import brightway2 as bw
import premise as pm

from bw2data.backends.peewee.proxies import Activity
from bw2data.backends.peewee.database import SQLiteBackend

# TODO: ask Adrien if this list is okay; TODO: switch this to csv file
final_metals = [
    "Aluminium",
    "Antimony",
    "Arsenic",
    "Boron",
    "Cadmium",
    "Cerium",
    "Chromium",
    "Cobalt",
    "Copper",
    "Dysprosium",
    "Europium",
    "Feldspar",
    "Fluorspar",
    "Gadolinium",
    "Gallium",
    "Graphite",
    "Hafnium",
    "Lanthanum",
    "Lithium",
    "Magnesium",
    "Manganese",
    "Neodymium",
    "Nickel",
    "Niobium",
    "Palladium",
    "Phosphorus",
    "Platinum",
    "Praseodymium",
    "Rhodium",
    "Samarium",
    "Scandium",
    "Selenium",
    "Silicon",
    "Silver",
    "Strontium",
    "Tantalum",
    "Tellurium",
    "Terbium",
    "Tin",
    "Titanium",
    "Vanadium",
    "Yttrium",
    "Zinc",
    "Zirconium",
]


def add_baseline_databases(db_name: str, db_location: str):
    """db_name is name of the baseline ecoinvent database.
    db_location is the location of the db on disk
    """
    # import elementary flows, LCIA methods and some other data
    bw.bw2setup()

    # import ecoinvent
    if db_name in bw.databases:
        print("Database has already been imported.")
    else:
        fpei39cut = db_location
        ei39cut = bw.SingleOutputEcospold2Importer(fpei39cut, db_name)
        ei39cut.apply_strategies()
        print(ei39cut.statistics())
        ei39cut.write_database()


def add_prospective_databases(base_db_name: str, scenarios: list):
    """Add a prospective database to the brightway project using Premise."""

    scenarios_list = []
    for scenario in scenarios:
        scenarios_list.append({"model": "remind", "pathway": scenario, "year": 2050})

    db = pm.NewDatabase(
        scenarios=scenarios_list,
        source_db=base_db_name,
        source_version="3.9.1",
        key="tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=",
    )

    db.update_all()  # function requires a long time to run
    db.write_db_to_brightway(name=scenarios)


def find_activity(database: SQLiteBackend, name: str, location: str) -> Activity:
    list_of_possibilities = [
        act
        for act in database
        if (name in act["name"]) and (location in act["location"])
    ]
    if len(list_of_possibilities) > 1:
        raise LookupError()
    if len(list_of_possibilities) == 1:
        return list_of_possibilities[0]


def create_inventory_dataframe(
    database_name: str, process: str, interests=final_metals, cutoff=None
):
    """ """
    lca = bw.LCA({process: 1})
    lca.lci()
    array = lca.inventory.sum(axis=1)

    if cutoff is not None and not (0 < cutoff < 1):
        warnings.warn(f"Ignoring invalid cutoff value {cutoff}")
        cutoff = None

    total = array.sum()

    if hasattr(lca, "dicts"):
        mapping = lca.dicts.biosphere
    else:
        mapping = lca.biosphere_dict

    data = []

    include = lambda x: abs(x / total) >= cutoff if cutoff is not None else True
    for key, row in mapping.items():
        amount = array[row, 0]
        if include(amount):
            data.append((bw.get_activity(key), row, amount))

    data.sort(key=lambda x: abs(x[2]))

    ## returns a dataframe with
    res = pd.DataFrame(
        [
            {
                "Category": str(flow.get("categories")),
                "Type": flow.get("type"),
                "Exchange": flow.get("name"),
                "Unit": flow.get("unit"),
                "Value": amount,
            }
            for flow, row, amount in data
        ]
    )
    # only return the data for the metals you need (or any exchange you need)
    modified_fei_list = [metal + ", in ground" for metal in interests]
    all_present = [
        metal for metal in modified_fei_list if metal in res["Exchange"].tolist()
    ]  # if process is based on ecoinvent 3.8
    all_present += [
        metal for metal in interests if metal in res["Exchange"].tolist()
    ]  # if process is based on ecoinvent 3.9

    res = res[res["Exchange"].isin(all_present)]
    res = res[res["Type"] == "natural resource"]
    res.set_index("Exchange", inplace=True)

    return res.sort_index()
