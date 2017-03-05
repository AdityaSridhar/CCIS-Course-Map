from bs4 import BeautifulSoup
from time import sleep
import requests
import re


def get_course_data(level="graduate", department_code="CS"):
    # Get appropriate regex for the provided data.
    """
    Retrieves the information as tuple of the form (course numbers, titles, pre-requisites, description)
    for a given program and department.

    :type level: string (Must be one of "undergraduate", "graduate" or "Any")
    :type department_code: string (Must be one of "CS", "DS", "IS", "GNSD", "HINF", "IA")
    """
    course_code_regex = get_regexp(level, department_code)

    # CCIS Courses Page URL.
    url = "http://www.ccis.northeastern.edu/academics/courses/"

    request_time_out = 5

    # Add user-agent info to headers to identify this bot.
    custom_header = requests.utils.default_headers()
    custom_header.update({'User-Agent': "CourseBot/1.0"})

    # Make GET request and obtain page data.
    r = requests.get(url, headers=custom_header, timeout=request_time_out)

    # Make sure its not an erroneous response.
    r.raise_for_status()

    data = r.text

    # Soup-ify the data to make it easier to parse.
    soup = BeautifulSoup(data, "html.parser")

    # TODO: Build a graph of courses with course numbers as keys and rest of the data as values.
    course_numbers = []
    course_titles = []
    course_descriptions = []
    course_dependencies = []

    # Find all links which match the pattern.
    course_elements = soup.find_all('a', text=course_code_regex)

    # The pre-requisite courses could be undergraduate too, for graduate courses.
    all_courses_code_regex = get_regexp(None, "Any")

    for element in course_elements:
        course_numbers.append(element.text)

        # Ignore the " -" in the beginning.
        course_titles.append(element.next_sibling[3:])

        # Get the course data from the course link.
        course_link = element["href"]
        course_request = requests.get(course_link)
        course_data = course_request.text
        course_soup = BeautifulSoup(course_data, "lxml")

        # Course Description.
        course_description = course_soup.find('td', 'ntdefault')
        course_descriptions.append(course_description.contents[0].strip())

        # The course page contains an italicised prerequisites element.
        pre_req_elem = course_soup.find('i', text=re.compile(r'Prereq.*'))
        dep = []
        if pre_req_elem and pre_req_elem.text:
            # Ignore the "Prereq." in the beginning.
            s1 = pre_req_elem.text[7:]

            """
            * The pattern appears to be (course1,course2, or course3) and (course4, or course5). So split on the "and".
            * The groups remaining after the split are all of the OR type. This works in most cases.
            """
            s2 = s1.split('and')
            for sub in s2:
                matches = re.findall(all_courses_code_regex, sub.strip())
                if matches:
                    dep.append(matches)
        course_dependencies.append(dep)

        # Moment of silence.
        sleep(1)

    # TODO: Need to json-ify the data and return that.
    return course_numbers, course_titles, course_dependencies, course_descriptions


def get_regexp(level="Any", department_code="CS"):
    regexp = "({0}".format(department_code)
    if level == "graduate":
        regexp += " [5-7][0-9]{3}?)"
    elif level == "undergraduate":
        regexp += " [0-4][0-9]{3}?)"
    else:
        # Default to all levels.
        regexp += " [0-9][0-9]{3}?)"

    return re.compile(regexp)


print(get_course_data(level="graduate", department_code="CS"))
