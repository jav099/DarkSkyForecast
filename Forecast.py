import matplotlib.pyplot as plt
import datetime
import requests
import json


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
        self.optionalParams = "?exclude=currently,minutely,alerts,flags&extend=hourly"
        self.location = {"latitude": "19.3599300", "longitude": "-99.2938800", "cluster": "Cuajimalpa"}
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
        print(len(data))
        for i in range(168):
            hourData = data[i]
            self.next168Hours[convertTime(hourData["time"])] = tempConverter(hourData["temperature"])



class Prediction():
    """
    Requires: a valid ApiRequest instance
    Modifies: nothing
    Effects: initializes member dictionary with all the keys
    """
    def __init__(self,apiRequest):
        self.next2WeeksTemp = apiRequest.next168Hours
        self.averageTempByHour = {}
        self.fillTime()
        self.calcAveragePerHour()
        self.hourArray = []
        self.avgTempArray = []
        self.fillArrays()


    """
    Requires: nothing
    Modifies: nothing
    Effects: fills the averageTempByHour with all keys (hours) and sets default temp to 0
    """
    def fillTime(self):
        for key in self.next2WeeksTemp:
            timeKey = self.splitDate(key)
            self.averageTempByHour[timeKey] = 0


    """
    Requires: date is a date string of format YYYY,MM,DD HH:MM:SS
    Modifies: nothing
    Effects: returns only the HH:MM:SS part as string
    """
    def splitDate(self,date):
        timeArr = date.split(" ")
        time = timeArr[1]
        return time

    """
    Requires: The member dictionaries are correctly filled
    Modifies: averageTempByHour
    Effects: calculates the average for each hour of day and fills the dictionary
    """
    def calcAveragePerHour(self):
        for hourKey in self.averageTempByHour:
            for dateKey in self.next2WeeksTemp:
                if(self.splitDate(dateKey) == hourKey):
                    self.averageTempByHour[hourKey] += self.next2WeeksTemp[dateKey]
        for key in self.averageTempByHour:
            #the data is of seven days, which is why to get the average it is divided by 7
            print(self.averageTempByHour[key])
            self.averageTempByHour[key] /= 7

    """
    Requires: 
    Modifies:
    Effects:
    """
    def fillArrays(self):
        for hour in self.averageTempByHour:
            self.hourArray.append(hour)
            self.avgTempArray.append(self.averageTempByHour[hour])






"""
Requires: time is a UNIX time as string
Modifies: nothing
Effects: returns the time as YYYY,MM,DD HH:MM:SS
"""
def convertTime(time):
    newTime = datetime.datetime.fromtimestamp(int(time)).strftime('%Y,%m,%d %H:%M:%S')
    return newTime

"""
Requires: ftemp is a string of temperature in Fahrenheit
Modifies: Nothing
Effects: returns ctemp, the temperature in celsius
"""
def tempConverter(ftemp):
    ctemp = (int(ftemp) - 32) * (5/9)
    return ctemp


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
    plt.rcParams["figure.figsize"] = fig_size
    # Get current size
    fig_size = plt.rcParams["figure.figsize"]

    # New Size is: [12, 9]

    #############


    req = ApiRequest()
    print(len(req.next168Hours))
    #print(req.next168Hours)
    pred = Prediction(req)
    print(pred.averageTempByHour)

    chartLabel = "Prediction of hourly temperature for a day"

    xAxis = pred.hourArray
    yAxis = pred.avgTempArray
    plt.title(chartLabel)
    plt.plot(xAxis, yAxis)
    plt.xlabel("Hour", fontsize=14)
    plt.ylabel("Temperature (°C)", fontsize=14)
    plt.savefig("FirstTest.png")





if __name__ == '__main__':
    main()


