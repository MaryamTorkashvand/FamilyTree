# parsing GEDCOM files and making csv files with certain columns
# Author= Maryam Torkashvand

import os
import csv
import time
import zipfile
import ged4py  # written based on C and probably is faster that GEDCOM library


def gedcom_to_csv(zippedfiles_dir, output_dir, chunk_size):
    '''
    This function gets directory of zipped GEDCOM files
    and returns CSV files for each file.
    :param zippedfiles_dir: input files path
            output_dir: output files path
            chunk_size: Intiger, the number of rows that we want to save in the row list
    :return: None (write csv files to the output directory)
                        To save memory, we can store the rows in chunks and then write each chunk into the csv file.
                        This way the writing process will be faster while there is no need of huge memory usage to store the data.
                        as the Chunk size can be changed, we add it to the function parameter.
    '''

    for zip_filename in os.listdir(zippedfiles_dir):
        if not zip_filename.endswith(".zip"):
            continue

        zip_path = os.path.join(zippedfiles_dir, zip_filename)

        with (zipfile.ZipFile(zip_path) as zip_archive):

            for gedcom_name in zip_archive.namelist():
                if not gedcom_name.endswith(".ged"):
                    continue

                with zip_archive.open(gedcom_name) as gedcom_file:
                    gedcom_reader = ged4py.parser.GedcomReader(gedcom_file)

                    csv_filename = gedcom_name.replace(".ged", ".csv")
                    csv_path = os.path.join(output_dir, csv_filename)

                    with open(csv_path, 'w', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(["Index", "GEDid", "Name", "Gender", "Father_name", "Mother_name", "Birth Year", "Birth Place"]) #Header

                        #initiate a list that collect rows up to chunk_size
                        all_rows = []

                        # indexing the records
                        for index, person in enumerate(gedcom_reader.records0("INDI"), start=1):
                            # we want to write individuals name, Fname, Mname, bdate, bplace, id, gender
                            # using tags first extract the variables
                            # .format() method in ged4py format the names from last/first to first last name

                            name = person.name.format() if person.name else ''

                            birth_record = person.sub_tag("BIRT")
                            if birth_record:
                                birth_date = birth_record.sub_tag("DATE")
                                birth_year = str(birth_date.value).split()[-1] if birth_date else ''
                            else:
                                birth_year = ''

                            birth_place = birth_record.sub_tag("PLAC").value if birth_record and birth_record.sub_tag("PLAC") else ''

                            father_name = person.father.name.format() if person.father else ''
                            mother_name = person.mother.name.format() if person.mother else ''

                            gender = person.sub_tag("SEX").value if person.sub_tag("SEX") else ''

                            all_rows.append(
                                [index, person.xref_id, name, gender, father_name, mother_name, birth_year, birth_place]
                            )
                            #when all_rows fill with the same number of rows as chink_size, write the chunk to the csv and clear the chunk
                            if len(all_rows) == chunk_size:
                                writer.writerows(all_rows)
                                all_rows.clear()

                        #if a file has less than chunk size rows, and also for remaining data of other files that cannot make up a full chunk, write everything in all-rows after the loop
                        if all_rows:
                            writer.writerows(all_rows)


#Test with two GEDCOM files
zippedfiles_dir = "/Users/maryamtorkashvand/Desktop/gedcomziped"
output_dir = "/Users/maryamtorkashvand/Desktop/csvs"
start_time = time.time()
gedcom_to_csv(zippedfiles_dir, output_dir, 10000)
process_time = time.time() - start_time
print (f"Time of process: {process_time: .2f} second")
