
#List of Final Constants used
AUTHOR = "author"
SUBMISSION = "submission"
REVIEW = "review"
AUTHOR_ID = 0
SUBMISSION_ID = 2
REVIEW_ID = 1

#DATE_REGEX = r"(^(0?[1-9]|[12]\d|3[01])[\/](0?[1-9]|1[0-2])[\/](19|20)\d{2}$)"
DATE_REGEX = r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$"
TIME_REGEX = "^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
DATE_AND_TIME_REGEX = r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])\s+([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
#format: yyyy-mm-dd hh-mm