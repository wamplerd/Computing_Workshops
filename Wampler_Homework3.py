#! /usr/bin/env python
# 		Program Overview
# Last Modified on Nov 15th
# This is a Python script created to duplicate (and improve upon) the work of a previous Bash script. It is now much faster and more accurate.
# This program is designed to read in VIC 'fluxes' files (in any number) with the requirement they follow the format: fluxes_<lat>.<long>
# This program will output a file for each input file of the data reduced to average precipitation in mm/month for each month. It will place these files in the folder ./monthly_precipitation
# This program will also output a .txt file (Regional_Weighted_Monthly_Average_Precipitation.txt) of average monthly rainfall of all grid cells (with normalized areas) combined for each month. It will place this file in the folder ./
# The format of this .txt file will be a number from 1-12 in the first column representing the month (starting in January), and a number in the second column representing average mm precipitation across all grid cells for that month.

# 		Debugging and Testing
# Edge cases: Leap years and months of incomplete data are accounted for. They will not skew the overall results unduely, although months with very few days of data are prone to skewing if those days are anomolous. Grid cells centered on the equator and poles do not causes issues.
# File writing: If folder ./monthly_precipitation does not exist, it will be created. If files already exist, they will be overwritten without prompt. 
# Results relying on math (such as the area calculation of 0.5x0.5 degree grid cells) were checked against online sources and handheld calculators. Some variance between the calculated grid cell area here versus online calculators, likely due to us assuming the Earth is a perfect sphere. These errors are generally ~2-4%.
# Final results checked against online monthly precipitation estimates for two regions (Southeast and Western Africa). Results are as expected from a winter-storm dominated Southeast Africa and a summer-storm dominated Western Africa.


# 		Assumptions
# This program assumes the flux files are formatted correctly - both their file name and internal data. Extra lines/comments within data files (such as a header) will crash the program.
# flux files with very few entries have the potential to skew overall averages, since the number of entires is not accounted for when comparing between grid cells.
# The Earth is modeled as a perfect sphere in this program.
# Grid cell areas are calculated assuming perfectly 2-dimensional rectangles, with widths/heights based on lat/long at center of the cell.
# Leap years are calculated by year/4 method. Rare exceptions to this are not yet handled (year/100, year/400).
# pi is approximated to 3.14159
# If not every flux file has the same number of months, the final results will be skewed in favor of flux files with more month values.

#		Issues
# 

#=========================  Code below calculates monthly average preciptation for each input file  ==============================

#from calendar import monthrange
import glob
import math
#import matplotlib.pyplot as mplot
import numpy
import os

if not os.path.exists("monthly_precipitation"):
	os.makedirs("monthly_precipitation")

path = '.'

for filename in glob.glob(os.path.join(path, 'fluxes_*')):
	with open(filename) as f:
		if filename[-1] == "~":
			continue
		latlong = filename[9:].split("_")
		currentyear = 0
		MonthlyTotalPrecipitation = [0.0] * 12
		MonthlyTotalDays = [0] * 12
		MonthlyAveragePrecipitation = [[0] for _ in range(12)]
		for line in f:
			columns = line.split()
			#print MonthlyTotalPrecipitation
			#print MonthlyTotalDays
			if int(columns[0]) != currentyear:
				if currentyear == 0:
					currentyear = int(columns[0])
				else:
					currentyear = int(columns[0])
					for n in range(12):
						if n == 0 or n == 2 or n == 4 or n == 6 or n == 7 or n == 9 or n == 11:
							days = 31
						elif n == 1 and currentyear%4 == 0:
							days = 29
						elif n == 1:
							days = 28
						else:
							days = 30

						try:
							MonthlyAveragePrecipitation[n - 1].append(round((MonthlyTotalPrecipitation[n - 1]/MonthlyTotalDays[n - 1]) * days, 4))
						except:
							pass
				MonthlyTotalPrecipitation = [0.0] * 12
				MonthlyTotalDays = [0] * 12

			MonthlyTotalPrecipitation[int(columns[1]) - 1] += float(columns[3])
			MonthlyTotalDays[int(columns[1]) - 1] += 1

		for n in range(12):
			try:
				MonthlyAveragePrecipitation[n - 1].append(round((MonthlyTotalPrecipitation[n - 1]/MonthlyTotalDays[n - 1]) * days, 4))
			except:
				pass

		TotalMonthlyAverage = [[]*1 for _ in range(12)]
		i = 0
		for array in MonthlyAveragePrecipitation:
			totalelements = 0
			for element in array:
				totalelements += element
			TotalMonthlyAverage[i] = totalelements / len(MonthlyAveragePrecipitation[i])
			i += 1

		numpy.savetxt('./monthly_precipitation/monthly_precipitation.' + latlong[0] + "_" + latlong[1], TotalMonthlyAverage, '%2f')


#=====================  Code below calculates a weighted regional precipitation average for each month  ==========================

regionareatotal = 0 #total area of all grid cells analyzed. 
RegionMonthlyWeightedAverage = [0]*12
Months = [[i+1] for i in range(12)]

for i in range(12):
	Months[i] = int(i+1)

for filename in glob.glob(os.path.join(path, './monthly_precipitation/monthly_precipitation.*')):
	if filename[-1] == "~":
		continue # ignores temp files that may be hard to spot
	i = 0

# 40030 = 2 * 3.14159 * 6371 ~= circumference of the planet at equator in kilometers. Following equation assumes perfect sphere.
# Treats length of lat/long through center of cell as length of lat/long of sides of cell
	latlong2 = filename[48:].split("_")
	width = 40030/720 * math.cos(3.14159/180 * abs(float(latlong2[0])))
	height = (40030)/720 # circumference of Earth divided by 360 (to get degrees) divided by 2 (grid cells are 0.5 degrees across)
	cellarea = width * height
	regionareatotal += cellarea

	with open(filename) as f:
		for line in f:

			RegionMonthlyWeightedAverage[i] += (float(line) * cellarea) #regions with more cell area have relative values increased
			i += 1


for i in range(12):
	RegionMonthlyWeightedAverage[i] /= regionareatotal 

# This creates a stacked value list for printing to file conveniently
CodeResult = numpy.column_stack((Months, RegionMonthlyWeightedAverage))

# Months are saved as integers, precipitation averages are saved as floating point numbers to 2 decimals. Columns are seperated by a tab
numpy.savetxt('./Regional_Weighted_Monthly_Average_Precipitation', CodeResult, fmt='%i \t %.2f')

#mplot.plot(RegionMonthlyWeightedAverage)
#mplot.ylabel('Monthly Precipitation (mm)')
#mplot.show()




