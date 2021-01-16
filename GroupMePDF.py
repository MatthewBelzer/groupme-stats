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
likeEnd = df.columns.get_loc("Message Like Break")
likeRecEnd= df.columns.get_loc("Like Break Received")
likeGivenEnd = df.columns.get_loc("Like Break Given")
likeRecPercentEnd = df.columns.get_loc("Like Break Received Percent")
likeGivenPercentEnd = df.columns.get_loc("Like Break Given Percent")
dummy = pd.DataFrame(df).to_numpy()

TimeArray = dummy[:,10:timeEnd]
LengthArray = dummy[:,timeEnd+1:lengthEnd]
LikeArray = dummy[:,lengthEnd+1:likeEnd]
LikeRecArray = dummy[:,likeEnd+1:likeRecEnd]
LikeGivenArray = dummy[:,likeRecEnd+1:likeGivenEnd]
LikeRecPercentArray = dummy[:,likeGivenEnd+1:likeRecPercentEnd]
LikeGivenPercentArray = dummy[:,likeRecPercentEnd+1:likeGivenPercentEnd]

Columns = df.columns.values.tolist()
PeopleNameArray = Columns[likeEnd+1:likeRecEnd]

height = len((df))
def AppendArray(length, inputArray, ArrayPosition, i = 0, OutputArray = []):
    while i <= length - 1:
        OutputArray = np.append(OutputArray, inputArray[i][ArrayPosition])
        i+=1
    return OutputArray

names = AppendArray(height, dummy, 0)
posts = AppendArray(height, dummy, 1)
likesReceived = AppendArray(height, dummy, 2)
likesGiven = AppendArray(height, dummy, 3)
likesRatio = AppendArray(height, dummy, 4)
likeAvg = AppendArray(height, dummy, 5)
misspelledWords = AppendArray(height, dummy, 6)
imagesGifs = AppendArray(height, dummy, 7)
kicked = AppendArray(height, dummy, 8)
kickedOthers = AppendArray(height, dummy, 9)

def ArrayTrimmer(array, name, threshold = None, zeroChecker = False):
    #Delete String Values
    deleteArray = []
    i = 0
    while i < len(array):
        try:
            array[i] = float(array[i])
            i+=1
        except:
            deleteArray = np.append(deleteArray, i)
            i+=1
    #Delete Strings
    if len(deleteArray) > 0:
        array = np.delete(array, deleteArray.astype(int))
        name = np.delete(name, deleteArray.astype(int))
    
    #Checks for zeros and deletes them
    if zeroChecker == True:
        deleteArray = []
        i = 0
        while i < len(array):
            if array[i] == 0:
                deleteArray = np.append(deleteArray, int(i))
            i+=1
        
        if len(deleteArray) > 0:
            array = np.delete(array, deleteArray.astype(int))
            name = np.delete(name, deleteArray.astype(int))

    #Delete Things Below the threshold   
    if threshold != None:
        deleteArray = []
        ArrSum = np.sum(array)
        i = 0
        while i < len(array):
            if array[i]/ArrSum < threshold:
                deleteArray = np.append(deleteArray, int(i))
            i+=1
        if len(deleteArray) > 0:
            OtherValue = array[deleteArray.astype(int)].sum()
            array = np.delete(array, deleteArray.astype(int))
            name = np.delete(name, deleteArray.astype(int))
            
            array = np.append(array, OtherValue)
            name = np.append(name, "Other")
            
    
    
    return array, name 



#Finalzing arrays for graphs

updatePost, namePost = ArrayTrimmer(posts, names, .03)
updateRec, nameRec = ArrayTrimmer(likesReceived, names, .03)
updateGiv, nameGiv = ArrayTrimmer(likesGiven, names, .03)
updateImGif, nameImGif = ArrayTrimmer(imagesGifs, names, .03)
updateKicked, nameKicked = ArrayTrimmer(kicked, names, .03)
updateKickedOther, nameKickedOther = ArrayTrimmer(kickedOthers, names, .03)
updateLikeAvg, nameLikeAvg = ArrayTrimmer(likeAvg, names)

#deleting the zeros for it to be flipped
updateLikeRat_Rec_to_Giv, nameLikeRat = ArrayTrimmer(likesRatio, names, zeroChecker = True)

updateLikeRat_Giv_to_Rec = []
for j in updateLikeRat_Rec_to_Giv:
    updateLikeRat_Giv_to_Rec = np.append(updateLikeRat_Giv_to_Rec, j**(-1) )

#Writing pdf file and making graphs
BarMaxWidth = 18

def autolabel(rects, ax):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                str('%f' % float(height))[:6], fontsize=8, ha='center', va='bottom')


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
    while j < divide*(BarMaxWidth-1):
        fig, ax = plt.subplots()
        rects1 = ax.bar(name[j:j+BarMaxWidth], data[j:j+BarMaxWidth], color='g')
        x_pos = [i for i, _ in enumerate(name)]
        fig.set_figheight(8)
        fig.set_figwidth(8)
        plt.title(Title, fontsize=18)
        plt.xlabel(x_label, fontsize=14)
        plt.ylabel(y_label, fontsize=14)
        ax.set_ylim([0,1.1*np.max(data[j:j+BarMaxWidth])])
        plt.xticks(rotation=90)
        plt.bar(height = data[j:j+BarMaxWidth], x = name[j:j+BarMaxWidth], color = 'g')
        autolabel(rects1, ax)
        pdf.savefig(fig) 
        plt.close(fig)
        j+=BarMaxWidth
        
    fig, ax = plt.subplots()
    rects1 = ax.bar(name[j:], data[j:], color='g')
    x_pos = [i for i, _ in enumerate(name)]
    fig.set_figheight(8)
    fig.set_figwidth(8)
    plt.title(Title, fontsize=18)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    ax.set_ylim([0,1.1*np.max(data[j:])])
    plt.xticks(rotation=90)
    plt.bar(height = data[j:], x = name[j:], color = 'g')
    autolabel(rects1, ax)
    pdf.savefig(fig) 
    plt.close(fig)
    
def barSmall(name, data, Title, x_label, y_label):
    fig, ax = plt.subplots()
    rects1 = ax.bar(name, data, color='g')
    x_pos = [i for i, _ in enumerate(name)]
    fig.set_figheight(8)
    fig.set_figwidth(8)
    plt.title(Title, fontsize=18)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    ax.set_ylim([0,1.1*np.max(data)])
    plt.xticks(rotation=90)
    plt.bar(height = data, x = name, color = 'g')
    autolabel(rects1, ax)
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
    firstPage.text(0.5,0.5, "GroupMe Chat Data Visualization", transform=firstPage.transFigure, 
                   ha="center", fontsize = 24)
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
    
    bar(nameLikeAvg, updateLikeAvg, "Average Likes Received", "Name", "Average Likes per Post")
    
    pie_chart("Likes Given", updateGiv, nameGiv)
    
    
    bar(names, likesGiven, "Likes Given", "Users", "Number of Likes Given")
    
    boxplot("Likes Given and Likes Received", "Likes", 
            [likesGiven, likesReceived], ["Likes Given", "Likes Received"],["Likes Given", "Likes Received"])
    
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
    MasterLike = []
    for i in range(0, len(names)):
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
        
        #Cutting Down Like Data
        
        lengthLike = len(LikeArray[i])
        LikeData = []
        for j in range(0, lengthLike):
            if LikeArray[i][j] == "nothingLike":
                break
            LikeData = np.append(LikeData, int(LikeArray[i][j]))
            
        #Likes Received Data
        LikeRecArrayTemp, PeopleNameRecArrayTemp = ArrayTrimmer(LikeRecArray[i], PeopleNameArray, .03)
        BarLikeRecArrayTemp, BarPeopleNameRecArrayTemp = ArrayTrimmer(LikeRecArray[i], PeopleNameArray)
        
        #Likes Given Data 
        LikeGivenArrayTemp, PeopleNameGivenArrayTemp = ArrayTrimmer(LikeGivenArray[i], PeopleNameArray, .03)
        BarLikeGivenArrayTemp, BarPeopleNameGivenArrayTemp = ArrayTrimmer(LikeGivenArray[i], PeopleNameArray)
        
        #Likes Received Percent Data
        LikeRecPercentArrayTemp, PeopleNameRecPercentArrayTemp = \
        ArrayTrimmer(LikeRecPercentArray[i], PeopleNameArray)
        
        #Likes Given Percent Data
        LikeGivenPercentArrayTemp, PeopleNameGivenPercentArrayTemp = \
        ArrayTrimmer(LikeGivenPercentArray[i], PeopleNameArray)
        
        #New Person Page
        Page = plt.figure(figsize=(8, 8))
        Page.clf()
        Page.text(0.5,0.5, names[i] + "'s Message Time Data", transform=firstPage.transFigure
                  , ha="center", fontsize = 24)
        pdf.savefig()
        plt.close()
        Hour(HourData, "Hourly Messaging of " + names[i]) 
        DayGraphs(DayData, "Daily Messaging of " + names[i], 
                  "Total Messaging over Time of " + names[i], 
                  "Weekly Messaging of " + names[i])
        boxplot("Character Length of " + names[i] + "'s Messages", "Character Length", 
                LengthData, ["Length of " + names[i]], Dataframe = False)
        
        boxplot(names[i] + "'s Likes per Message", "Likes per Message", LikeData, 
                ['Likes Per Message of ' + names[i]], Dataframe = False)
        
        #Likes Per User Graphs
        pie_chart("User Breakdown of " +names[i]+ "'s Received Likes", LikeRecArrayTemp, PeopleNameRecArrayTemp)
        bar(BarPeopleNameRecArrayTemp, BarLikeRecArrayTemp, "User Breakdown of " +names[i]+ "'s Received Likes", 
            "names", "Number of Likes Received")
        
        pie_chart("User Breakdown of " +names[i]+ "'s Likes Given Out", LikeGivenArrayTemp, PeopleNameGivenArrayTemp)
        bar(BarPeopleNameGivenArrayTemp, BarLikeGivenArrayTemp, "User Breakdown of " +names[i]+ "'s Likes Given Out", 
            "Names", "Number of Likes Given Out")
        
        bar(PeopleNameRecPercentArrayTemp, LikeRecPercentArrayTemp, 
            "Normalized User Breakdown of\n" +names[i]+ "'s Received Likes", 
            "Names", "Likes Per Post Received")
        
        bar(PeopleNameGivenPercentArrayTemp, LikeGivenPercentArrayTemp, 
            "Normalized User Breakdown of\n" +names[i]+ "'s Likes Given Out", 
            "Names", "Number of Likes Given Out")
        
        
        #Master
        MasterDay = np.append(MasterDay, DayData)
        MasterHour = np.append(MasterHour, HourData)
        MasterLength = np.append(MasterLength, LengthData)
        MasterLike = np.append(MasterLike, LikeData)

    #Sorting
    MasterDay = sorted(MasterDay)
    MasterHour = sorted(MasterHour)
    
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
                MasterLength, ["Group Message Length"], Dataframe = False)
    boxplot("The Group's Likes per Message", "Likes per Message", MasterLike, 
                ["Likes Per Message of the Group"], Dataframe = False)
