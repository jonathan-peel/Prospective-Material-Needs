import brightway2 as bw
import pandas as pd
from helpers import (
    create_inventory_dataframe,
    add_baseline_databases,
    find_activity,
    add_prospective_databases,
)

def main():
    current_project = "Material intensities: Brightway vs Premise"
    bw.projects.set_current(current_project)

    # Import EcoInvent database as the baseline
    ei_db_name = "ecoinvent_3.9.1_cutoff_ecoSpold02"

    ei_db_location = "/Users/jopeel/Library/CloudStorage/OneDrive-ETHZurich/PhD data/Tools/LCA/ecoinvent/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets"
    if ei_db_name not in bw.databases.list:
        add_baseline_databases(ei_db_name, ei_db_location)

    # Generate the prospective databases using Premise
    scenarios = ["SSP2-Base", "SSP2-PkBudg500"]
    if not all((element in bw.databases.list) for element in scenarios):
        add_prospective_databases(ei_db_name, scenarios=scenarios)

    # Find LCI for each scenario
    activity_name = "photovoltaic slanted-roof installation, 3kWp, multi-Si, panel, mounted, on roof"
    location = "CH"
    database_names = [ei_db_name] + scenarios
    LCI_dfs = {}
    for database_name in database_names:
        # Instantiate database object
        database = bw.Database(database_name)

        # Find activity
        activity = find_activity(database=database, name=activity_name, location=location)

        # Create and save material intensities
        LCI_dfs[database_name] = create_inventory_dataframe(database_name=database_name, process=activity) # how to get name of premise db?
        LCI_dfs[database_name].to_csv(f"{database_name}.csv")

    pass


if __name__ == "__main__":
    main()
