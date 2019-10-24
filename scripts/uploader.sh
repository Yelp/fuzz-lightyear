#!/bin/bash
# This script pretty much just follows the instructions from
# https://packaging.python.org/tutorials/packaging-projects/
# and uploads this package to pypi.

MODULE_NAME='fuzz_lightyear'

function usage() {
    echo "Usage: uploader.sh [test|main]"
    echo "Specify the pypi instance you want to upload to."
    echo "  - test:   uploads to test.pypi.org"
    echo "  - main:   uploads to pypi.org"
}

function main() {
    local mode="$1"
    if [[ -z "$mode" ]]; then
        usage
        return 0
    fi
    if [[ "$mode" != "main" ]] && [[ "$mode" != "test" ]]; then
        usage
        return 1
    fi

    gitTagVersion "$mode"
    if [[ "$?" != 0 ]]; then
        return 1
    fi

    # Install dependencies
    pip install setuptools wheel twine

    # Create distribution files
    python setup.py sdist bdist_wheel

    uploadToPyPI "$mode"
    testUpload "$mode"
    if [[ $? == 0 ]]; then
        echo "Success!"
        rm -r build/ dist/
    fi
}

function gitTagVersion() {
    # Usage: gitTagVersion <mode>
    # This tags the latest upload with the latest version.
    local mode="$1"

    local version
    version=`python -m $MODULE_NAME --version`
    if [[ "$?" != 0 ]]; then
        echo "Unable to get version information."
        return 1
    fi

    local extraArgs=""
    if [[ "$mode" == "test" ]]; then
        extraArgs="--index-url https://test.pypi.org/simple/"
    fi

    # Check pip for existing version
    local buffer
    buffer=$((pip install $extraArgs $MODULE_NAME==no_version_found) 2>&1)
    buffer=`echo "$buffer" | grep "$version"`
    if [[ "$?" == 0 ]]; then
        echo "error: Version already exists in PyPI."
        return 1
    fi

    # Ignore output
    buffer=`git tag --list | grep "^v$version$"`
    if [[ "$?" != 0 ]]; then
        # We combine both staged and unstaged files in this check.
        buffer=`echo "$(git diff --name-only)$(git diff --name-only --staged)" | tr -d '\n' | wc -c | tr -d ' '`
        if [[ "$buffer" > 0 ]]; then
            echo "warning: Are you sure you want to tag the current version?"
            echo "warning: There are still changes that are not tracked!"
            echo "warning: If you want to continue, stash your changes, then try again."
        else
            git tag "v$version" && git push origin --tags
        fi
    fi
}

function uploadToPyPI() {
    # Usage: uploadToPyPI <mode>
    local mode="$1"
    if [[ "$mode" == "main" ]]; then
        twine upload dist/*
    else
        twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    fi
}

function testUpload() {
    # Usage: testUpload <mode>
    local mode="$1"

    installFromPyPI "$mode"

    `underscoreToHyphen $MODULE_NAME` --version
    if [[ $? != 0 ]]; then
        echo "Failed installation!"
        return 1
    fi
}

function installFromPyPI() {
    # Usage: installFromPyPI <mode>
    local mode="$1"
    local name=`underscoreToHyphen $MODULE_NAME`
    if [[ "$mode" == "main" ]]; then
        pip install $name
    else
        pip install --index-url https://test.pypi.org/simple/ $name
    fi
}

function underscoreToHyphen() {
    # Usage: underscoreToHyphen <string>
    echo "$1" | tr '_' '-'
}

main "$@"
