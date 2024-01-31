import boto3
import json
import pandas as pd
import streamlit as st
import os
import re
import shutil

region = os.environ.get("AWS_DEFAULT_REGION", 'us-west-2')
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name=region)
model = "anthropic.claude-v2:1"

all_categories_file = './src/data/all_categories.txt'
xml_out_format = './src/data/xml_out_format.txt'
prompt_file = './src/prompts/category_generate_prompt.txt'
# output_csv_file = "./output/output_res.csv"
xml_prompt_file = './src/prompts/xml_generate_prompt.txt'
# xml_out_file = './output/xml_output.xml'

st.title("Automating Product Categorization(APC)")

def model_response(prompt, to_replace):
    for key in to_replace:
        prompt = prompt.replace(key, to_replace[key])
    
    body = json.dumps({
        "prompt": "\n\nHuman: " + prompt + "\n\nAssistant:",
        "max_tokens_to_sample": 1000,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "anthropic_version": "bedrock-2023-05-31"
    })

    response = bedrock_runtime.invoke_model(
        body=body,
        contentType="application/json",
        accept="*/*",
        modelId=model
    )
    return json.loads(response['body'].read()).get("completion")

def read_file(file_path):
    with open(file_path) as f:
        data = f.read()
        return data

def get_category(description):

    all_categories = read_file(all_categories_file)
    prompt = read_file(prompt_file)

    to_replace = {
        "<<description>>": description,
        "<<all_categories>>": all_categories
    }
    return model_response(prompt, to_replace)


def filter_res(suggested_category):
    # check if response contains the list
    matches = re.search(r'\[([^\]]+)\]', suggested_category)
    if matches:
        return matches.group(1)

    # split if response has no list
    filter_categories = suggested_category.split(':')
    if len(filter_categories) == 1:
        return filter_categories[0]

    return filter_categories[1]

def generateXml(xml_data):
    outputPath = './output/'
    text_out_file = './output/xml_output.txt'
    xml_prompt = read_file(xml_prompt_file)
    data = f"""
    {xml_data}
    """
    to_replace = {
        "<<xml_data>>": data
    }
    xml_resp =  model_response(xml_prompt, to_replace)
    # st.write(xml_resp)
    start_ind = xml_resp.rindex("xml")
    end_ind = xml_resp.rindex("```")
    xml_resp = xml_resp[start_ind + 3:end_ind]
    # if xml resp is coming inside category-assignments
    if xml_resp.find('<category-assignments>'):
        pattern = r'<category-assignments>(.*?)<\/category-assignments>'
        matches = re.findall(pattern, xml_resp, re.DOTALL)
        if matches:
            xml_resp = matches[0].strip()

    xml_output_format = read_file(xml_out_format)
    xml_output = xml_output_format.replace("<<to_replace_xml>>", xml_resp)

    # Create "output" directory if it does not exists
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    # Save XML response as text
    f = open(text_out_file, "w")
    f.write(xml_output)
    f.close()
    return xml_output

def renameFile(existingFile, renameFile):
    if os.path.exists(renameFile):
        os.remove(renameFile)
        
    if os.path.exists(existingFile):
        os.rename(existingFile, renameFile)

def downloadXML(xml_data):
    final_xml = generateXml(xml_data)

    # download the file
    if final_xml:
        renameFile('./output/xml_output.txt', './output/xml_output.xml')
        with open('./output/xml_output.xml', 'rb') as f:
            st.success("Congratulations! Output file is available to download.")
            st.download_button('Download', f, file_name='xml_output.xml')
            f.close()


def main_fun():

    # upload the csv file
    uploaded_csv_file = st.file_uploader("Choose your file (csv format supported)")

    if uploaded_csv_file is not None:
        # convert to dataframe
        csv_dframe = pd.read_csv(uploaded_csv_file)
        st.subheader("Original data")
        st.write(csv_dframe)

        # read short description and pids from input file
        all_short_descriptions = csv_dframe.loc[:,'shortDescription__default']
        all_pids = csv_dframe.loc[:,'ID']
        all_suggested_categories = []
        xml_data = []
        for index, shortDesc in enumerate(all_short_descriptions):
            suggested_category = get_category(shortDesc)
            # st.write(suggested_category)
            suggested_category = filter_res(suggested_category)

            # if more than one category present , assign the first category
            if ',' in suggested_category:
                suggested_category = suggested_category.split(',')[0]
            tag_data = {
                "category-id": suggested_category,
                "product-id" : all_pids[index]
            }
            xml_data.append(tag_data)
            all_suggested_categories.append(suggested_category)

        csv_dframe['category'] = all_suggested_categories
        st.warning("Processed file")
        st.write(csv_dframe)
        # csv_dframe.to_csv(output_csv_file)

        downloadXML(xml_data)


main_fun()