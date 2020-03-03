def simplify_datapackage(dirPath):
    '''
    (str) => 
    compacts the datapackage.json file generated by data.world, found in dirPath
    data.world automatically generates CSV files derived from originally uploaded ones,
    even when the original files are themselves CSV.
    As a consequence, the automatically generated datapackage.json file in data.world
    reports two file resources for each one original file. This script simplifies it,
    so that it documents only the original and not the generated CSV files.
    '''
    import os
    import json
    with open(dirPath + 'datapackage.json', 'r', encoding = 'UTF-8') as json_file:
        data = json.load(json_file)
    os.rename (dirPath + 'datapackage.json', dirPath + 'datapackage.verbose') 

    # enter the project's homepage below:
    homepage = 'https://populism-europe.com/poprebel/'
    data['homepage'] = homepage

    # enter your license below:
    mylicense = 'CC-BY-4.0'
    data['license'] = mylicense

    # remove the 'dwSourceId' fields, unnecessary since I will scrap the "/original" folder
    myresources = data['resources']
    for i in range(4):
        for field in myresources[i]['schema']['fields']:
            field.pop('dwSourceId', None)

    # copy the "description" field from the metadata of files in the "original" folder
    # into those of the "data" folder.
    # also drop the "path" field, because Zenodo dataset saves do not support subdirectories
    for i in range(4):
        myresources[i]['description'] = myresources[i + 4]['description']
        myresources[i].pop('path', None)

    ## finally, drop the items in "resources" referring to the "/original" folder
    del myresources[4:]
    
    ## save the file
    with open (dirPath + 'datapackage.json', 'w', encoding = 'UTF-8') as write_file:
            json.dump(data, write_file)

    return None



if __name__ == '__main__':
    # replace the string below with the directory where you store your datapackage.json
    dirPath = '/Users/albertocottica/Documents/Edgeryders the company/SSNA_data_export/poprebel test folder/haiku66-poprebel-ssn-data/' 
    simplify_datapackage(dirPath)