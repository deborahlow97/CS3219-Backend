
#List of Final Constants used
AUTHOR = "author"
SUBMISSION = "submission"
REVIEW = "review"

AUTHOR_CSV = "author.csv"
SUBMISSION_CSV = "submission.csv"
REVIEW_CSV = "review.csv"
AUTHOR_REVIEW = "author.review"
AUTHOR_SUBMISSION = "author.submission"
REVIEW_SUBMISSION = "review.submission"
AUTHOR_REVIEW_SUBMISSION = "author.review.submission"

AUTHOR_HAS_HEADER = "author.HasHeader"
REVIEW_HAS_HEADER = "review.HasHeader"
SUBMISSION_HAS_HEADER = "submission.HasHeader"

AUTHOR_ID = 0
SUBMISSION_ID = 2
REVIEW_ID = 1

REQUEST = "request"
NAME = 'name'
DATE = "date"
TIME = "time"
EMAIL = "email"
FILES = "files"
PASSWORD = "password"

########### ERROR MESSAGES #######################
ERROR =  "error"
INCORRECT_REQUEST_ERROR_MSG = "ERROR: file should have been rejected by frontend already"
REVIEW_OVERALL_EVAL_SCORE_ERROR_MSG  = "Oops! Value Error occurred. There seems to be an error related to the information in review - overall evaluation score. Do make sure that only numbers are accepted as overall evaluation scores."
DATE_FORMAT_ERROR_MSG = "Oops! There seems to be an error related to the information in review - date. Do note that only yyyy-mm-dd format is accepted."
TIME_FORMAT_ERROR_MSG = "Oops! There seems to be an error related to the information in review - time. Do note that only HH:MM format is accepted."
REVIEW_FIELD_NO_ERROR_MSG = "Oops! Value Error occurred. There seems to be an error related to the information in review - field #. Do make sure that only numbers are accepted as field #."
DATE_AND_TIME_ERROR_MSG = "Oops! There seems to be an error related to the information in submission - time submitted or time last updated. Do note that only yyyy-mm-dd HH:MM format is accepted."
ERROR_MSG = "An error has occurred"
#DATE_REGEX = r"(^(0?[1-9]|[12]\d|3[01])[\/](0?[1-9]|1[0-2])[\/](19|20)\d{2}$)"
DATE_REGEX = r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$"
TIME_REGEX = "^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
DATE_AND_TIME_REGEX = r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])\s+([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
#format: yyyy-mm-dd hh:mm