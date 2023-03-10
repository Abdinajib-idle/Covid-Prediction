import pandas as pd


# -- cleaning and getting data from covid-19-case-count.csv

def month_to_quarter(month):
    if 1 <= month <= 3:
        return 1
    elif 4 <= month <= 6:
        return 2
    elif 7 <= month <= 9:
        return 3
    else:
        return 4



######################### COVID CASES COUNT #########################
#####################################################################
input_cases = pd.read_csv("inputs/covid-19-case-count.csv")

# remove rows where province name is Canada and Repatriated travellers
updated = input_cases['update'] == 1
cases = input_cases[updated]

cases.rename(columns={"prname": "province"}, inplace=True)
cases['month'] = pd.DatetimeIndex(cases['date']).month
cases['year'] = pd.DatetimeIndex(cases['date']).year
cases['quarter'] = cases.apply(lambda x: month_to_quarter(x.month), axis=1)
cleaned_cases = cases[['date','province', 'quarter', 'year', 'totalcases', 'numdeaths']]
cleaned_cases.sort_values(by=['date','province', 'year', 'quarter'], inplace=True)

#  we can see that the totalcases is accumulative, \
# meaning the total cases of a province is the latest date within the quarter, and also the largest number within a quarter
cleaned_cases['lastdate_in_quarter'] = cleaned_cases.groupby(['province', 'year', 'quarter'])['date'].transform(max)
cleaned_cases = cleaned_cases[cleaned_cases['lastdate_in_quarter'] == cleaned_cases['date']]
cleaned_cases = cleaned_cases.drop(columns=['date', 'lastdate_in_quarter'])
cleaned_cases.sort_values(by=['province', 'year', 'quarter'], inplace=True)



######################### POPULATION COUNT #########################
####################################################################
populationCount = pd.read_csv('./inputs/population_count.csv', parse_dates=['REF_DATE'])
# Filter population table by REF_DATE, GEO and VALUE
populationCount = populationCount.filter(items=['REF_DATE', 'GEO', 'VALUE'])
# Rename GEO to province and VALUE to population
populationCount = populationCount.rename(columns={'GEO': 'province', 'VALUE': 'population'})
# Exclude 'Canada' in province column
populationCount = populationCount[populationCount['province'] != 'Canada']
# Extract only year from REF_DATE column
populationCount['year'] = pd.DatetimeIndex(populationCount['REF_DATE']).year
# Extract only quarter from REF_DATE colum
populationCount['quarter'] = populationCount.REF_DATE.dt.quarter

populationCount['lastdate_in_quarter'] = populationCount.groupby(['province', 'year', 'quarter'])['REF_DATE'].transform(max)
populationCount = populationCount[populationCount['lastdate_in_quarter'] == populationCount['REF_DATE']]
populationCount.sort_values(by=['province', 'year', 'quarter'], inplace=True)

# Remove REF_DATE, lastdate_in_quarter columns
populationCount = populationCount.drop(columns=['REF_DATE', 'lastdate_in_quarter'])


######################### VACCINATION COVERAGE MAP #########################
############################################################################
vaccinationCoverage = pd.read_csv('./inputs/vaccination-coverage-map.csv', parse_dates=['week_end'])
# Change column name to 'week_end' to 'province'
vaccinationCoverage = vaccinationCoverage.rename(
    columns={'prename':'province'})
# Keep columns = [province, quarter, year, numtotal_atleast1dose, numtotal_fully]
vaccinationCoverage = vaccinationCoverage.filter(
    items=['province', 'week_end', 'numtotal_atleast1dose', 'numtotal_fully'])
# Excludes 'Canada' in province column
vaccinationCoverage  = vaccinationCoverage[vaccinationCoverage['province'] != 'Canada']
# Extract year
vaccinationCoverage['year'] = pd.DatetimeIndex(vaccinationCoverage['week_end']).year
# Extract quarters
vaccinationCoverage['quarter'] = vaccinationCoverage.week_end.dt.quarter

vaccinationCoverage['lastdate_in_quarter'] = vaccinationCoverage.groupby(['province', 'year', 'quarter'])['week_end'].transform(max)
vaccinationCoverage = vaccinationCoverage[vaccinationCoverage['lastdate_in_quarter'] == vaccinationCoverage['week_end']]
vaccinationCoverage.sort_values(by=['province', 'year', 'quarter'], inplace=True)

vaccinationCoverage = vaccinationCoverage.drop(columns=['week_end', 'lastdate_in_quarter']).sort_values(by=['province'])


######################### FINAL TABLE #########################
###############################################################
# Join covid cases table with population table by province, year and quarter
final_data = pd.merge(cleaned_cases, populationCount, on=['province', 'year', 'quarter'], how='left')
# Join covid cases, population and vaccination table by province, year and quarter
final_data = pd.merge(final_data, vaccinationCoverage, on=['province', 'year', 'quarter'], how='left')

final_data['vaccination_score_atleast1dose'] = final_data['numtotal_atleast1dose'] / final_data['population']
final_data['vaccination_score_fully'] = final_data['numtotal_fully'] / final_data['population']

final_data.to_csv('inputs/processed-data-numerics.csv')
print(final_data)


