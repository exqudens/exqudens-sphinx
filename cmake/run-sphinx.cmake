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
    cmake_path(GET "CMAKE_CURRENT_LIST_DIR" PARENT_PATH sourceDir)

    set(options)
    set(oneValueKeywords
        "VERBOSE"
        "SSL"
        "BUILD_DIR"
    )
    set(multiValueKeywords
        "PROJECTS"
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

    if("${${currentFunctionName}_BUILD_DIR}" STREQUAL "")
        set(buildDirRelative "build")
    else()
        set(buildDirRelative "${${currentFunctionName}_BUILD_DIR}")
        cmake_path(APPEND buildDirRelative "DIR")
        cmake_path(GET "buildDirRelative" PARENT_PATH buildDirRelative)
    endif()

    if("${${currentFunctionName}_PROJECTS}" STREQUAL "")
        set(projects
            "all"
            "flat-table"
            "numbered-list"
            "traceability"
        )
    else()
        set(projects "${${currentFunctionName}_PROJECTS}")
    endif()

    find_program(SPHINX_BUILD_COMMAND
        NAMES "sphinx-build.exe" "sphinx-build"
        PATHS "${sourceDir}/${buildDirRelative}/py-env/Scripts" "${sourceDir}/${buildDirRelative}/py-env/bin"
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
            WORKING_DIRECTORY "${sourceDir}"
            COMMAND_ECHO "STDOUT"
            COMMAND_ERROR_IS_FATAL "ANY"
        )
        find_program(PIP_COMMAND
            NAMES "pip.exe" "pip"
            PATHS "${sourceDir}/${buildDirRelative}/py-env/Scripts" "${sourceDir}/${buildDirRelative}/py-env/bin"
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
            WORKING_DIRECTORY "${sourceDir}"
            COMMAND_ECHO "STDOUT"
            COMMAND_ERROR_IS_FATAL "ANY"
        )
        find_program(SPHINX_BUILD_COMMAND
            NAMES "sphinx-build.exe" "sphinx-build"
            PATHS "${sourceDir}/${buildDirRelative}/py-env/Scripts" "${sourceDir}/${buildDirRelative}/py-env/bin"
            NO_CACHE
            REQUIRED
            NO_DEFAULT_PATH
        )
    endif()

    foreach(project IN LISTS "projects")
        foreach(builder "html" "docx" "pdf")

            # build
            if("${verbose}")
                message(STATUS "project: '${project}' build ${builder}")
            endif()
            if(EXISTS "${sourceDir}/${buildDirRelative}/doc/${project}/${builder}")
                file(REMOVE_RECURSE "${sourceDir}/${buildDirRelative}/doc/${project}/${builder}")
            endif()
            execute_process(
                COMMAND "${CMAKE_COMMAND}" "-E" "env" "PROJECT=${project}"
                        "${SPHINX_BUILD_COMMAND}" "-E" "-b" "${builder}" "doc" "${buildDirRelative}/doc/${project}/${builder}"
                WORKING_DIRECTORY "${sourceDir}"
                COMMAND_ECHO "STDOUT"
                COMMAND_ERROR_IS_FATAL "ANY"
            )

        endforeach()
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
