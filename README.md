# Azure VM Pricing CLI Tool

This tool is designed to help users fetch and display virtual machine SKU prices from a specified source. It provides an interactive CLI interface to select various options like OS/software, category, VM series, VM type, and region to filter the VM pricing data.



## Features

- Fetch virtual machine SKU prices.
- Interactive menus to select OS/software, category, VM series, VM type, and region.
- Display the pricing information in a tabulated format.

## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/emrgcl/AzureVMPricingCLI.git
```

Navigate to the cloned directory:

```bash
cd AzureVMPricingCLI
```

Install the required dependencies:

```bash
pip install -r requirements.txt

```

## Usage

o run the VM Pricing CLI tool, execute the following command in the terminal:

```bash
python azure_vm_pricing_cli.py
```

# Dependencies

- `inquirer`: For creating interactive command-line user interfaces.
- `yaspin`: To display spinners in the CLI for loading processes.
- `tabulate`: To format and display the data in a table.