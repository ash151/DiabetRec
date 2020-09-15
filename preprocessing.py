import numpy as np
import pandas as pd
import requests
import json
import os


def logs_to_macros(input_directory,output_directory,app_id,API_key):
    """
    queries nutritionix API for macronutrient content, using the longer of "meal title" and "meal ingredients," saves results to output_directory
    Arguments:
    input_directory, output_directory, app_id (nutritionix), API_key (nutritionix)
    Returns: dataframe
    """
    app_id = app_id
    API_key = API_key
    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    headers = {'content-type': 'application/json','x-app-id':app_id, 'x-app-key':API_key}
    macros = ['nf_total_carbohydrate', 'nf_protein', 'nf_total_fat', 'nf_calories', 'nf_dietary_fiber']
    aliases = ['carbs','protein','fat','calories','fiber']

    df = pd.read_csv(input_directory)
    user_logs = pd.DataFrame(columns= ['user_id','meal_id','item'] + aliases)
    for i in range(len(df)):
        query_string = max(df.iloc[i]['ingredients'],df.iloc[i]['title'],key=len)
        body = {'query':query_string}
        result = requests.post(url,data=json.dumps(body),headers=headers)
        data = result.json()
        if data.get('foods'):
            for j in range(len(data['foods'])):
                entry = data['foods'][j]
                user_logs.loc[len(user_logs)]= [df.loc[i]['user_id'],df.loc[i]['meal_id']] + [entry[column] for column in ['food_name'] + macros]
        else:
            message = data.get('message')
            if message == 'usage limits exceeded':
                print('API limit exceeded')
                return 0
            user_logs.loc[len(user_logs)] = [df.loc[i]['user_id'],df.loc[i]['meal_id']] + [None for column in ['food_name'] + macros]
    user_logs.to_csv(output_directory)
    return 1

def delete_files(filename='nutritionix_preprocessed.csv'):
    """
    deletes all files in current and subdirectories with filename
    """
    walk = os.walk(os.getcwd())
    for directory,subdirectories,filenames in walk:
        if filename in filenames:
            os.remove(os.path.join(directory,filename))


def merge_files(input_path=None,output_path = None):
    """
    Takes all preprocessed dataframes in one folder and merges them.
    Args:
    input_path: directory to merge CSV files (default: current directory)
    output_path: directory to store output (defualt: current directory with filename "preprocessed_merged.csv")
    """
    cd = os.getcwd()
    if input_path == None: input_path = os.getcwd()
    if output_path == None: output_path = os.path.join(os.getcwd(),"preprocessed_merged.csv")
    result = pd.DataFrame()
    os.chdir(input_path)
    for file in os.listdir():
        df = pd.read_csv(file)
        result = result.append(df,ignore_index=True)
    os.chdir(cd)
    result.to_csv(output_path)

if __name__ == "__main__":
    app_id='xxx-your-app-id-here'
    API_key='xxx-your-api-key-here'
    output_name = 'nutritionix_preprocessed.csv' #name of output files
    for directory,subdirectories,files in os.walk(os.getcwd()):
        if 'mealyzer_data.csv' in files and not output_name in files:
            if logs_to_macros(os.path.join(directory,'mealyzer_data.csv'),os.path.join(directory,output_name),app_id,API_key):
                print('Finished folder {}'.format(directory))
            else:
                print('exiting')
                break
