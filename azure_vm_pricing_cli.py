import json
import urllib.request as request
import inquirer
import yaspin
from tabulate import tabulate
from colorama import init, Fore, Style

@yaspin.yaspin(text="Fetching Azure VM SKUs")
def fetch_virtual_machine_sku_prices(virtual_machine_calculator_api='https://azure.microsoft.com/api/v3/pricing/virtual-machines/calculator/?culture=en-us&currency=$currency'):
        try:
            response=request.urlopen(virtual_machine_calculator_api)
            data = response.read()
            jsondata = json.loads(data)
            return jsondata
        except Exception as e:
            print(f"Error occurred while fetching virtual machine prices: {e}")
def ensure_selection(func):
    def wrapper(*args, **kwargs):
        # Ensure the decorator only enforces selection for checkbox menus
        if 'checkbox' in args:
            while True:
                answers = func(*args, **kwargs)
                if answers:
                    return answers
                print(Fore.RED, "Please select at least one option.\n" + Style.RESET_ALL)
        else:
            # For list menus, just call the function once
            return func(*args, **kwargs)
    return wrapper
@ensure_selection
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
     disk_size = offer.get('diskSize',0)
     return f"Size: {size_display} Cpu: {offer['cores']} Cores, Ram: {offer['ram']} GB, Disk: {disk_size} GB"
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

def main():
    # initialize colorama
    init()
    # fetch data from the Azure VM pricing API
    data = fetch_virtual_machine_sku_prices()
    software_licenses = data['softwareLicenses']

    os_software_selection=invoke_menu(software_licenses, 'Windows','OS/Software')
    categories= data['dropdown']

    category_selection=invoke_menu(categories, 'all','Category')

    vm_series_info = [c for c in categories if c.get('slug') == category_selection][0]
    vm_series = vm_series_info['series']

    vm_series_selection=invoke_menu(vm_series, 'all','VM Series')
    vm_serie = [vs for vs in vm_series if vs.get('slug') == vm_series_selection][0]

    instances = vm_serie['instances']

    updated_instances = create_instance_data(instances,os_software_selection,data)

    instance_selection = invoke_menu(updated_instances, 'all','VM Type')

    sku=f"{'windows' if os_software_selection == 'windows-os' else os_software_selection}-{instance_selection}-standard"
    print(f"Selected SKU: {sku}")
    region_price_list=[]
    regions = data['regions']
    region_selection=invoke_menu(regions, 'all','Region','checkbox')
    print(f"Selected Regions: {region_selection}")
    offer_skus = get_vm_offer_skus(data,sku)
    offer_sku_keys = offer_skus.keys()
    for region in region_selection:
        for key in offer_sku_keys:
            offer=offer_skus[key]
            region_price=0
            for offer_name_raw in offer:
                offer_info=offer_name_raw.split('--')
                offer_name = offer_info[0]
                offer_pricing_type=offer_info[1]
                region_exists = data['offers'][offer_name]['prices'][offer_pricing_type].get(region)
                #print(f"Offer Name: {offer_name}")
                if 'global' in data['offers'][offer_name]['prices'][offer_pricing_type].keys() and region_exists:
                    region_price += data['offers'][offer_name]['prices'][offer_pricing_type]['global'].get('value')
                else:
                    try:                     
                        region_price += data['offers'][offer_name]['prices'][offer_pricing_type].get(region).get('value')
                    except:
                        #region ha no price
                        region_price += 0
            region_price_list.append({"region":region,"key":key,"pricing_type":offer_pricing_type,"hourly_price":region_price,"monthly_price":region_price*730})      
    table_headers = region_price_list[0].keys()
    table_rows = [vs.values() for vs in region_price_list]
    print(tabulate(table_rows, headers=table_headers, tablefmt="grid"))

if __name__ == "__main__":
    main()