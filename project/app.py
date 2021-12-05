'''
Includes functions that read the config file
and return useful values and that split a
string time input into a useful integer value.
These functions are for use in all other modules
of the package
'''
import json

def read_config_file():
    '''
    Reads the json config file and returns the data in it as a
    dictionary
        Returns:
        config_data (dictionary): A dictionary containing the data in the
        config file
    '''
    with open('config_file.json', 'r', encoding="UTF-8") as config_file:
        config_data=json.load(config_file)
        return config_data

read_config_file()


def split_time(time_input):
    '''
    splits an input into hours and minutes, and then converts the total into seconds
        Parameters:
            time_input (string): The time to be split into hours and minutes and
            converted into seconds. It should have the format HH:MM where H means
            hours and M means minutes
        Returns:
            total (int): The total number of seconds that the time_inpuit has been
            converted into
        '''
    spliter=time_input.split(":")
    hours=int(spliter[0])
    minutes=int(spliter[1])
    total=(hours*60*60)+(minutes*60)
    return total
