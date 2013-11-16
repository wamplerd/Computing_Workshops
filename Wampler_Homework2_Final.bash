#! /bin/bash
# 		Program Overview
# Created on October 11th, 2013
# This program is designed to read in VIC 'fluxes' files (in any number) with the requirement they follow the format: fluxes_<lat>.<long>
# This program will output a file for each input file of the data reduced to average precipitation in mm/month for each month. It will place these files in the folder ./monthly_precipitation
# This program will also output a .txt file (CW_Homework_2.txt) of average monthly rainfall of all grid cells (with normalized areas) combined for each month. It will place this file in the folder ./
# The format of this .txt file will be a number from 1-12 in the first column representing the month, and a number in the second column representing average mm/month precipitation across all grid cells.

# 		Debugging and Testing
# Extensive use of print/echo commands was used to check output of each function thorughout the coding. This allowed for errors on any given runthrough to be tracked down easily. It also helped show when variables ended up with values that were problematic.
# Extreme/Edge cases (grid cell centered on equator and poles - February leap year) were checked.
# Months in the flux files that are incomplete do not skew precipitation-per-month .
# Created files were opened and checked, to ensure results are reasonable and the output was formatted correctly.
# Results relying on math (such as the area calculation of 0.5x0.5 degree grid cells) were checked against online sources and handheld calculators.
# Final results were roughly tested against much simpler code (listed below) to ensure results are within range expected.
# awk ' { sum += $4} END {print sum/NR} ' fluxes_*
# The code above gives average precipitation per day, which can be roughly converted to per month, then compared to the output of this program. It should catch agregious flaws.


# 		Assumptions
# This program assumes the flux files are formatted correctly - both their file name and internal data. Extra lines/comments within data files will crash the program.
# flux files with very few entries have the potential to skew overall averages, since the number of entires is not accounted for when comparing between grid cells.
# The Earth is modeled as a perfect sphere in this program.
# Grid cell areas are calculated assuming perfectly 2-dimensional rectangles, with widths/heights based on lat/long at center of the cell.
# 28.25 days in February is assumed to be a reasonable estimate over the timescales involved in these flux files.
# pi is approximated to 3.14159

#		Issues
# This program runs slowly. This is probably because I read in flux files each time for each month. It could be sped up by creating an array of averages for each month, and modifying the variables all at once for each flux file. This would result in 1/12th as many open-file operations.

mkdir -p monthly_precipitation

for file in $( ls fluxes_*); do
	coordinates=$(echo $file | sed ' s/fluxes_//g ')
# This will calculate sum of precipitation per month, then convert units from mm/day to 
	awk ' { sum[$2] += $4} END {
		for ( month in sum )
			if (month%2 == 1)
				printf "%s\t %.4f\n", month, sum[month] / 31;
			else if (month - 2 == 0)
				printf "%s\t %.4f\n", month, sum[month] / 28.25;
			else
				printf "%s\t %.4f\n", month, sum[month] / 30;
			
		} ' $file | sort -n > monthly_precipitation/monthly_precipitation.$coordinates
	done

cd monthly_precipitation
echo -n "" > ../CW_Homework_2.txt

# This loop runs in its entirety once for each month. Not a good design choice.
counter=1
while [  $counter -lt 13 ]; do
	echo -n "Running... " "$counter" " months calculated"
	area=0
	rain=0
	volume=0
	volumetotal=0
	cellarea=0
	cellareatotal=0
	circum=`echo "2*3.14159*6371" | bc`

	for file in $( ls monthly_precipitation.*); do

		lat=$(echo $file | sed -e ' s/monthly_precipitation.// ' -e ' s/-//g ' -e ' s/_[0-9]*\.[0-9]*// ')

		width=$(echo "$circum*c($lat*3.14159/180)/720" | bc -l)
		height=$(echo "$circum/720" | bc -l)
		cellarea=$(echo "$width * $height" | bc -l)

		filereduced=$(head -$counter $file | tail -1 | sed ' s/[0-9] //')

		rain=$(echo $filereduced | sed -e ' s/ /D/ ' -e 's/[0-9]*D// ')
		volume=$(echo "$rain * $cellarea" | bc -l)

		cellareatotal=$(echo "$cellareatotal + $cellarea" | bc -l)
		volumetotal=$(echo "$volume + $volumetotal" | bc -l)

		done

	echo -n -e "$counter" '\t' "$(echo "scale=2; $volumetotal / $cellareatotal" | bc -l)" '\n' >> ../CW_Homework_2.txt
	
	echo -en "\r"	
	let counter=counter+1
	done
cd ..
echo "Complete!! "



