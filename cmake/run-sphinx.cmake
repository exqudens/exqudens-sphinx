cmake_minimum_required(VERSION 3.25 FATAL_ERROR)

cmake_policy(PUSH)
cmake_policy(SET CMP0007 NEW)
cmake_policy(PUSH)
cmake_policy(SET CMP0010 NEW)
cmake_policy(PUSH)
cmake_policy(SET CMP0012 NEW)
cmake_policy(PUSH)
cmake_policy(SET CMP0054 NEW)
cmake_policy(PUSH)
cmake_policy(SET CMP0057 NEW)

function(execute_script args)
    set(currentFunctionName "${CMAKE_CURRENT_FUNCTION}")
    cmake_path(GET "CMAKE_CURRENT_LIST_DIR" PARENT_PATH projectDir)
    cmake_path(GET "CMAKE_CURRENT_LIST_FILE" STEM currentFileNameNoExt)

    set(options)
    set(oneValueKeywords
        "VERBOSE"
        "SSL"
        "UNDEFINED_REFERENCE"
        "SOURCE_DIR"
        "BUILD_DIR"
    )
    set(multiValueKeywords
        "FILES"
        "BUILDERS"
    )

    cmake_parse_arguments("${currentFunctionName}" "${options}" "${oneValueKeywords}" "${multiValueKeywords}" "${args}")

    if(NOT "${${currentFunctionName}_UNPARSED_ARGUMENTS}" STREQUAL "")
        message(FATAL_ERROR "Unparsed arguments: '${${currentFunctionName}_UNPARSED_ARGUMENTS}'")
    endif()

    if("${${currentFunctionName}_VERBOSE}")
        set(verbose "TRUE")
    else()
        set(verbose "FALSE")
    endif()

    if("${verbose}")
        message(STATUS "execute file: '${CMAKE_CURRENT_LIST_FILE}'")
        string(TIMESTAMP currentDateTime "%Y-%m-%d %H:%M:%S")
        message(STATUS "currentDateTime: '${currentDateTime}'")
    endif()

    if("${${currentFunctionName}_SSL}" STREQUAL "")
        set(ssl "TRUE")
    else()
        if("${${currentFunctionName}_SSL}")
            set(ssl "TRUE")
        else()
            set(ssl "FALSE")
        endif()
    endif()

    if("${${currentFunctionName}_UNDEFINED_REFERENCE}" STREQUAL "")
        set(undefinedReference "FALSE")
    else()
        if("${${currentFunctionName}_UNDEFINED_REFERENCE}")
            set(undefinedReference "TRUE")
        else()
            set(undefinedReference "FALSE")
        endif()
    endif()

    if("${${currentFunctionName}_SOURCE_DIR}" STREQUAL "")
        set(sourceDirRelative "doc")
    else()
        set(sourceDirRelative "${${currentFunctionName}_SOURCE_DIR}")
        cmake_path(APPEND sourceDirRelative "DIR")
        cmake_path(GET "sourceDirRelative" PARENT_PATH sourceDirRelative)
    endif()

    if("${${currentFunctionName}_BUILD_DIR}" STREQUAL "")
        set(buildDirRelative "build")
    else()
        set(buildDirRelative "${${currentFunctionName}_BUILD_DIR}")
        cmake_path(APPEND buildDirRelative "DIR")
        cmake_path(GET "buildDirRelative" PARENT_PATH buildDirRelative)
    endif()

    #[[if("${${currentFunctionName}_START_FILE}" STREQUAL "")
        set(startFile "index")
    else()
        set(startFile "${${currentFunctionName}_START_FILE}")
        cmake_path(APPEND startFile "DIR")
        cmake_path(GET "startFile" PARENT_PATH startFile)
        cmake_path(GET "startFile" PARENT_PATH startDir)
        cmake_path(RELATIVE_PATH "startDir" BASE_DIRECTORY "${sourceDirRelative}" OUTPUT_VARIABLE startDir)
        cmake_path(GET "startFile" STEM startFile)
        if(NOT "${startDir}" STREQUAL "")
            set(startFile "${startDir}/${startFile}")
        endif()
    endif()]]

    if("${${currentFunctionName}_BUILDERS}" STREQUAL "")
        set(builders "html" "docx" "pdf")
    else()
        set(builders "${${currentFunctionName}_BUILDERS}")
    endif()

    if("${${currentFunctionName}_FILES}" STREQUAL "")
        set(files
            "flat-table/index.rst"
            "numbered-list/index.rst"
            "traceability/user-requirements.rst"
            "traceability/system-tests.rst"
            "traceability/matrix.rst"
        )
    else()
        set(files "")
        foreach(file IN LISTS "${currentFunctionName}_FILES")
            cmake_path(GET "file" PARENT_PATH fileDir)
            cmake_path(RELATIVE_PATH "fileDir" BASE_DIRECTORY "${sourceDirRelative}" OUTPUT_VARIABLE fileDir)
            cmake_path(GET "file" FILENAME fileName)
            if("${fileDir}" STREQUAL "")
                list(APPEND files "${fileName}")
            else()
                list(APPEND files "${fileDir}/${fileName}")
            endif()
        endforeach()
    endif()

    find_program(SPHINX_BUILD_COMMAND
        NAMES "sphinx-build.exe" "sphinx-build"
        PATHS "${projectDir}/${buildDirRelative}/py-env/Scripts" "${projectDir}/${buildDirRelative}/py-env/bin"
        NO_CACHE
        NO_DEFAULT_PATH
    )

    # create py-env
    if("${SPHINX_BUILD_COMMAND}" STREQUAL "SPHINX_BUILD_COMMAND-NOTFOUND")
        if("${verbose}")
            message(STATUS "create py-env")
        endif()
        find_program(PYTHON_COMMAND NAMES "py.exe" "py" "python.exe" "python" NO_CACHE REQUIRED)
        execute_process(
            COMMAND "${PYTHON_COMMAND}" "-m" "venv" "${buildDirRelative}/py-env"
            WORKING_DIRECTORY "${projectDir}"
            COMMAND_ECHO "STDOUT"
            COMMAND_ERROR_IS_FATAL "ANY"
        )
        find_program(PIP_COMMAND
            NAMES "pip.exe" "pip"
            PATHS "${projectDir}/${buildDirRelative}/py-env/Scripts" "${projectDir}/${buildDirRelative}/py-env/bin"
            NO_CACHE
            REQUIRED
            NO_DEFAULT_PATH
        )
        set(command "${PIP_COMMAND}" "install")
        if(NOT "${ssl}")
            list(APPEND command "--trusted-host" "pypi.org" "--trusted-host" "pypi.python.org" "--trusted-host" "files.pythonhosted.org" "-r" "requirements.txt")
        endif()
        list(APPEND command "-r" "requirements.txt")
        execute_process(
            COMMAND ${command}
            WORKING_DIRECTORY "${projectDir}"
            COMMAND_ECHO "STDOUT"
            COMMAND_ERROR_IS_FATAL "ANY"
        )
        find_program(SPHINX_BUILD_COMMAND
            NAMES "sphinx-build.exe" "sphinx-build"
            PATHS "${projectDir}/${buildDirRelative}/py-env/Scripts" "${projectDir}/${buildDirRelative}/py-env/bin"
            NO_CACHE
            REQUIRED
            NO_DEFAULT_PATH
        )
    endif()

    # create structure
    if("${verbose}")
        message(STATUS "create structure")
    endif()
    if(EXISTS "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}")
        file(REMOVE_RECURSE "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}")
    endif()
    string(JOIN "\n" indexRstContent
        ".. toctree::"
        "   :maxdepth: 2"
        "   :caption: Contents:"
    )
    string(APPEND indexRstContent "\n" "" "\n")
    foreach(file IN LISTS "files")
        cmake_path(GET "file" PARENT_PATH fileDir)
        cmake_path(GET "file" FILENAME fileName)
        cmake_path(GET "fileName" STEM fileNameNoExt)
        if("${fileDir}" STREQUAL "")
            string(APPEND indexRstContent "   ${fileNameNoExt}" "\n")
        else()
            string(APPEND indexRstContent "   ${fileDir}/${fileNameNoExt}" "\n")
        endif()
    endforeach()
    if("${undefinedReference}")
        string(JOIN "\n" indexRstContent
            "${indexRstContent}"
            ""
            ".. item:: UNDEFINED_REFERENCE Undefined reference."
            ""
        )
    endif()
    file(MAKE_DIRECTORY "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}/${sourceDirRelative}")
    file(WRITE "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}/${sourceDirRelative}/index.rst" "${indexRstContent}")
    foreach(file IN LISTS "files")
        cmake_path(GET "file" PARENT_PATH fileDir)
        if("${fileDir}" STREQUAL "")
            file(COPY "${projectDir}/${sourceDirRelative}/${file}" DESTINATION "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}/${sourceDirRelative}")
        else()
            file(MAKE_DIRECTORY "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}/${sourceDirRelative}/${fileDir}")
            file(COPY "${projectDir}/${sourceDirRelative}/${file}" DESTINATION "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}/${sourceDirRelative}/${fileDir}")
        endif()
    endforeach()
    file(COPY "${projectDir}/${sourceDirRelative}/conf.py" DESTINATION "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}/${sourceDirRelative}")
    file(COPY "${projectDir}/name-version.txt" DESTINATION "${projectDir}/${buildDirRelative}/${currentFileNameNoExt}/${sourceDirRelative}")

    foreach(builder IN LISTS "builders")

        # build
        if("${verbose}")
            message(STATUS "build ${builder}")
        endif()
        if(EXISTS "${projectDir}/${buildDirRelative}/doc/${builder}")
            file(REMOVE_RECURSE "${projectDir}/${buildDirRelative}/doc/${builder}")
        endif()
        execute_process(
            COMMAND "${SPHINX_BUILD_COMMAND}"
                    "-E"
                    "-b"
                    "${builder}"
                    "${buildDirRelative}/${currentFileNameNoExt}/${sourceDirRelative}"
                    "${buildDirRelative}/doc/${builder}"
            WORKING_DIRECTORY "${projectDir}"
            COMMAND_ECHO "STDOUT"
            COMMAND_ERROR_IS_FATAL "ANY"
        )

    endforeach()

    if("${verbose}")
        string(TIMESTAMP currentDateTime "%Y-%m-%d %H:%M:%S")
        message(STATUS "currentDateTime: '${currentDateTime}'")
    endif()
endfunction()

block()
    set(args "")
    set(argsStarted "FALSE")
    math(EXPR argIndexMax "${CMAKE_ARGC} - 1")
    foreach(i RANGE "0" "${argIndexMax}")
        if("${argsStarted}")
            list(APPEND args "${CMAKE_ARGV${i}}")
        elseif(NOT "${argsStarted}" AND "${CMAKE_ARGV${i}}" STREQUAL "--")
            set(argsStarted "TRUE")
        endif()
    endforeach()
    execute_script("${args}")
endblock()

cmake_policy(POP)
cmake_policy(POP)
cmake_policy(POP)
cmake_policy(POP)
cmake_policy(POP)
