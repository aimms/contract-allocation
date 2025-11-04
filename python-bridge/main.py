# This script demonstrates integration with an AIMMS optimization model 
# (ContractAllocation.aimms) using the 'aimmspy' Python bridge.
# Source: https://pypi.org/project/aimmspy/

# Technical Notes (for documentation/debugging, removed from core script):
# - AIMMS set/index access requires exact identifier names, preventing typos is key.
# - LoggerConfig.xml output location is the folder of this .py file.
# - Debugging may show a superfluous message: "Superfluous DEBUG: type of 'self.project.aimms_api' is <class 'aimmspy_cpp.AimmsAPI'>"

import time
import pandas as pd
import datetime
import os
import pathlib
import sys

from aimmspy.project.project import DataReturnTypes, Project, AimmsException, AimmsPyException, Model
from aimmspy.utils import find_aimms_path

# --- Setup: Path and Project Initialization   ---

# Get the directory of the current script for relative path resolution.
script_dir = os.path.dirname(os.path.abspath(__file__))
now = datetime.datetime.now()
cwd = os.getcwd()

# Define the root path of the project structure.
projectroot = script_dir.replace("\\python-bridge","") 

print(f"Start: {now} cwd: {cwd}")

# Initialize the AIMMS project connection.
project = Project(
    # Path to the AIMMS Bin folder (required for API connection).
    aimms_path=find_aimms_path("25"),

    # Path to the AIMMS project file to be opened.
    aimms_project_file=os.path.join(projectroot, 'AIMMS-project', 'ContractAllocation.aimms'),

    # The name of the AIMMS set containing all identifiers exposed to Python.
    exposed_identifier_set_name="AllIdentifiers", 

    # Default data type for multi-dimensional data retrieval (Pandas DataFrame is preferred).
    data_type_preference=DataReturnTypes.PANDAS,
    
    # license_url: Fill license URL if using a network license.
)

# Get a reference to the active AIMMS model instance for data transfer and execution.
aimms_model : Model = project.get_model(__file__)

# --- Core Logic ---

def process_allocate_contracts(datainput: str):
    """
    Loads contract and capacity data from an Excel file, assigns it to the AIMMS model,
    executes the optimization procedure (MainExecution), and exports the results.
    """
    
    # Verify the input file exists.
    datainput_path = pathlib.Path(datainput)
    if not datainput_path.exists():
        print(f"Error: File {datainput} does not exist.")
        sys.exit()

    # 1. Load and Assign Producer Data (i_producer, capacities)
    datainput_pd_producer = pd.read_excel(datainput, sheet_name='Producers')

    # Rename columns to match exact AIMMS identifiers for seamless assignment.
    datainput_pd_producer.rename(columns={         
        'Producers'             : 'i_producer',                 
        'Available Capacity'    : 'p_availableCapacity',            
        'Minimal Delivery'      : 'p_minimalDelivery'
        }, inplace=True)

    # Assign data to the corresponding AIMMS identifiers.
    aimms_model.multi_assign(datainput_pd_producer)


    # 2. Load and Assign Contract Data (i_contract, contract limits)
    datainput_pd_contract = pd.read_excel(datainput, sheet_name='Contracts')

    # Rename columns to match exact AIMMS identifiers.
    datainput_pd_contract.rename(columns={                             
        'Contracts'                     : 'i_contract',                 
        'Minimum Contract Size'         : 'p_minimumContractFulfillment',    
        'Maximum Contract Size'         : 'p_maximumContractFulfillment', 
        'Minimal Number of Contributors': 'p_minimalNumberofContributors'
        }, inplace=True)

    # Assign data to the corresponding AIMMS identifiers.
    aimms_model.multi_assign(datainput_pd_contract)

    # 3. Load and Assign Production Cost Data (2D parameter)
    datainput_pd_prodcost = pd.read_excel(datainput, sheet_name='Production Costs')

    # Rename columns to match exact AIMMS identifiers (including index columns).
    datainput_pd_prodcost.rename(columns={              
        'Producers'         : 'i_producer',             
        'Contracts'         : 'i_contract', 
        'Production Cost'   : 'p_productionCost'            
        }, inplace=True)

    # Assign data to the corresponding AIMMS identifier (p_productionCost).
    aimms_model.multi_assign(datainput_pd_prodcost)

    # 4. Execute the AIMMS Optimization
    # Calls the main procedure in AIMMS to solve the optimization problem.
    aimms_model.MainExecution()

    # 5. Retrieve and Prepare Output Data

    # Get the allocation results (i_producer, i_contract, allocation value).
    df_producer_allocation = aimms_model.multi_data(["i_producerExport","i_contractExport","p_generation"])

    # Rename columns for user-friendly export to Excel.
    df_producer_allocation.rename(columns={
        'i_producerExport'  : 'Producer',
        'i_contractExport'  : 'Contract',
        'p_generation'      : 'Generation'
        }, inplace=True)

    # Get the total contract fulfillment results.
    df_contract_allocation = aimms_model.multi_data(["i_contractExport","p_totalGeneration"])

    # Rename columns for user-friendly export to Excel.
    df_contract_allocation.rename(columns={
        'i_contractExport'      : 'Contract',
        'p_totalGeneration'     : 'Total Generation'
        }, inplace=True)

    # 6. Export Results to Excel
    # Determines the output file path by replacing "Data" with "Data_Solution" in the input path.
    excel_file_path = datainput.replace("Data","Data_Solution") 
    
    # Use ExcelWriter to write multiple DataFrames to separate sheets in a single file.
    with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
        df_producer_allocation.to_excel(writer, sheet_name='Allocation per Producer', index=False)
        df_contract_allocation.to_excel(writer, sheet_name='Contract Allocation', index=False)

    
if __name__=="__main__":
    # Define the path to the default input file relative to the project structure.
    datainput = os.path.join(projectroot, 'AIMMS-project', 'DefaultData.xlsx')
    
    # Execute the data processing and optimization.
    process_allocate_contracts(datainput) 
    
    now = datetime.datetime.now()
    print(f"finish: {now} cwd: {cwd}")