
import json
import urllib.request as request
import inquirer
import yaspin

@yaspin.yaspin(text="Fetching Azure VM SKUs")
def fetch_virtual_machine_sku_prices(virtual_machine_calculator_api='https://azure.microsoft.com/api/v3/pricing/virtual-machines/calculator/?culture=en-us&currency=$currency'):
        try:
            response=request.urlopen(virtual_machine_calculator_api)
            data = response.read()
            jsondata = json.loads(data)
            return jsondata
        except Exception as e:
            print(f"Error occurred while fetching virtual machine prices: {e}")

def invoke_menu(menu_data, display_name_fallback,message_item,menu_type='list'):
     
     choices = [(md.get('displayName',display_name_fallback),md['slug'])  for md in menu_data]
     question_type = inquirer.List if menu_type.lower() == 'list' else inquirer.Checkbox
     questions = [
            question_type('selected_item', message=f"Please select {message_item}", choices=choices),
    ]
     answers = inquirer.prompt(questions)
     return answers['selected_item']
def create_sku_string(os_software_selection,instance_selection):
    sku=f"{'windows' if os_software_selection == 'windows-os' else os_software_selection}-{instance_selection}-standard"
    return sku
def create_spec_display_string(os_software_selection,instance_selection,data):
     sku=create_sku_string(os_software_selection,instance_selection)
     offer=get_offer_sku(sku,data,'payg')
     size_display_items = [item for item in data['sizesPayGo'] if item['slug'] == instance_selection]
     size_display = size_display_items[0]['displayName']
     #offer=data['offers'][offer_sku]
     return f"Size: {size_display} Cpu: {offer['cores']} Cores, Ram: {offer['ram']} GB, Disk: {offer['diskSize']} GB"
def create_instance_data(instance_data,os_software_selection,data):
     updated_data = [{'slug': item['slug'], 'displayName': create_spec_display_string(os_software_selection,item['slug'],data)} for item in instance_data]
     return updated_data
def get_offer_sku(sku,data,plan,return_string=False):
    sku_items = data['skus'][sku][plan]
    sku_items_corrected = [element.split('--')[0] for element in sku_items]

    for sku in sku_items_corrected:
        # Iterate over each offer in the data
        offer = data['offers'][sku]
        #print(f"getting sku for{offer}")
        # Check if the SKU is in the current offer and if 'global' key is not present
        if 'global' not in offer['prices']['perhour'].keys() :
            if return_string:
                return data['offers'][sku]
            return offer
def get_vm_offer_skus(data,sku):
    return data['skus'][sku]
if __name__ == "__main__":
    print("This script is intended to be imported and used by vm_pricing_cli.py, not run directly.")
