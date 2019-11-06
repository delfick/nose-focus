from setuptools import setup, find_packages

setup(
      name = "nose_focus"
    , version = "0.1.4"
    , packages = find_packages(include='nose_focus.*', exclude=["tests*"])
    , include_package_data = True

    , install_requires =
      [ 'six'
      ]

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
    , license = "WTFPL"
    , keywords = "nose tests focus"
    )
