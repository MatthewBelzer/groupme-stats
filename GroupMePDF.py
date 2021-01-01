import pandas as pd
import numpy as np
import scipy
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import dates as mdates
from datetime import datetime
import math
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

#Open csv file and turn it into numpy array
csvFile = 'stats.csv'
df = pd.read_csv(csvFile)
df = df.sort_values('Name')
timeEnd = df.columns.get_loc("Message Time-Length Break")
lengthEnd = df.columns.get_loc("Message Length Break")
dummy = pd.DataFrame(df).to_numpy()
TimeArray = dummy[:,10:timeEnd]
LengthArray = dummy[:,timeEnd+1:lengthEnd]

#initialize
names = []
posts = []
likesReceived = []
likesGiven = []
likesRatio = []
likesAvg = []
misspelledWords = []
imagesGifs = []
kicked = []
kickedOthers = []

#make individual arrays for each data set
height = len((df))
i = 0
while i <= height-1:
    names = np.append(names, dummy[i][0])
    posts = np.append(posts, dummy[i][1])
    likesReceived = np.append(likesReceived, dummy[i][2])
    likesGiven = np.append(likesGiven, dummy[i][3])
    likesRatio = np.append(likesRatio, dummy[i][4])
    likesAvg = np.append(likesAvg, dummy[i][5])
    misspelledWords = np.append(misspelledWords, dummy[i][6])
    imagesGifs = np.append(imagesGifs, dummy[i][7])
    kicked = np.append(kicked, dummy[i][8])
    kickedOthers = np.append(kickedOthers, dummy[i][9])
    i+=1
legendCol = round(len(names)/(len(names)**.5))

#ToBeDeleted

deletePosts = []
deleteRec = []
deleteGiv = []
deleteLikeRat = []
deleteImGif = []
deleteKicked = []
deleteKickedOther = []

#Prepares to get rid of strings in the Like Ratio array
i = 0
while i <= height-1:
    try:
        likesRatio[i] = float(likesRatio[i])
        i+=1
    except:
        deleteLikeRat = np.append(deleteLikeRat, i)
        i+=1

#sum everything up for truncating data
sumPosts = np.sum(posts)
sumlikesRec = np.sum(likesReceived) 
sumlikesGiv = np.sum(likesGiven)
sumImGif = np.sum(imagesGifs)
sumKicked = np.sum(kicked)
sumKickedOther = np.sum(kickedOthers)

#Choosing which elements to be removed and consolidated
i = 0
while i <= height-1:
    if posts[i]/sumPosts < .03:
        deletePosts = np.append(deletePosts, int(i))
    if likesReceived[i]/sumlikesRec < .03:
        deleteRec = np.append(deleteRec, int(i))
    if likesGiven[i]/sumlikesGiv < .03:
        deleteGiv = np.append(deleteGiv, int(i))
    if imagesGifs[i]/sumImGif < .03:
        deleteImGif = np.append(deleteImGif, int(i))
    if kicked[i]/sumKicked <= 0:
        deleteKicked = np.append(deleteKicked, int(i))
    if kickedOthers[i]/sumKickedOther <= 0:
        deleteKickedOther = np.append(deleteKickedOther, int(i))
    i+=1
#Find Other Values
deleteKicked = np.array(deleteKicked)
otherPosts = posts[deletePosts.astype(int)].sum()
otherRec = likesReceived[deleteRec.astype(int)].sum()
otherGiv = likesGiven[deleteGiv.astype(int)].sum()
otherImGif = imagesGifs[deleteImGif.astype(int)].sum()
otherKicked = kicked[deleteKicked.astype(int)].sum()
otherKickedOther = kickedOthers[deleteKickedOther.astype(int)].sum()

#Array that updates everything
def updateVal(old, name, deletion, other = None):
    update = np.delete(old, deletion.astype(int))
    updatedName = np.delete(name, deletion.astype(int))
    if other != None:
        update = np.append(update, other)
        updatedName = np.append(updatedName, "Other")
    return [update, updatedName]

#Finalzing arrays for graphs

updatePost, namePost = updateVal(posts, names, deletePosts, otherPosts)
updateRec, nameRec = updateVal(likesReceived, names, deleteRec, otherRec)
updateGiv, nameGiv = updateVal(likesGiven, names, deleteGiv, otherGiv)
updateImGif, nameImGif = updateVal(imagesGifs, names, deleteImGif, otherImGif)
updateKicked, nameKicked = updateVal(kicked, names, deleteKicked)
updateKickedOther, nameKickedOther = updateVal(kickedOthers, names, deleteKickedOther)


updateLikeRat_Rec_to_Giv = np.delete(likesRatio, np.array(deleteLikeRat, dtype=int)).astype(float)

#deleting the zeros for it to be flipped
i = 0
delLikeRatZero = []
while i <= len(updateLikeRat_Rec_to_Giv)-1:
    if updateLikeRat_Rec_to_Giv[i] == 0:
        delLikeRatZero = np.append(delLikeRatZero, i)
    i+=1
    
updateLikeRat_Rec_to_Giv = np.delete(updateLikeRat_Rec_to_Giv, delLikeRatZero)
updateLikeRat_Giv_to_Rec = []
for j in updateLikeRat_Rec_to_Giv:
    updateLikeRat_Giv_to_Rec = np.append(updateLikeRat_Giv_to_Rec, j**(-1) )

deleteLikeRat = np.append(deleteLikeRat, delLikeRatZero)
nameLikeRat = np.delete(names, deleteLikeRat.astype(int))
#Writing pdf file and making graphs
BarMaxWidth = 18

def pie_chart(title, data, info):
    fig = plt.figure(figsize =(8, 8))
    plt.title(title, fontsize=18) 
    plt.pie(data, labels = info, autopct='%1.1f%%')
    pdf.savefig(fig)  
    plt.close(fig)
    
def boxplot(title, y_label, data, column, info=None, Dataframe = True):
    fig = plt.figure(figsize =(8, 8))
    plt.title(title, fontsize=18)
    plt.ylabel(y_label, fontsize=14)
    if info == None:
        plt.boxplot(data)
    else:
        plt.boxplot(data, labels = info)
    
    pdf.savefig(fig)
    plt.close(fig)
    
    #Write Stats
    if Dataframe == True:
        for i in range(0, len(column)):
            Page = plt.figure(figsize=(8, 8))
            Page.clf()
            describe = str( df[column[i]].describe() )
            Page.text(0.5,0.5, column[i] + "\n" + describe, transform=Page.transFigure, size=24, ha="center")
            pdf.savefig()
            plt.close()
    else:
        for i in range(0, len(column)):
            TempDataframe = pd.DataFrame(data = data, columns = [column[i]])
            Page = plt.figure(figsize=(8, 8))
            Page.clf()
            describe = str( TempDataframe[column[i]].describe() )
            Page.text(0.5,0.5, column[i] + "\n" + describe, transform=Page.transFigure, size=24, ha="center")
            pdf.savefig()
            plt.close()
        
def bar(name, data, Title, x_label, y_label):
    divide = math.floor(len(name)/BarMaxWidth)
    j = 0
    while j <= divide*(BarMaxWidth-1) - 1:
        fig = plt.figure(figsize =(8, 8))
        plt.title(Title, fontsize=18)
        plt.xlabel(x_label, fontsize=14)
        plt.ylabel(y_label, fontsize=14)
        plt.xticks(rotation=90)
        plt.bar(height = data[j:j+BarMaxWidth], x = name[j:j+BarMaxWidth], color = 'g')
        pdf.savefig(fig) 
        plt.close(fig)
        j+=BarMaxWidth
        
    fig = plt.figure(figsize =(8, 8))
    plt.title(Title, fontsize=18)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.xticks(rotation=90)
    plt.bar(height = data[j:], x = name[j:], color = 'g')
    pdf.savefig(fig) 
    plt.close(fig)
    
def barSmall(name, data, Title, x_label, y_label):
    fig = plt.figure(figsize =(8, 8))
    plt.title(Title, fontsize=18)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.xticks(rotation=90)
    plt.bar(height = data, x = name, color = 'g')
    pdf.savefig(fig)
    plt.close(fig)
    
def Hour(array, Title):
    rcParams.update({'figure.autolayout': True})
    plt.rc('xtick', labelsize=12) 
    plt.rc('ytick', labelsize=12) 
    Last = None
    Label = []
    HourMsg = []
    holder = None
    for j in array:
        if j == Last:
            holder +=1
        elif holder ==None:
            Label = j
            holder = 1
        else:
            HourMsg = np.append(HourMsg,holder)
            Label = np.append(Label,j)
            holder = 1
        Last = j
    HourMsg = np.append(HourMsg,holder)
    fig = plt.figure(figsize =(8, 8))
    plt.title(Title + ' in UTC', fontsize=20)
    plt.xlabel("Hour (UTC)", fontsize=16)
    axes = plt.gca()
    axes.set_ylim([0,1.4*np.max(HourMsg)])
    plt.ylabel("Number of Messages", fontsize=16)
    fig.text(.2, .8,
             "MIT: -11      HST: -10      AST: -9       PST: -8      PNT: -7      MST: -7\n"
             "CST: -6       EST: -5         IET: -5        PRT: -4      CNT: -3.5   AGT: -3\n"
             "BET: -3       CAT: -1        ECT: +1      EET: +2     ART: +2   EAT: +2\n"
             "MET: +3.5  NET: +4       PLT: +5      IST: +5.5    BST: +6   VST: +7\n"
             "CTT: +8      JST: +9        ACT: +9.5  AET: +10    SST +11   NST:+12"
             ,bbox={'facecolor': 'lightgrey'}, fontsize=12)
    plt.bar(height = HourMsg, x = Label, color = 'b')
    pdf.savefig(fig)
    plt.close(fig)
    
def DayGraphs(array, TitleChange, TitleTotal, TitleWeek):
    rcParams.update({'figure.autolayout': True})
    plt.rc('xtick', labelsize=12) 
    plt.rc('ytick', labelsize=12)
    Last = None
    ChangeDates = []
    Week = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
    Occurance = np.zeros(7)
    n=0
    i = 0
    for j in array:
        #Change Plots
        DateTemp = datetime(int(j[:4]), int(j[5:7]), int(j[8:10]))
        ChangeDates = np.append(ChangeDates, DateTemp)
        #Total Plots
        if j == Last:
            yTotal[n] = yTotal[n]+1

        elif Last == None:
            Date = [ChangeDates[i]]
            yTotal = [1]
            
        else:
            Date = np.append(Date, ChangeDates[i])
            yTotal = np.append(yTotal, yTotal[n]+1)
            n+=1
            
        #Weekday Plots
        Day = DateTemp.weekday()
        Occurance[Day] = Occurance[Day] + 1
    
        Last = j
        i += 1
        

    #Setting up Day of the Week Plot
    fig = plt.figure(figsize =(8, 8))
    plt.title(TitleWeek + ' in UTC', fontsize=18)
    plt.xlabel("Day of the Week", fontsize=14)
    plt.ylabel("Number of Messages", fontsize=14)
    plt.bar(height = Occurance, x = Week, color = 'g')
    pdf.savefig(fig)
    plt.close(fig)
    
    #Setting up Change Plot
    length = len(ChangeDates)
    fig, ax = plt.subplots()
    fig.set_figheight(8)
    fig.set_figwidth(8)
    plt.title(TitleChange + ' in UTC', fontsize=20)
    plt.xlabel("Date (Year - Month - Date) (UTC)", fontsize=16)
    plt.ylabel("Number of Messages", fontsize=16)
    fig.autofmt_xdate()
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.hist(ChangeDates, bins = math.floor(len(ChangeDates)**(.4)))
    pdf.savefig(fig)
    plt.close(fig)

    #Setting up Total Plot
    fig, ax = plt.subplots()
    fig.set_figheight(8)
    fig.set_figwidth(8)
    plt.title(TitleTotal + ' in UTC', fontsize=20)
    plt.xlabel("Date (Year - Month - Date) (UTC)", fontsize=16)
    plt.ylabel("Number of Messages", fontsize=16)
    fig.autofmt_xdate()
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    if len(Date) < 2:
        plt.plot_date(Date, yTotal, linestyle = 'solid', ms = 3)
    else:
        plt.plot_date(Date, yTotal, linestyle = 'solid', marker = None)
    pdf.savefig(fig)
    plt.close(fig)
    

with PdfPages('graph.pdf') as pdf:
    #Cover Page
    
    firstPage = plt.figure(figsize=(8, 8))
    firstPage.clf()
    firstPage.text(0.5,0.5, "GroupMe Chat Data Visualization", transform=firstPage.transFigure, ha="center", fontsize = 24)
    pdf.savefig()
    plt.close()

    
    #Post Graphs
    #Cover Page
    
    Page = plt.figure(figsize=(8, 8))
    Page.clf()
    Page.text(0.5,0.5, "Post Data", transform=firstPage.transFigure, ha="center", fontsize = 24)
    pdf.savefig()
    plt.close()

    
    pie_chart("Posts", updatePost, namePost)
    
    bar(names, posts, "Posts", "Users", "Post Count")
    
    boxplot("Posts", "Post Count", posts, ["Posts"])
    
    
    #Likes
    Page = plt.figure(figsize=(8, 8))
    Page.clf()
    Page.text(0.5,0.5, "Likes Data", transform=firstPage.transFigure, ha="center", fontsize = 24)
    pdf.savefig()
    plt.close()
    
    pie_chart("Likes Received", updateRec, nameRec)
    
    bar(names, likesReceived, "Likes Received", "Users", "Number of Likes Received")
    
    pie_chart("Likes Given", updateGiv, nameGiv)
    
    
    bar(names, likesGiven, "Likes Given", "Users", "Number of Likes Given")
    
    boxplot("Likes Given and Likes Received", "Likes", 
            [likesGiven, likesReceived], ["Likes Given", "Likes Recieved"],["Likes Given", "Likes Recieved"])
    
    bar(nameLikeRat, updateLikeRat_Rec_to_Giv, "Likes Received to Given Ratio", "Users", "Ratio")

    bar(nameLikeRat, updateLikeRat_Giv_to_Rec, "Likes Given to Received Ratio", "Users", "Ratio")
    
    #Images and Gifs
    Page = plt.figure(figsize=(8, 8))
    Page.clf()
    Page.text(0.5,0.5, "Images and Gifs Data", transform=firstPage.transFigure, ha="center", fontsize = 24)
    pdf.savefig()
    plt.close()
    
    pie_chart("Posts of Images and Gifs", updateImGif, nameImGif)
    
    bar(names, imagesGifs, "Posts of Images and Gifs", "Users", "Number of Posts of Images and Gifs")

    boxplot("Posts of Images and Gifs", "Number of Posts of Images and Gifs", 
            imagesGifs, ["Images and Gifs"])

    #Kicking
    Page = plt.figure(figsize=(8, 8))
    Page.clf()
    Page.text(0.5,0.5, "Kicking Data", transform=firstPage.transFigure, ha="center", fontsize = 24)
    pdf.savefig()
    plt.close()
    
    pie_chart("Kicked by Others", updateKicked, nameKicked)    

    barSmall(nameKicked, updateKicked, "Kicked by Others", "Users", "Number of Times Kicked by Others")
    
    pie_chart("Kicked Other People", updateKickedOther, nameKickedOther)

    barSmall(nameKickedOther, updateKickedOther, "Kicked Other People", "Users", "Number of Times Kicked Other People")
    
    
    #General Message Data
    Page = plt.figure(figsize=(8, 8))
    Page.clf()
    Page.text(0.5,0.5, "Message Time Data", transform=firstPage.transFigure, ha="center", fontsize = 24)
    pdf.savefig()
    plt.close()
    
    MasterDay = []
    MasterHour = []
    MasterLength = []
    for i in range(0, len(TimeArray)):
        DayData = []
        HourData = []
        timeLength = len(TimeArray[i])
        #Cutting Down Time Array
        for j in range(0, timeLength):
            if TimeArray[i][j] == "nothingTime":
                break
            value = TimeArray[i][j]
            DayData = np.append(DayData, value[:10])
            HourData = np.append(HourData, value[11:13])
        DayData = sorted(DayData)
        HourData = sorted(HourData)
        #Cutting Down Length Array
        lengthLength = len(LengthArray[i])
        LengthData = []
        for j in range(0, lengthLength):
            if LengthArray[i][j] == "nothingLength":
                    break
            LengthData = np.append(LengthData, int(LengthArray[i][j]))
        
        LengthData = sorted(LengthData) 
        
        #New Person Page
        Page = plt.figure(figsize=(8, 8))
        Page.clf()
        Page.text(0.5,0.5, names[i] + "'s Message Time Data", transform=firstPage.transFigure, ha="center", fontsize = 24)
        pdf.savefig()
        plt.close()
        Hour(HourData, "Hourly Messaging of " + names[i]) 
        DayGraphs(DayData, "Daily Messaging of " + names[i], 
                  "Total Messaging over Time of " + names[i], 
                  "Weekly Messaging of " + names[i])
        boxplot("Character Length of " + names[i] + "'s Messages", "Character Length", 
                LengthData, ["Length"], Dataframe = False)
        
        
        #Master
        MasterDay = np.append(MasterDay, DayData)
        MasterHour = np.append(MasterHour, HourData)
        MasterLength = np.append(MasterLength, LengthData)
    
    #Sorting
    MasterDay = sorted(MasterDay)
    MasterHour = sorted(MasterHour)
    MasterLength = sorted(MasterLength)
    
    Page = plt.figure(figsize=(8, 8))
    Page.clf()
    Page.text(0.5,0.5, "Group Message Time Data", transform=firstPage.transFigure, ha="center", fontsize = 24)
    pdf.savefig()
    plt.close()
    Hour(MasterHour, "Total Hourly Messaging")
    DayGraphs(MasterDay, "Daily Messaging of the Group Chat", 
            "Total Messaging of the Group Chat over Time", 
            "Weekly Messaging of the Group Chat")
    boxplot("Character Length of Group's Messages", "Character Length", 
                MasterLength, ["Length"], Dataframe = False)