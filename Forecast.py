import matplotlib.pyplot as plt
import datetime
import requests


"""
This class will make the DarkSky request, and have as member variable the response
"""
class ApiRequest:

    """
    Requires: Nothing.
    Modifies: Self.
    Effects: Makes the Dark Sky call and sets the member variables.
    """
    def __init__(self):
        self.key = "2fecc76215ad344d79970e5a78e94f84"
        self.currentDate = datetime.datetime.today()
        self.apiCall = "https://api.darksky.net/forecast/"
        #coordinates = Cuajimalpa
        #request has to be in format https://api.darksky.net/forecast/[key]/[latitude],[longitude]
        #excluding several blocks to reduce latency. Extending the hourly request from 48 to 168 hours
        self.optionalParams = "?exclude=currently,minutely,alerts,flags&extend=hourly"
        self.location = {"latitude": "18.9261000", "longitude": "-99.2307500", "cluster": "Cuernavaca"}
        self.response = requests.get(self.apiCall + self.key + "/" + self.location["latitude"] + "," + self.location["longitude"] + self.optionalParams)
        #this Dict has format [time : temperature] with time as YYYY-MM-DD HH:MM:SS
        self.next168Hours = {}
        self.forecast()

    """
    Requires: Nothing
    Modifies: next168Hours
    Effects: fills the next168Hours as [time : temperature] (in F°, but is converted to C° with tempConverter)
    """

    def forecast(self):
        # DarkSky forecast request returns either an hourly forecast for next 48 hours, minutely for the next day or
        # day by day for the next week
        # used a optional param in the request to get the forecast hourly for next 168 hours
        data = self.response.json()
        hourly = data["hourly"]
        data = hourly["data"]
        for i in range(168):
            hourData = data[i]
            self.next168Hours[convertTime(hourData["time"])] = tempConverter(hourData["temperature"])

    """
    TEST FUNCTION
    """
    def TESTRounding(self):
        testFile = open("testFile.txt","w")
        data = self.response.json()
        hourly = data["hourly"]
        data = hourly["data"]
        testDict = {}
        tempByHour = {}
        for i in range(168):
            hourData = data[i]
            testDict[convertTime(hourData["time"])] = tempConverter(hourData["temperature"])

        # write to file the dictionary with every hour : temp
        for key in testDict:
            testFile.write(str(key) + ": ")
            testFile.write(str(testDict[key]) + "\n")

        # Fill temp by hour with all hours as keys (0-24)
        for key in testDict:
            timeKey = splitDate(key)
            tempByHour[timeKey] = 0

        total = 0
        # add to a specific hour all the temperatures associated with that hour
        for hourKey in tempByHour:
            for dateKey in testDict:
                #looks through all the days, thus there are multiple instances of the same hour.
                if(splitDate(dateKey) == hourKey):
                    tempByHour[hourKey] += testDict[dateKey]

        #gets the average for 16:00
        for key in tempByHour:
            if (key == "16:00"):
                total += tempByHour[key]

       print("TEMPERATURES AT 16:00 FOR THE NEXT 7 DAYS")
       for key in testDict:
            if("16:00" in key):
                # temperatures for 16:00
                print("***" + str(testDict[key]))

        avg = total / 7
        print("AVG:")
        print(avg)






class Prediction():
    """
    Requires: a valid ApiRequest instance
    Modifies: nothing
    Effects: initializes member dictionary with all the keys, and makes all the calls to the member functions that do
            most of the setup
    """
    def __init__(self,apiRequest):
        #simply a copy of the dictionary containing the hourly temperature for the next 168 hours (2 weeks)
        self.next2WeeksTemp = apiRequest.next168Hours
        # Dictionary which contains 24 hours of the day as keys, and as values has the average temperature for that hour
        # averaged from the values in next2WeeksTemp
        self.averageTempByHour = {}
        self.fillTime()
        self.calcAveragePerHour()
        # A list containing only the hour values of the averageTempByHour dictionary
        self.hourArray = []
        # A list containing only the temperature values contained in the averageTempByHour dictionary
        self.avgTempArray = []
        self.fillArrays()


    """
    Requires: nothing
    Modifies: nothing
    Effects: fills the averageTempByHour with all keys (hours) and sets default temp to 0
    """
    def fillTime(self):
        for key in self.next2WeeksTemp:
            timeKey = splitDate(key)
            self.averageTempByHour[timeKey] = 0



    """
    Requires: The member dictionaries are correctly filled
    Modifies: averageTempByHour
    Effects: calculates the average for each hour of day and fills the dictionary
    """
    def calcAveragePerHour(self):
        for hourKey in self.averageTempByHour:
            for dateKey in self.next2WeeksTemp:
                #looks through all the days, thus there are multiple instances of the same hour.
                if(splitDate(dateKey) == hourKey):
                    self.averageTempByHour[hourKey] += self.next2WeeksTemp[dateKey]
        for key in self.averageTempByHour:
            #the data is of seven days, which is why to get the average it is divided by 7
            self.averageTempByHour[key] /= 7

    """
    Requires: averageTempByHour is correctly filled
    Modifies: avgTempArray and hourArray
    Effects: fills hourArray using the keys from averageTempByHour and fills avgTempArray using the values from avgTempByHour
    """
    def fillArrays(self):
        for hour in self.averageTempByHour:
            self.hourArray.append(hour)
            self.avgTempArray.append(self.averageTempByHour[hour])

"""
Requires: date is a date string of format YYYY,MM,DD HH:MM
Modifies: nothing
Effects: returns only the HH:MM:SS part of the time as a string
"""
def splitDate(date):
    timeArr = date.split(" ")
    time = timeArr[1]
    return time




"""
Requires: time is a UNIX time as string
Modifies: nothing
Effects: returns the time as YYYY,MM,DD HH:MM
"""
def convertTime(time):
    newTime = datetime.datetime.fromtimestamp(int(time)).strftime('%Y,%m,%d %H:%M')
    return newTime

"""
Requires: ftemp is a string of temperature in Fahrenheit
Modifies: Nothing
Effects: returns ctemp, the temperature in celsius
"""
def tempConverter(ftemp):
    ctemp = (int(ftemp) - 32) * (5/9)
    return ctemp

"""
Requires: Prediction and ApiRequest objects have been created error-free beforehand
Modifies: Nothing
Effects: Creates a csv file with hour,temp (predicted temperature in °C).
"""
def csvOutput(pred,req):
    # using this style for opening guarantees that the file will be closed
    with open("csvPrediction.txt","w") as csvFile:
        csvFile.write("hour,temperature" + "\n")
        for key in pred.averageTempByHour:
            csvFile.write(key + "," + str(pred.averageTempByHour[key]) + "\n")


def main():
    """
    plt setup ahead
    """
    ##############
    # Get current size
    fig_size = plt.rcParams["figure.figsize"]

    # Current size is: [8.0, 6.0]

    fig_size[0] = 18
    fig_size[1] = 15
    #New Size is [18, 15]
    plt.rcParams["figure.figsize"] = fig_size
    #############

    req = ApiRequest()
    req.TESTRounding()

    #print(req.next168Hours)
    pred = Prediction(req)

    chartLabel = "Prediction of hourly temperature for a day"

    xAxis = pred.hourArray
    yAxis = pred.avgTempArray
    plt.title(chartLabel)
    plt.plot(xAxis, yAxis)
    plt.xlabel("Hour", fontsize=14)
    plt.ylabel("Temperature (°C)", fontsize=14)
    plt.savefig("predictionGraph.png")

    #creating the csvFile
    csvOutput(pred, req)


if __name__ == '__main__':
    main()


