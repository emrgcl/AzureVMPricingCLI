from azure_vm_pricing_utility import fetch_virtual_machine_sku_prices,invoke_menu,create_instance_data,get_vm_offer_skus,get_offer_sku
from tabulate import tabulate

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
        for offer_name_raw in offer:
            offer_info=offer_name_raw.split('--')
            offer_name = offer_info[0]
            offer_pricing_type=offer_info[1]
            #print(f"Offer Name: {offer_name}")
            if 'global' not in data['offers'][offer_name]['prices'][offer_pricing_type].keys() :
                region_price = data['offers'][offer_name]['prices'][offer_pricing_type][region].get('value')
                #print(f" Region: {region}, Key:{key}, PricingType: {offer_pricing_type} Price: {region_price} ")
                region_price_list.append({"region":region,"key":key,"pricing_type":offer_pricing_type,"price":region_price})
    

    
table_headers = region_price_list[0].keys()
table_rows = [vs.values() for vs in region_price_list]
print(tabulate(table_rows, headers=table_headers, tablefmt="grid"))
