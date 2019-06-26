
#Python Packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sk
import re
%matplotlib inline
import seaborn as sns
import wordcloud
import nltk
import yaml 
import sys
import os
#from nltk.tokenize.regexp import RegexpTokenizer
#from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
#from sklearn.cluster import KMeans
#from sklearn.decomposition import PCA
#from sklearn.lda import LDA
#from sklearn.decomposition import LatentDirichletAllocation
#import gensim
#from gensim import corpora
#from nltk.corpus import stopwords 
#from nltk.stem.wordnet import WordNetLemmatizer
#import string
#from nltk.stem.porter import PorterStemmer



#File Names
file_List = ["2017-November.txt","2017-December.txt","2018-January.txt","2018-February.txt" ,"2018-March.txt","2018-April.txt","2018-May.txt","2018-June.txt","2018-July.txt","2018-August.txt","2018-September.txt","2018-October.txt","2018-November.txt","2018-December.txt"]


#Regular expressions to remove unnecessary elements while reading in from CSV files
onHeaderPattern = 'On\s[A-Z{1}][a-z]{4,7}y{1}\s\d{1,2}\s[A-Z]{1}[a-z]{3,8}\s\d{4}\s.*wrote:'
onHeaderPattern2 = 'On\s[A-Z{1}][a-z]{2}\,\s[A-Z]{1}[a-z]{2}\s\d{1,2}\,\s\d{4}\s.*\,\s.*wrote:'
dpdk_termPattern = '(Signed-off-by|Tested-by|Acked-by|Nacked-by|Reviewed-by|Suggested-by|Reported-by)'
amendmentPatternNew = '\s*\d{1,}\s*file[s]*\s*changed\s*\,*\s*\d{1,}\s*(insertion[s]{0,1}|deletion[s]{0,1})'
#not to be used since it does not capture diff which will be later used to cleaning
systempathPattern = '^[\w\d\s\-\_]*\/[\w\d\s\-\_]*\/'
fileInsDelPattern = '.*\/[\w\d\-\_]*\.[a-z]{1,}\s*\|\s*\d{1,}\s*\+*\-*'
#amendmentPattern = '\s*\d{1,}\s*file[s]*\s*changed\,*\s*\d{0,}\s*insertion[s]{0,1}[\(\+\)]*\,*\s*\d{0,}\s*deletion[s]{0,1}\s*[\(\-\)]*'
diffPattern = '^diff\s\-\-git\s{1}.*\.[a-z]{1,}'



#Converts Basic CSV file email conversations into a structured 2 column data frame (Column 1: Sender, Column 2: Message) 
#replace the file name in the line 24 to read in all the files and merge respective dataframes into one single dataframe (can also be done using a for Loop)
#works well to remove indendation in the code 
strn=''
sender_list = list()
msg_list = list()
with open('2018-March.txt', 'r') as fr:
    for line in fr:
        if line[:4] == 'From' and line[4] !=':' and line[-5:-1] == "2018":
            sender_list.append(line)
            if len(strn) > 0:
                msg_list.append(strn)
                strn = ''
        elif line[0] == ">":
            pass
        elif re.search(onHeaderPattern, line):
            pass
        elif re.search(onHeaderPattern2, line):
            pass
        elif re.search(dpdk_termPattern, line):
            pass
        elif re.search(amendmentPatternNew, line):
            pass
        elif (line[:10] != "diff --git") and (re.search(systempathPattern, line)):
            pass
        elif re.search(fileInsDelPattern, line):
            pass
        else:
            strn += line
    msg_list.append(strn)

Mar2018df = pd.DataFrame({'sender':sender_list, 'message': msg_list})




def diffGitRemove1(Series):
    """ Signature 1 to remove the C, Linux and Python script following the "diff --git" element from the e-mail body"""
    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        for i, v in enumerate(newtemp):
            if v[:10] == "diff --git":
                del newtemp[i:]
            newtemp = " ".join(newtemp[:])
            if len(newtemp) == 0:
                newtemp = " ";
                break

        result[j] = newtemp

    return result



def diffGitRemove2(Series):
    """ Signature 2 to remove the C, Linux and Python script following the "diff --git" element from the e-mail body"""
    result = pd.Series(index = Series.index)
    for j,line in enumerate(Series):
        newtemp = line
        with open(newtemp, 'r') as f:
            strn = ""
            for lines in f.readlines():
                if(lines[:10] == "diff --git"):
                    break
                else:
                    strn += lines
            result[j] = strn
    return result



def diffGitRemove3(Series):
    """ Signature 3 to remove the C, Linux and Python script following the "diff --git" element from the e-mail body"""
    result = pd.Series(index = Series.index)
    for j,line in enumerate(Series):
        newtemp = line
        for i,x in enumerate(newtemp):
            if (x[:10] == "diff --git"):
                del newtemp[i:]
                break
        result[j] = newtemp

    return result



def text_list_cleaner(Series):
    """Supportive Function to remove redundant text elements from the E-mail body by breaking down into a list"""
    result = pd.Series(index=Series.index)
    for j,line in enumerate(Series):
        temp_text = line
        for i,x in enumerate(temp_text):
            if x == '\r':
                del temp_text[i]
        result[j] = temp_text

    return result


#The Single consolidated DataFrame is exported as "full_data_2018_clean_reindexed.csv" and read back into python for Analysis
fulldata = pd.read_csv("full_data_2018_clean_reindexed.csv")

#Remove the Unnamed column
fulldata = fulldata.loc[:, ~fulldata.columns.str.contains('^Unnamed')]

#Remove the index column (DF only contains 2 columns Sender and Message)
fulldata = fulldata = fulldata.drop("index", axis = 1)



#All other necessary functions to extract separate email headers
def extract_text(dataObject, row_number):
    """returns text from rows mentioned as row_number from each Body in dataObject"""
    result = pd.Series(index=dataObject.index)
    for r, m in enumerate(dataObject):
        mes_words = m.split('\n')
        del mes_words[:row_number]
        result.iloc[r] = mes_words
    return result

def row_extract(dataObject, row_number):
    """returns the row irrespective whether it is a text or any other email body header"""
    result = pd.Series(index=dataObject.index)
    for r, m in enumerate(dataObject):
        mes_words = m.split('\n')
        mes_words = mes_words[row_number]
        result.iloc[r] = mes_words
    return result

def email_address_extractor(dataframe, dataObject):
    """returns an email address """
    emailRegex = '[\w\.-]+@[\w\.-]+\.\w+'
    address_compile = re.compile(emailRegex)
    all_addresses = []
    email1 = pd.Series(index=dataframe.index)
    email2 = pd.Series(index=dataframe.index)
    email3 = pd.Series(index=dataframe.index)
    for i in range(len(dataframe)):
        for j in dataObject:
            correspondents = re.findall(address_compile, j)
            all_addresses.append(correspondents)
            email1[i] = all_addresses[i][0]
        if col_num >= 2:
            if len(all_addresses[i]) >= 3:
                email2[i] = all_addresses[i][1]
                if col_num == 3:
                    if len(all_addresses[i]) >= 4:
                        email3[i] = all_addresses[i][2]
    return email1, email2, email3

def format_slice(DataFrame, dataObject, str, slice_element):
    """Drop rows if string not in the message"""
    all_rows = []
    for r, m in enumerate(dataObject):
        mes_words = m.split('\n') #splits every new line character
        if string not in mes_words[slice_element]:
            all_rows.append(r)
    DataFrame = DataFrame.drop(DataFrame.index[all_rows])
    return DataFrame


#date \r remover - sample.date
def string_remover(dataObject, to_remove_char):
    """Strips off mentioned character on either ends of the message line"""
    result = pd.Series(index = dataObject.index)
    for r, m in enumerate(dataObject):
        mes_words = m.strip(to_remove_char)
        result.iloc[r] = mes_words 
    return result

=
## Helper functions - working
def textOrPlain_Extract(msg):
    '''Obtain only the text or Plain ASCII content from the email body'''
    headers = []
    for header in msg.walk():
        if header.get_content_type() == 'text/plain':
            headers.append(header.get_payload() )
    return ''.join(parts)





allMessages = list(map(email.message_from_string, fulldata['message']))

fulldata = fulldata.drop('message')

#Get Headers from email object
key = allMessages[0].keys()
for key in keys:
    fulldata[key] = [doc[key] for doc in allMessages]
# Parse content from emails
fulldata['content'] = list(map(get_text_from_email, messages))

fulldata['From'] = fulldata['From'].map(split_email_addresses) #use split email address function to get multiple email addresses present in single email

fulldata['To'] = fulldata['To'].map(split_email_addresses)

fulldata['senders'] = get_row(fulldata.message, 0)

fulldata['date'] = get_row(fulldata.message, 1)

fulldata['subject'] = get_row(fulldata.message, 2)

fulldata['In-Reply_To'] = get_row(fulldata.message, 3)

fulldata['References'] = get_row(fulldata.message, 4)

fulldata['text'] = get_text(fulldata.message, 7)



#remove "Date" text from all the rows in the Date column 
fulldata.date = fulldata.date.str.replace('Date: ', '')

fulldata.date = strremover(fulldata.date, '\r')

fulldata = pd.read_csv("FullData130219.csv")

#Data format incosistency
fulldata["Date"] = fulldata["Date"].str.replace('Wen,', 'Wed,')

#remove "Subject" text from all the rows in the subject column 
fulldata.subject = fulldata.subject.str.replace('Subject: ', '')

#Remove Unnamed column from the data - Read and write using index = True
fulldata = fulldata.loc[:, ~fulldata.columns.str.contains('^Unnamed')]

#converts Date into a format acceptable by Python
fulldata["Date"] = pd.to_datetime(fulldata["Date"])


#input - df["content"] -------output - df["content-split"]  #input content column as series
def text_list_creator(Series):

    result = pd.Series(index=Series.index)
    for j,line in enumerate(Series):
        temp = line.split("\n")
        result[j] = temp

    return result

#Above in the function definition and below is the usage
fulldata["content_split"] = text_list_creator(fulldata["content"])


#input - df["content-split"] -------output - df["content-splitnew"]
def CcodeDiffCharTest4(Series):
    result = pd.Series(index = Series.index)
    for j,line in enumerate(Series):
        newtemp = line
        for i,x in enumerate(newtemp):
            if (x[:10] == "diff --git"):
                del newtemp[i:]
                break
        result[j] = newtemp

    return result

#Above in the function definition and below is the usage
fulldata["content_splitnew"] = CcodeDiffCharTest4(fulldata["content_split"])


#input - df["content-splitnew"] -------output - df["content-splitlatest"]
def StaticRemove(Series):
    result = pd.Series(index = Series.index)
    for j,line in enumerate(Series):
        newtemp = line
        for i,x in enumerate(newtemp):
            if (x[:6] == "static"):
                newtemp[i] = " "
        result[j] = newtemp

    return result

#Above in the function definition and below is the usage
fulldata["content_splitStat"] = StaticRemove(fulldata["content_splitnew"])


def TextJoin(Series):
    result = pd.Series(index = Series.index)
    for j,line in enumerate(Series):
        strn = ""
        newtemp = line
        strn = "".join(newtemp)
        result[j] = strn
    return result

#Above in the function definition and below is the usage
fulldata["clean"] = TextJoin(fulldata["content_splitStat"])

#cleans the list if any element in the list is '\r'
def text_list_cleaner(Series):

    result = pd.Series(index=Series.index)
    for j,line in enumerate(Series):
        temp_text = line
        for i,x in enumerate(temp_text):
            if x == '\r':
                del temp_text[i]
        result[j] = temp_text

    return result

#call it thrice
fulldata["content_split"] = text_list_cleaner(fulldata["content_split"])

fulldata["content_split"] = text_list_cleaner(fulldata["content_split"])

fulldata["content_split"] = text_list_cleaner(fulldata["content_split"])


#To remove empty or null elements in a list
def text_list_cleaner2(Series):

    result = pd.Series(index=Series.index)
    for j,line in enumerate(Series):
        temp_tex = line
        for i,x in enumerate(temp_tex):
            if x == '':
                del temp_tex[i]
        result[j] = temp_tex

    return result

#call it thrice
fulldatajan["content_split"] = text_list_cleaner2(fulldatajan["content_split"])

fulldatajan["content_split"] = text_list_cleaner2(fulldatajan["content_split"])

fulldatajan["content_split"] = text_list_cleaner2(fulldatajan["content_split"])

#Strips off the "\r" from the ends
def text_list_cleaner3(Series):
 
    result = pd.Series(index=Series.index)
    for j,line in enumerate(Series):
        temp_te = line
        for i,x in enumerate(temp_te):
            tempe = x.strip("\r")
            temp_te[i] = tempe
        result[j] = temp_te

    return result


#call it thrice
fulldatajan["content_split"] = text_list_cleaner(fulldatajan["content_split"])

fulldatajan["content_split"] = text_list_cleaner(fulldatajan["content_split"])

fulldatajan["content_split"] = text_list_cleaner(fulldatajan["content_split"])


#function to obtain Acknowledgement (Acked_by)
def SourceAcknowledgementNew(Series):

    result = pd.Series(index = Series.index)
    for j,line in enumerate(Series):
        temp_t = lines
        temp1 = ""
        for i,x in enumerate(temp_t):
            if x[:10] == "Acked-by: ":
                temp1 = x
            else:
                pass
        if len(temp1) == 0:
            temp1 = 'NaN'
        result[j] = temp1

    return result


#"Acked-by: "
sample["Acked-by"] = sample["Acked-by"].str.replace('Acked-by: ', '')

sample["Acked-by"] = sample["Acked-by"].str.replace('Acked-by: ', '')

sample["Acked-by"] = sample["Acked-by"].str.replace('>', '')

sample["Acked-by"] = sample["Acked-by"].str.replace('<', '')


fulldata["Acked-by"] = fulldata["Acked-by"].str.replace('Acked-by: ', '')

fulldata["Acked-by"] = fulldata["Acked-by"].str.replace('>', '')

fulldata["Acked-by"] = fulldata["Acked-by"].str.replace('<', '')


#Extract "Reviewed by" element
def SourceReviewnew(Series):

    result = pd.Series(index = Series.index)
    for j,line in enumerate(Series):
        temp_t = line
        temp1 = ""
        for i,x in enumerate(temp_t):
            if x[:13] == "Reviewed-by: ":
                temp1 = x
            else:
                pass
        if len(temp1) == 0:
            temp1 = 'NaN'
        result[j] = temp1

    return result

#Extract "Reviewed by" element
def SourceNackednew(Series):

    result = pd.Series(index = Series.index)
    for j,line in enumerate(Series):
        temp_t = line
        temp1 = ""
        for i,x in enumerate(temp_t):
            if x[:11] == "Nacked-by: ":
                temp1 = x
            else:
                pass
        if len(temp1) == 0:
            temp1 = 'NaN'
        result[j] = temp1

    return result


#Extract Acknowledger Name
def AckedNameSeparator(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        if len(line) > 3:
            newtemp1 = line.split(" ")
            result[j] = ' '.join([newtemp1[0],newtemp1[1]])
        else:
            result[j] = 'Nan'

    return result


sample["Acked-Name"] = AckedNameSeperator(sample["Acked-by"]) 


#Extract Acknowledger Email
def AckedEmailNewSeparator(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        if len(line) > 3:
            newtemp1 = line.split(" ")
            result[j] = ' '.join(newtemp1[2:])
        else:
            result[j] = 'Nan'

    return result


#cleaning all columns (remove "\r", spaces, "\n" etc)

fulldata["senders"] = spaceremover(fulldata["senders"])

fulldata["senders"] = strremover(fulldata["senders"], '\r')

#remove from:
fulldata["senders"] = fulldata["senders"].str.replace('From: ', '')


#find all the match (regex)
def SenderNameSeparator(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        result[j] = re.findall(r'\((.*?)\)',newtemp)

    return result

#gets the first element from the list
def SenderNameSeparator2(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        result[j] = newtemp[0]

    return result 



dirty_list = ['=?utf-8?B?546L5b+X5YWL?=','=?iso-8859-1?Q?N=E9lio?= Laranjeiro','=?gb18030?B?1ebO0rfnssk=?=','=?iso-8859-1?Q?Ga=EBtan?= Rivet','wei.guo.simon at gmail.com','garwilkie at gmail.com','xiangxia.m.yue at gmail.com','george.dit at gmail.com','akhil.goyal at nxp.com','sodey at rbbn.com','=?utf-8?B?TW9ydGVuIEJyw7hydXA=?=','=?UTF-8?B?UmFmYcWCIEtvemlr?=','=?UTF-8?Q?Micha=C5=82_Krawczyk?=','wang.yong19 at zte.com.cn','=?iso-8859-1?Q?Huertas_Garc=EDa=2C_V=EDctor?=','=?utf-8?B?SHVlcnRhcyBHYXJjw61hLCBWw61jdG9y?=','tom.barbette at uliege.be','zhiyong.yang at intel.com','mvarlese at suse.de','=?UTF-8?q?Mattias=20R=C3=B6nnblom?=','=?UTF-8?Q?Se=c3=a1n_Harte?=','eduser25 at gmail.com','=?UTF-8?Q?Mattias_R=c3=b6nnblom?=','=?UTF-8?Q?Jan_Reme=C5=A1?=','gavin.hu at linaro.org','=?utf-8?B?WmlqaWUgUGFu?=','luca.boccassi at gmail.com','=?UTF-8?B?QmrDtnJuIFTDtnBlbA==?=','=?utf-8?B?WWFvwqBjaHVob25n?=','antonin at barefootnetworks.com','ilia.kurakin at intel.com','thiery.ouattara at outscale.com','=?UTF-8?q?Mattias=20R=C3=B6nnblom?=','=?UTF-8?Q?Mattias_R=c3=b6nnblom?=','wubenqing at ruijie.com.cn','=?utf-8?B?TMOhc3psw7MgVmFka2VydGk=?','=?UTF-8?B?5YiY6L6J?=','=?GBK?B?vajD9w==?=','=?utf-8?B?6IyD5bu65piO?=','robertshearman at gmail.com','=?UTF-8?Q?Wojciech_Wa=C5=9Bko?=','=?iso-8859-1?Q?Mattias_R=F6nnblom?=','=?GBK?B?vajD9w==?=','=?utf-8?B?6IyD5bu65piO?=','subarna.kar at intel.com','nikhil.rao at intel.com','=?UTF-8?B?5LiH5LmQ5Yaw?=','=?ISO-8859-1?B?YmFpIGJha2FyaQ==?=']

clean_list = ['wangzhike','laranjeiro nelio','1534057243 at qq.com','rivet gaetan','wei guo simon','garwilkie','xiangxia','george dit','akhil goyal','sodey','smartsharesystems','semihalf(rk)','semihalf(mk)','wang yong','vhuertas','vhuertas','tom barbette','zhiyong yang','mvarlese','hofors','seanbh','eduser25','hofors','remes','gavin.hu','zijie.pan','luca.boccassi','bjorn topel','ych at panath.cn','antonin','ilia kurakin','thiery ouattara','mattias ronnblom','mattias ronnblom','wubenqing','laszlo vadkerti','h liu','jianmingfan','unknown','robertshearman','wojciech','mattias.ronnblom','jianmingfan','fanjianming','subarna kar','nikhil rao','wanlebing','912873551 at qq.com']

def SenderNameCleanerNew(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        if line in dirty_list:
            ind = dirty_list.index(line)
            tempor = clean_list[ind]
            result[j] = tempor
        else:
            result[j] = line
    return result



def SenderEmailSeperator(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        result[j] = re.findall(r'([^(\)]+)(?:$|\()', newtemp)

    return result


def SenderEmaillistSeperator2(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        result[j] = newtemp[0]

    return result 


fulldata["SendersEmail"] = SenderEmailSeperator(fulldata["senders"])

fulldata["SendersEmail"] = SenderEmaillistSeperator2(fulldata["SendersEmail"])

fulldata["SendersEmail"] = spaceremover(fulldata["SendersEmail"])


#writing to a csv file
fulldata.to_csv('FullDataNew.csv')



fulldatanew["References"] = fulldatanew["References"].str.replace('<', '')

fulldatanew["References"] = fulldatanew["References"].str.replace('>', '')

fulldatanew["In-Reply-To"] = fulldatanew["In-Reply-To"].str.replace('<', '')

fulldatanew["In-Reply-To"] = fulldatanew["In-Reply-To"].str.replace('>', '')

fulldatanew["Message-ID"] = fulldatanew["Message-ID"].str.replace('<', '')

fulldatanew["Message-ID"] = fulldatanew["Message-ID"].str.replace('>', '')



def PlusRemover(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        for i, v in enumerate(newtemp):
            if v[0] == ">":
                del newtemp[i]
            elif v[:4] == "diff" and v[4] == " ":
                del newtemp[i:]
            
        result[j] = newtemp

    return result


def CcodeRemoverforindent5(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        for v in newtemp:
            try:

                if v[0] == ">":
                    newtemp.remove(v)

            except IndexError:
                pass
        result[j] = newtemp

    return result


def emptylistelement(Series):

    result = pd.Series(index = Series.index)
    for j, line in enumerate(Series):
        newtemp = line
        listtemp = []
        for x in range(len(newtemp)):

            if len(newtemp[x]) == 0:
                del newtemp[x]
        result[j] = newtemp

    return result


fulldata["joined"] = fulldata["content_plain"].apply(lambda x: " ".join(x))





