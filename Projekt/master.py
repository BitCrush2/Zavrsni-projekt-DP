import os
import arxiv
import doaj
import hrcak
import json_convert
import pdf_tessar
import pypaper
import scholar
import unstructured_process

if __name__ == '__main__':
    i = 0
    while i == 0:
        print("Which site do you want to scrape?: 1.Arxiv 2.Hrcak 3.Directory_of_open_access_journals 4.Scholar")
        site = int(input("Input number: "))

        if site == 1:
            arxiv.main()  # Assume arxiv.py has a main() function
        elif site == 2:
            hrcak.main()  # Assume hrcak.py has a main() function
        elif site == 3:
            doaj.main()  # Assume doaj.py has a main() function
        elif site == 4:
            print("Do you want to use 1.pypaper or the 2.scholarly package?")
            choice = int(input("Input number: "))
            if choice == 1:
                pypaper.main()  # Assume pypaper.py has a main() function
            elif choice == 2:
                scholar.main()  # Assume scholar.py has a main() function

        proces = input("Would you like to use the unstructured library to process the papers y/n? ")
        if proces == "y":
            unstructured_process.main()  # Assume unstructured_process.py has a main()
        elif proces == "n":
            pdf_tessar.main()  # Assume pdf_tessar.py has a main()

        transforms = input("Would you like to transform the papers into json y/n? ")
        if transforms == "y":
            json_convert.main()  # Assume json_convert.py has a main()

        exit_prog = input("Would you like to exit the program y/n? ")
        if exit_prog == "y":
            break
        elif exit_prog == "n":
            continue