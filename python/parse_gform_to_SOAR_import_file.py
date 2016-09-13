#!/usr/bin/env python
'''
 Simple Python app to parse CSV file produced from "Download as' from
 'Pack 2 Family Contact Information (Responses)' sheet, and creates a
 second CSV file that can be used in SOAR to import and create members.

 Usage:
  ./parse_gform_to_SOAR_import_file.py 'Pack 2 Family Contact Information (Responses) - Form Responses 1.csv' 'Pack2-import.csv'

'''
import argparse
import csv
import time

'''
   parse_and_create(gform_fname, SOAR_import_fname)

      gform_fname:        full path of csv file exported from 'Pack 2 Family Contact Information (Responses)' sheet
      SOAR_import_fname:  full path for the import file used by SOAR to create members

   Takes CSV data in gform_fname, parses each line to get family info data as entered by members using the google form,
   and builds another CSV file in the format used by SOAR for member import.
'''
def parse_and_create(gform_fname, SOAR_import_fname):
    new_members = []
    with open(gform_fname, 'r') as f_in:
        reader = csv.reader(f_in)
        for row in reader:
            #print(row)
            new_members.append(row)
    new_members = new_members[1:]

    header = ('Last Name','Suffix','First Name','Middle','Nickname','BSA ID','Den Name','Rank','UserID','Email','Cell Phone','Last Name','Suffix','First Name','Middle','Nickname','BSA ID','UserID','Email','Street','City','State','ZIP','Home Phone','Work Phone','Cell Phone','Last Name','Suffix','First Name','Middle','Nickname','BSA ID','UserID','Email','Street','City','State','Zip','Home Phone','Work Phone','Cell Phone')

    new_entries = []
    update_entries = []
    for m in new_members:
        if m[1] == 'Add' and m[28].find("No") == 0:
            new_entry = []
            new_entry.append(m[16].strip().capitalize())         #     16    :  Scout-Last Name
            new_entry.append('')                                 #     ''    :  Scout-Suffix
            new_entry.append(m[17].strip().capitalize())         #     17    :  Scout-First Name
            new_entry.append('')                                 #     ''    :  Scout-Middle
            new_entry.append('')                                 #     ''    :  Scout-Nickname
            new_entry.append('')                                 #     ''    :  Scout-BSA ID
            new_entry.append('unassigned')                       #     ''    :  Scout-Den Name
            new_entry.append('')                                 #     ''    :  Scout-Rank
            new_entry.append("%s%s1" % (m[17].strip().lower(), m[16].strip().lower()))       #   17+16   :  Scout-UserID
            new_entry.append('')                                 #     ''    :  Scout-Email
            new_entry.append('')                                 #     ''    :  Scout-Cell Phone
            new_entry.append(m[8].strip().capitalize())          #     8     :  Parent1-Last Name
            new_entry.append('')                                 #     ''    :  Parent1-Suffix
            new_entry.append(m[9].strip().capitalize())          #     9     :  Parent1-First Name
            new_entry.append('')                                 #     ''    :  Parent1-Middle
            new_entry.append('')                                 #     ''    :  Parent1-Nickname
            new_entry.append('')                                 #     ''    :  Parent1-BSA ID
            new_entry.append("%s%s1" % (m[9].strip().lower(), m[8].strip().lower()))        #     9+8   :  Parent1-UserID
            new_entry.append(m[11].strip())                      #     11    :  Parent1-Email
            new_entry.append(m[ 2].strip())                      #     2      :  Parent1-Street
            new_entry.append(m[ 4].strip())                      #     4      :  Parent1-City
            new_entry.append("Tx")                               #     5      :  Parent1-State
            new_entry.append(m[ 6].strip())                      #     6      :  Parent1-ZIP
            new_entry.append(m[ 7].strip())                      #     7      :  Parent1-Home Phone
            new_entry.append('')                                 #     ''    :  Parent1-Work Phone
            new_entry.append(m[10].strip())                      #     10    :  Parent1-Cell Phone
            if len(m[12]) > 0:
                new_entry.append(m[12].strip().capitalize())     #     12    :  Parent2-Last Name
                new_entry.append('')                             #     ''    :  Parent2-Suffix
                new_entry.append(m[13].strip().capitalize())     #     13    :  Parent2-First Name
                new_entry.append('')                             #     ''    :  Parent2-Middle
                new_entry.append('')                             #     ''    :  Parent2-Nickname
                new_entry.append('')                             #     ''    :  Parent2-BSA ID
                new_entry.append("%s%s1" % (m[13].strip().lower(), m[12].strip().lower()))       #     13+12 :  Parent2-UserID
                new_entry.append(m[15].strip())                  #     15    :  Parent2-Email
                new_entry.append(m[ 2].strip())                  #     2      :  Parent2-Street
                new_entry.append(m[ 4].strip())                  #     4      :  Parent2-City
                new_entry.append("Tx")                           #     5      :  Parent2-State
                new_entry.append(m[ 6].strip())                  #     6      :  Parent2-Zip
                new_entry.append(m[ 7].strip())                  #     7      :  Parent2-Home Phone
                new_entry.append('')                             #     ''    :  Parent2-Work Phone
                new_entry.append(m[14].strip())                  #     14    :  Parent2-Cell Phone
            else:
                new_entry.append('')                             #     Parent2-Last Name
                new_entry.append('')                             #     Parent2-Suffix
                new_entry.append('')                             #     Parent2-First Name
                new_entry.append('')                             #     Parent2-Middle
                new_entry.append('')                             #     Parent2-Nickname
                new_entry.append('')                             #     Parent2-BSA ID
                new_entry.append('')                             #     Parent2-UserID
                new_entry.append('')                             #     Parent2-Email
                new_entry.append('')                             #     Parent2-Street
                new_entry.append('')                             #     Parent2-City
                new_entry.append('')                             #     Parent2-State
                new_entry.append('')                             #     Parent2-Zip
                new_entry.append('')                             #     Parent2-Home Phone
                new_entry.append('')                             #     Parent2-Work Phone
                new_entry.append('')                             #     Parent2-Cell Phone
            new_entries.append(new_entry)

    print(" --- Found %d new entries: " % (len(new_entries)) )
    for e in new_entries:
       print(e)

    with open(SOAR_import_fname, 'w') as f_out:
        writer = csv.writer(f_out)
        writer.writerow( header )
        writer.writerows(new_entries)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse gform data to create SOAR import file.')
    parser.add_argument("gform_file_path", help='path to the CSV file exported from Google sheet')
    parser.add_argument("SOAR_import_file_path", help='path for the created SOAR import file')
    args = parser.parse_args()

    parse_and_create(args.gform_file_path, args.SOAR_import_file_path)
