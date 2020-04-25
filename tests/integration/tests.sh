#!/usr/bin/env bash

#
# Hacky integration test script.
#
# TODO: Rewrite in Python.
#

set -e


passed=0

for test_scenario in tests/integration/examples/*
do
  cd "$test_scenario"

  set +e
  gadk --print 1> actual.yml 2> errors.log
  set -e

  # Confirm that there are no errors.
  if [[ $(wc -l errors.log) == "0 errors.log" ]]
  then
    echo "No errors in $test_scenario"
  else
    echo "Errors printed for $test_scenario"
    cat errors.log
    passed=1
    cd - > /dev/null
    continue
  fi

  # Confirm that actual.yml is not empty.
  if [[ $(wc -l actual.yml) == "0 actual.yml" ]]
  then
    echo "$test_scenario seems to be WIP!"
    passed=1
    cd - > /dev/null
    continue
  else
    # Confirm that actual.yml matches expected.yml.
    diff expected.yml actual.yml > diff.log
    if [[ $(wc -l diff.log) == "0 diff.log" ]]
    then
      echo "$test_scenario has passed!"
    else
      echo "$test_scenario does not match expected output."
      passed=1
      cd - > /dev/null
      continue
    fi
  fi

  cd - > /dev/null
done

exit $passed
