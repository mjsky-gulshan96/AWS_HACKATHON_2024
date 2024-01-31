# Automating Product Categorization(APC)
A repo for a `Automating Product Categorization(APC)` which we are using to help Merchant to identify the right catagory for the products with AI recommendations. `Amazon Badrock Anthropic Claude` is used to make it work.

# Prequisites
Create a text file with Merchant specific category IDs.
Place the text file following the path mentioned here.  
>`path: "src/data/all_categories.txt`

Amazon Badrock Anthropic Claude (ID: anthropic.claude-v2:1) Model access within AWS account.

## How to run the application locally
1. Install the required packages for this application with `pip install -r requirements.txt`. To avoid conflicts with existing python dependencies:   
  `$pip3 install -r requirements.txt` 

2. You will need a Amazon Badrock Anthropic Claude (ID: anthropic.claude-v2:1) Model access in your account. If you don't have, please take access through your administrator to use this.
3. Run the app with `python -m streamlit run src/index.py`
4. Upload product information list(Supported Format .CSV)
5. Make sure to have correct headings with in CSV file like `ID, name__default,shortDescription__default` 
6. You can download the output file in XML format.
7. The schema used for generating XML can be changed as required in the file
>`Path: src/data/xml_out_format.txt`. 
8. Download the XML file. 
9. upload the same XML in your system.
