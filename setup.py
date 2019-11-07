from setuptools import setup, find_packages
from nose_focus import VERSION

# fmt:off

setup(
      name = "nose_focus"
    , version = VERSION
    , packages = find_packages(include='nose_focus.*', exclude=["tests*"])
    , include_package_data = True

    , python_requires = ">= 3.5"

    , extras_require =
      { "tests":
        [ "nose"
        , "noseOfYeti"
        , "nose-pattern-exclude>=0.1.3"
        ]
      }

     , entry_points =
       { 'nose.plugins':
         [ 'nose_focus = nose_focus.plugin:Plugin'
         ]
       }

    # metadata for upload to PyPI
    , url = "http://nose_focus.readthedocs.org"
    , author = "Stephen Moore"
    , author_email = "stephen@delfick.com"
    , description = "Decorator and plugin to make nose focus on specific tests"
    , long_description = open("README.rst").read()
    , license = "MIT"
    , keywords = "nose tests focus"
    )

# fmt:on
