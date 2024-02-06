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
    ei_db_name = "ecoinvent_3.9_cutoff_ecoSpold02"
    ei_db_location = "/Users/jopeel/Library/CloudStorage/OneDrive-ETHZurich/PhD data/Tools/LCA/ecoinvent/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets"
    if ei_db_name not in bw.databases.list:
        add_baseline_databases(ei_db_name, ei_db_location)
    ei_db = bw.Database(ei_db_name)

    # Generate the prospective databases using Premise
    scenarios = ["SSP1-Base", "SSP1-PkBudg500"]
    if not all((element in bw.databases.list) for element in scenarios):
        prospective_db = add_prospective_databases(ei_db_name, scenarios=scenarios)

    # Find activity
    activity_name = "photovoltaic slanted-roof installation, 3kWp, multi-Si, laminated, integrated, on roof"
    location = "CH"
    activity = find_activity(database=ei_db, name=activity_name, location=location)

    # Find LCI for each scenario
    df = {}
    df['baseline'] = create_inventory_dataframe(database_name=ei_db_name, process_name=activity_name)
    for scenario in scenarios:
        df[scenario] = create_inventory_dataframe(database_name=prospective_db, process_name=activity) # how to get name of premise db?
    
    pass


if __name__ == "__main__":
    main()
