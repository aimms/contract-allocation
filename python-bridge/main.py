# This is a sample Python script.
# The purpose of this script is to demo the aimmspy Python bridge,
# see https://pypi.org/project/aimmspy/

# Remarks: 
# - an element not in the set that is the range of parameter - difficult to find the typo.
# + LoggerConfig.xml output opened in folder of .py file.
# - Superfluous DEBUG: type of 'self.project.aimms_api' is <class 'aimmspy_cpp.AimmsAPI'>

import time
import pandas as pd
import datetime
import os
import pathlib
import sys

from aimmspy.project.project import DataReturnTypes, Project, AimmsException, AimmsPyException, Model
from aimmspy.utils import find_aimms_path


# # Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Change the current working directory to the script's directory
# os.chdir(script_dir)
now = datetime.datetime.now()
cwd = os.getcwd()

projectroot=script_dir.replace("\\python-bridge","") 

# Initialize required paths.
print(f"Start: {now} cwd: {cwd}")


# Initialize the AIMMS project
project = Project(
    # path to the AIMMS Bin folder (on linux the Lib folder)
    aimms_path=find_aimms_path("25"),

    # path to the AIMMS project file
    aimms_project_file=os.path.join('..', 'AIMMS-project', 'ContractAllocation.aimms'),

    # the name of an aimms set containing identifiers. 
    exposed_identifier_set_name="AllIdentifiers",  # Limit access to specific identifiers,

    # default data type when retrieving multi-dimensional data
    data_type_preference=DataReturnTypes.PANDAS,
    
)

aimms_model : Model = project.get_model(__file__)

def process_vessel_schedule( datainput: str ):
    # Determine the input file.
    datainput_path = pathlib.Path(datainput)
    if not datainput_path.exists():
        print(f"File {datainput} does not exist.")
        sys.exit()

    # Read Excel sheet:
    datainput_pd_producer = pd.read_excel(datainput,sheet_name='Producers')

    # Rename the columns to AIMMS identifiers:
    datainput_pd_producer.rename(columns={        
        'Producers'             : 'i_producer',                 
        'Available Capacity'    : 'p_availableCapacity',            
        'Minimal Delivery'      : 'p_minimalDelivery'
        }, inplace=True)

    # Actually assign to AIMMS identifiers:
    aimms_model.multi_assign(datainput_pd_producer)


    # Read Excel sheet:
    datainput_pd_contract=pd.read_excel(datainput,sheet_name='Contracts')

    # Rename the columns to AIMMS identifiers:
    datainput_pd_contract.rename(columns={                     
        'Contracts'                     : 'i_contract',                 
        'Minimum Contract Size'         : 'p_minimumContractFulfillment',    
        'Maximum Contract Size'         : 'p_maximumContractFulfillment', 
        'Minimal Number of Contributors': 'p_minimalNumberofContributors'
        }, inplace=True)

    # Actually assign to AIMMS identifiers:
    aimms_model.multi_assign(datainput_pd_contract)

    # Read Excel sheet:
    datainput_pd_prodcost=pd.read_excel(datainput,sheet_name='Production Costs')

    # Rename the columns to AIMMS identifiers:
    datainput_pd_prodcost.rename(columns={              
        'Producers'         : 'i_producer',                
        'Contracts'         : 'i_contract',   
        'Production Cost'   : 'p_productionCost'            
        }, inplace=True)

    # Actually assign to AIMMS identifiers:
    aimms_model.multi_assign(datainput_pd_prodcost)


    # Execute the optimization logic.
    aimms_model.MainExecution()



    # Getting data from AIMMS model:
    df_producer_allocation = aimms_model.multi_data(["i_producerExport","i_contractExport","p_generation"])

    # Renaming columns Vessel overview for Excel Sheet:
    df_producer_allocation.rename(columns={
        'i_producerExport'  : 'Producer',
        'i_contractExport'  : 'Contract',
        'p_generation'      : 'Generation'
        },inplace=True)



    # Getting data from AIMMS model:
    df_contract_allocation = aimms_model.multi_data(["i_contractExport","p_totalGeneration"])

    # Renaming columns Cargo overview for Excel Sheet:
    df_contract_allocation.rename(columns={
        'i_contractExport'      : 'Contract',
        'p_totalGeneration'     : 'Total Generation'
        },inplace=True)


    # Exporting the three data frames each to a separate sheet:
    excel_file_path = datainput.replace("Data","Data_Solution")
    with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
        df_producer_allocation.to_excel(writer, sheet_name='Allocation per Producer', index=False)
        df_contract_allocation.to_excel( writer, sheet_name='Contract Allocation',  index=False)

    
if __name__=="__main__":
    datainput=os.path.join(projectroot,'AIMMS-project', 'DefaultData.xlsx')
    process_vessel_schedule(datainput)
    now = datetime.datetime.now()
    print(f"finish: {now} cwd: {cwd}")
