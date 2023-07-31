### Exports the posts and the users who authored them.
### Separate files are used to assign gender to informants (like 'polish_genders.csv')
### languages are assigned via the Discourse tags (like '#ethno-rebelpop-polska-interviews')
### No need to pseudonomyze, since the corpus already contains pseudonyms
### Run in Python 3 to make use of the encoding argument in the open(file) function

import sys
# replace the path below with the one where you are storing the z_discourse_API_functions module
sys.path.append('/Users/albertocottica/Documents/GitHub/network-viz-for-ssna/code/python scripts/') 

import z_discourse_API_functions as api
import csv
import time

def complete_gender_info(filename):
    '''
    (str) => dict of the form {userid: gender}
    filename.csv contains rows of the form username, gender
    Loads the file; then queries Edgeryders APIs to find the user ID; 
    then builds and returns the dict.
    '''
    print('Retrieving gender info...')
    informants_gender = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader: 
            call = api.baseUrl + 'u/' + row['username'] + '.json'
            ## line above checks that the entry in the genders file
            ## corresponds to an actual account on the forum
            user = api.responses.get(call).json()
            try:
                user_name = user['user']['username']
                informants_gender[user_name] = row['gender']
            except:
                print (call + ' not found.')
    print('Retrieved.')
    return informants_gender

def export_users_posts(tag, genderdict):
    '''
    (str, {'username':'usergender'}) => {'posts':[list of posts], participants:[list of authors]}
    Export:
    1. All posts in all topics associated to tag;
    2. All their authors, with gender. Gender is not stored in the database, and instead
        kept in a separate file and extracted via the function complete_gender_info(filename) 

    '''
    to_return = {'posts':[], 'participants':[]}

    tops = api.fetch_topics_from_tag(tag)
    allPosts = []
    for top in tops:
        topicPosts = api.fetch_posts_in_topic (top)
        for post in topicPosts:
            thisPost = {} # each post of each topic is an item in allPosts. Each item is an edge in the SSN-.
            thisPost['language'] = 'Czech' ## this is new
            thisPost['post_id'] = post['post_id']
            thisPost['post_number'] = post['post_number'] # can be used to rebuild the sequence of posts in the topic
            thisPost['topic_id'] = int(top)
            thisPost['source_username'] = post['username'] # the post's author is the source of the edge.
            thisPost['target_username'] = post ['target_username']
            if 'reply_to_post_id' in post:
                thisPost['reply_to_post_id'] = post['reply_to_post_id']
            else:
                thisPost['reply_to_post_id'] = 1
            ## NOTE! target_username defaults to the creator of the first post in the topic when a user hits the Reply button. 
            ## reply_to_post_id defaults to the ID of the first post in the topic
            ## This means that each first post in a category creates a self-loop in the social network
            thisPost['created_at'] = post['created_at'] # post date 
            thisPost['text'] = post['raw']
            qual_metrics = ['reply_count', 'reads', 'readers_count', 'incoming_link_count', 'quote_count', 'like_count', 'score']
            for qm in qual_metrics:
                thisPost[qm] = post[qm]
##                if qm in post:
##                    thisPost[qm] = post[qm]
##                else:
##                    thisPost[qm] = 0           
            allPosts.append(thisPost)

    ## build a list of participants
    ## since I want also their gender, I need to make it a list of dicts
    participants = []
    for post in allPosts:
        participant = {'username': 'something', 'gender': 'something else'}
        name = post['source_username']
        participant['username'] = name
        participant['gender'] = genderdict[name]
        participant['language'] = 'Polish'
        if participant not in participants:
            participants.append(participant)

    ## remove participants who have not given informed consent to participating in research,
    ## if any. Documentation: https://edgeryders.eu/t/consent-process-manual/11904
    print('The Edgeryders server limits the number of API calls per minute.')
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print('Taking a 30 seconds break, starting at ' + str(current_time))
    time.sleep(30)
    for participant in participants:
        time.sleep(0.2)
        if api.check_consent(participant['username']) == False:
            participants.remove(participant)
            print(participant['username'] + ' removed')
            ## also remove any posts authored by participant
            for post in allPosts:
                if post['source_username'] == participant['username']:
                    allPosts.remove(post)
            
    to_return['posts'] = allPosts
    to_return['participants'] = participants
    return to_return    

def make_pseudonyms_map (genderdict):
    '''
    ([{'username': 'Alice', 'gender':'F'},{...}]) => dict
    The output needs to be {'username':{'pseudo': 'anon1234567', 'gender': 'F'}}
    The input is genderdict, so 
    Associates a pseudonym of the form 'anon' + str(large integer) to each string in names.
    Returns a map from each string to its associated pseudonym  
    '''
    import random
    map = {}
    print(genderdict)
    for key in genderdict:
        pseudo = 'anon' + str(random.getrandbits(32))
        map[key] = {'pseudo': pseudo, 'gender': genderdict[key]['gender']}
    return map

def pseudonymize(data, genderdict_pseudo):
    '''
    ({'posts':[list of posts], participants:[list of authors]},
    {'username':{'pseudo': 'anon123456', 'gender': 'F'}})
    => 
    {'posts':[list of posts], participants:[list of authors]})
    Starts with the output of the export_users_posts(tag) function, and returns the same object, 
    but with all usernames replaced with pseudonyms of the form 'anon' + str(large integer)
    Mentions of the form @username also need to be expunged from the raw text
    This follows Discourse's convention for anonymizing users
    See: https://edgeryders.eu/t/advice-needed-exporting-and-pseudonymizing-ssna-data-for-long-term-storage/12645/2
    '''
    import re # need some Regex support
    pseudonymized_data = {'posts':[], 'participants':[]}

    for post in data['posts']:
        clean_post = {} # initialize a pseudonymized post
        clean_post['post_number'] = post['post_number'] # these five values in the post are not affected by pseudonymization
        clean_post['post_id'] = post['post_id'] 
        clean_post['created_at'] = post['created_at']
        clean_post['topic_id'] = str(post['topic_id']) # remember this had been transformed into int in export_users_posts(tag)
        qual_metrics = ['reply_count', 'reads', 'readers_count', 'incoming_link_count', 'quote_count', 'like_count', 'score']
        for qm in qual_metrics:
            clean_post[qm] = post[qm]
        if 'reply_to_post_id' in post:
            clean_post['reply_to_post_id'] = post['reply_to_post_id']
        else:
            clean_post['reply_to_post_id'] = 1 # by default, a reply is to the first post in the topic           
        clean_text = str(post['text'])
        # remove pictures and replace with a placeholder
        clean_text = re.sub("!\[.{5,}.jpeg\)", "<image here> \n", clean_text)
        # change the code below  to adapt it as in https://edgeryders.eu/t/12645/15
        for name in genderdict_pseudo:
            if post['source_username'] == name:
                clean_post['source_username'] = genderdict_pseudo[name]['pseudo']
            if post['target_username'] == name:
                clean_post['target_username'] = genderdict_pseudo[name]['pseudo']
            # the following takes care of the @mentions
            clean_text = clean_text.replace('@' + name, '@' + genderdict_pseudo[name]['pseudo'])
            # the following takes care of the [quote="username"]
            clean_text = clean_text.replace('[quote="' + name, '[quote="'+ genderdict_pseudo[name]['pseudo'])
            # the following takes care of the /u/username legacy HTML mention
            clean_text = clean_text.replace('/u/' + name, '/u/' + genderdict_pseudo[name]['pseudo'])
            # clean simple mentions meant for human consumption, with no "@":
            # "Like Kate was saying..."
            clean_text = clean_text.replace(name, genderdict_pseudo[name]['pseudo'])
        # last step: clean up mentions of people who are not on this particular convo.
        # so they are not on pseudonym_map.
        # clean @mentions
        clean_text = re.sub("@(?!anon).{3,}", "@anon", clean_text)
        #clean quotes
        clean_text = re.sub('quote="(?!anon).{3,}', 'quote="anon', clean_text)
        # clean /u/username legacy HTML mention
        clean_text = re.sub('\/u\/(?!anon).{3,}', '/u/anon', clean_text)
        # clean up double quote signs ('""'), that appear everywhere
        clean_text = clean_text.replace('""', '"')
        clean_post['text'] = clean_text
        pseudonymized_data['posts'].append(clean_post)
    return pseudonymized_data
            
def write_posts_users(dirPath, pseudonymized_data):
    '''
    (str, {'posts':[list of posts], participants:[list of authors]}) => None
    Writes two CSV files in the allocated dirPath, one for participants and the other for posts
    Remember to pass to this function the pseudonymized data!
    '''                    
    ####    
    # first the posts file. 
    # I want to use the DictWriter class, because each post is a dictionary.
    # I start by building the fieldnames list:
    fieldnames = []
    for key in pseudonymized_data['posts'][0]:
        fieldnames.append(key)
    with open (dirPath + 'posts_czech.csv', 'w', newline='', encoding="utf-8") as postFile:
        postWriter = csv.DictWriter(postFile, fieldnames = fieldnames)
        postWriter.writeheader()
        for post in pseudonymized_data['posts']:
            postWriter.writerow(post)
    # now the participant file.
    fieldnames = []
    for key in pseudonymized_data['participants'][0]:
        fieldnames.append(key)
    with open (dirPath + 'participants_czech.csv', 'w', newline='', encoding="utf-8") as partFile:
        partWriter = csv.DictWriter(partFile, fieldnames = fieldnames)
        partWriter.writeheader()
        for item in pseudonymized_data['participants']:
            partWriter.writerow(item)

def write_anno_codes(anno, codes):
    '''
    (list of dicts, list of dicts => None
    writes into files the annotations and the codes 
    '''
    # annotations. Here I need to add the language
    fieldnames = ['language']
    for key in anno[0]:
        fieldnames.append(key)
    with open (dirPath + 'annotations_czech.csv', 'w', newline='', encoding="utf-8") as annoFile:
        annoWriter = csv.DictWriter(annoFile, fieldnames = fieldnames)
        annoWriter.writeheader()
        for annotation in anno:
            annotation['language'] = 'Czech'
            annoWriter.writerow(annotation)
    # codes:
    fieldnames = []
    for key in codes[0]:
        fieldnames.append(key)
    with open (dirPath + 'codes_czech.csv', 'w', newline='', encoding="utf-8") as codesFile:
        codesWriter = csv.DictWriter(codesFile, fieldnames = fieldnames)
        codesWriter.writeheader()
        for code in codes:
            codesWriter.writerow(code)

    
if __name__ == '__main__':
    greetings = 'Hello world'
    print (greetings)
    ## change the dirPath variable to the directory where you want to store the data
    dirPath = '/Users/albertocottica/Downloads/'
    gendermap =  complete_gender_info(dirPath + 'czech_genders.csv')
    ## change the tag variable to the tag that denotes your project
    tag = 'ethno-rebelpop-czech-interviews'
    success = export_users_posts(tag, gendermap)
##    genderdict_pseudo = make_pseudonyms_map(gendermap)
##    print(genderdict_pseudo)
##    pseudo = pseudonymize(success, genderdict_pseudo)
    writedown = write_posts_users (dirPath, success)
    annos = api.fetch_annos(tag)
    codes = api.fetch_codes_from_annos(annos)
    writedown2 = write_anno_codes(annos, codes)
    print ('The ' + tag + ' corpus has:')
    print (str(len(success['posts'])) + ' posts')
    print (str(len(success['participants'])) + ' participants')
    print (str(len(annos)) + ' annotations')
    print (str(len(codes)) + ' codes')

